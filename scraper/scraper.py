from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, date
import json
import os
import re

def click_link(driver, text, timeout=60):
    '''Waits for a hyperlink to be clickable, then clicks it.

    Parameters:
        driver (webdriver) - the webdriver that's being used
        text (str) - the text of the link to click on
        timeout (int) - seconds to wait before timeout (default 60)
    Returns:
        None
    Raises:
        TimeoutException - when no element is found before timeout
    '''
    wait = WebDriverWait(driver, timeout)
    locator = (By.LINK_TEXT, text)
    link = wait.until(EC.element_to_be_clickable(locator))
    link.click()

def get_when_visible(driver, locator, timeout=60):
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
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.visibility_of_element_located(locator))
    return element

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

def get_other_contacts(interaction_element, popup_link):
    '''Collects all of the contacts found in a "other contacts" popup

    Parameters:
        interaction_element (webelement) - the interaction that's being processed
        popup_link (webelement) - a link to an "other contacts" popup
    Returns:
        a dictionary of all contacts found in the popup
    '''
    others = {}

    # open and find the popup element
    click_link(interaction_element, popup_link.text)
    popup_element = browser.find_element_by_css_selector('body > div.nmbl-PopupWindow')

    # find the contacts who have ids
    for link in popup_element.find_elements_by_css_selector('div.content div a.contact'):
        url = link.get_attribute('href').encode('utf8')
        link_search = re.search('^https?://.+?\.nimble.com(.*)$', url)
        others[link.text.encode('utf8')] = link_search.group(1)

    # find the contacts who don't have ids
    for span in popup_element.find_elements_by_css_selector('div.content div span.notMatched'):
        others[span.text.encode('utf8')] = 'notMatched'

    # close the popup element
    interaction_element.find_element_by_css_selector('span.last').click()

    return others

# open a new chrome web driver and go to nimble.com
path_to_chromedriver = os.environ['PATH_TO_CHROMEDRIVER']
browser = webdriver.Chrome(executable_path = path_to_chromedriver)
url = "https://nginx.nimble.com/#app/contacts/view?id=5581fe938e08ab59fe6dd915"
browser.get(url)

# get login information from config variables
email = os.environ['NIMBLE_EMAIL']
password = os.environ['NIMBLE_PASSWORD']

# find the login form elements, fill in the form, and then submit it
login_form_email = get_when_visible(browser, (By.ID, 'login-f_email'))
login_form_password = get_when_visible(browser, (By.ID, 'login-f_password'))
login_form_email.send_keys(email)
login_form_password.send_keys(password)
login_form_password.submit()

# navigate to the interaction list
click_link(browser, "Pending & History")
click_link(browser, "Show more >>")

# find the element that's displayed when the list is expanding
busy_view = browser.find_element_by_class_name("busyView");

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

        # read new interactions that have shown up as a result of scrolling
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


            # adds the interaction's subject to the 'data' dictionary
            try: data['sender'] = elem.find_element_by_css_selector('.details div.gwt-HTML *').text.encode('utf8')
            except NoSuchElementException: pass


            # adds the contacts who were involved in the interaction
            contacts = {}
            contacts_element = elem.find_element_by_css_selector('div.ExpandedMoreContactsListWidget')

            # first find all contacts who have associated urls
            for link in contacts_element.find_elements_by_tag_name('a'):

                # if the link is a contact, add it to the contacts dict
                if link.get_attribute('class') == 'contact':
                    url = link.get_attribute('href').encode('utf8')
                    link_search = re.search('^https?://.+?\.nimble.com(.*)$', url)
                    contacts[link.text.encode('utf8')] = link_search.group(1)

                # if there is an "X others" link, grab contacts from that too
                elif link.get_attribute('class') == 'gwt-Anchor':
                    contacts.update(get_other_contacts(elem, link))

            # then find all contacts who don't have associated urls
            for span in contacts_element.find_elements_by_css_selector('span.notMatched'):
                contacts[span.text.encode('utf8')] = 'notMatched'

            if contacts: data['contacts'] = contacts


            # append this dictionary to the neo4j submit list
            submit_list.append(data)


# displays the data in json format
print json.dumps(submit_list, indent=4)


# TODO: submit submit_list to neo4j somehow


#~ def get_data(urls):
#~ # given a list of urls
    #~ for url in urls
        #~ dirty_data = get_data(url)
        #~ clean_data = cleaner(dirty_data)
        #~ send data to graph database
