from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, date
from json import dumps
import os
import re

def get_when_visible(driver, locator, timeout=30):
    '''Waits until a web element is be visible, then returns it.

    Parameters:
        driver (webdriver) - the webdriver that's being used
        locator (locator) - the webelement locator object
        timeout (int) - seconds to wait before timeout (default 60)
    Returns:
        The web element found using the locator
    Raises:
        TimeoutException - when no element is found before timeout
    '''
    return wait(driver, timeout).until(EC.visibility_of_element_located(locator))

def get_date(top_elem, css_selector):
    '''Finds the date from an HTML element

    Parameters:
        top_elem (webelement) - the element that represents the entire interaction
        css_selector (str) - css selector pointing to the element with the date
    Returns:
        string representation of the date in ISO format
    '''
    date_elem = top_elem.find_element_by_css_selector(css_selector)
    date_search = re.search('([A-Za-z]{3} \d?\d)(?:, )?(\d{4})?', date_elem.text)
    # if the date was found, return it
    if date_search:
        # if the date doesn't specify a year, assume the current year
        year = (date_search.group(2) if date_search.group(2) else str(date.today().year))
        return str(datetime.strptime(date_search.group(1) + ' ' + year, '%b %d %Y').date())
    # if the date wasn't found, check if the text describes a time of day
    elif re.search('([0-2]?\d:[0-5]\d [apAP][mM])', date_elem.text):
        # if it does, return today
        return date.today().isoformat();

def get_contacts(top_elem):
    '''Collects all of the contacts found in a "other contacts" popup

    Parameters:
        top_elem (webelement) - the parent of the contact elements
    Returns:
        a dictionary of all contacts found in the popup
    '''
    contact_list = {}
    # find the contacts who have ids
    for link in top_elem.find_elements_by_tag_name('a'):
        if link.get_attribute('class') == 'contact':
            contact_list[link.text.encode('utf8')] = link.get_attribute('href').encode('utf8')
        # if this is an "X others" link, add contacts from the popup it opens
        elif link.get_attribute('class') == 'gwt-Anchor':
            link.click()
            popup_elem = browser.find_element_by_css_selector('body > div.nmbl-PopupWindow')
            contact_list.update(get_contacts(popup_elem))
            top_elem.find_element_by_css_selector('span.last').click()
    # find the contacts who don't have ids
    for span in top_elem.find_elements_by_css_selector('span.notMatched'):
        contact_list[span.text.encode('utf8')] = 'notMatched'
    return contact_list

# get information from environment variables
email = os.environ['NIMBLE_EMAIL']
password = os.environ['NIMBLE_PASSWORD']
path_to_chromedriver = os.environ['PATH_TO_CHROMEDRIVER']

# open a new chrome web driver and go to nimble.com
browser = webdriver.Chrome(executable_path = path_to_chromedriver)
url = "https://nginx.nimble.com/#app/contacts/view?id=5581fe938e08ab59fe6dd915"
browser.get(url)

# find the login form elements, fill in the form, and then submit it
login_form_email = get_when_visible(browser, (By.ID, 'login-f_email'))
login_form_password = get_when_visible(browser, (By.ID, 'login-f_password'))
login_form_email.send_keys(email)
login_form_password.send_keys(password)
login_form_password.submit()

# navigate to the interaction list
get_when_visible(browser, (By.LINK_TEXT, "Pending & History")).click()
get_when_visible(browser, (By.LINK_TEXT, "Show more >>")).click()

# find the element that's displayed when the list is expanding
busy_view = browser.find_element_by_class_name("busyView")

submit_list = []

# TODO: find most recent interaction
table = browser.find_element_by_class_name('ContactEntitiesTable')

# TODO: break when freshly loaded interactions are too old
# TODO: loop until the last interaction read is already in database
read_count = 0
while read_count < 100:
    # when the expandable interaction list isn't expanding
    if busy_view.is_displayed() is False:
        # scroll to the bottom of the page to expand it
        browser.execute_script("scroll(0, document.body.scrollHeight)")
        # read new interactions that have showed up as a result of scrolling
        currently_open = len(table.find_elements_by_tag_name('tr'))
        while read_count < currently_open:
            # focus on the next unread element in the interaction list
            read_count = read_count + 1
            elem = table.find_element_by_xpath('.//tr[%d]/td/div' % read_count)
            data = {}

            # finds the interaction's type
            class_name = elem.get_attribute('class')
            type_search = re.search('(.+)ContactWidget ?(.*)', class_name)
            if type_search.group(1): data['type'] = type_search.group(1).encode('utf8')
            else: data['type'] = class_name

            if type_search.group(2): data['subtype'] = type_search.group(2).encode('utf8')

            # adds the interaction's date to the 'data' dictionary
            if   data['type'] == 'Event':   data['date'] = get_date(elem, '.created')
            elif data['type'] == 'Twitter': data['date'] = get_date(elem, '.details div:last-of-type')
            elif data['type'] == 'Email':   data['date'] = get_date(elem, '.details div:last-of-type')
            else:
                # logs interactions that the program wasn't prepared to handle
                with open('unrecognized_types.log', 'a') as f:
                    f.write(class_name + ':\t')
                    f.write(elem.get_attribute('innerHTML') + '\n')

            # adds the interaction's subject to the 'data' dictionary
            try: data['subject'] = elem.find_element_by_css_selector('.subject').text.encode('utf8')
            except NoSuchElementException: data['subject'] = '(no subject)'

            # adds the interaction's sender to the 'data' dictionary (if relevant)
            try:
                sender_elem = elem.find_element_by_css_selector('.details div.gwt-HTML *')
                name = sender_elem.text
                url = sender_elem.get_attribute('href') if sender_elem.tag_name is 'a' else 'notMatched'
                data['sender'] = { name.encode('utf8') : url.encode('utf8') }
            except NoSuchElementException:
                pass

            # adds the contacts who were involved in the interaction
            contacts_elem = elem.find_element_by_css_selector('.ExpandedMoreContactsListWidget')
            contacts = get_contacts(contacts_elem)
            if contacts: data['contacts'] = contacts

            # append this dictionary to the neo4j submit list
            submit_list.append(data)

# displays the data in json format
print dumps(submit_list, indent=4)


# TODO: submit submit_list to neo4j somehow


#~ def get_data(urls):
#~ # given a list of urls
    #~ for url in urls
        #~ dirty_data = get_data(url)
        #~ clean_data = cleaner(dirty_data)
        #~ send data to graph database
