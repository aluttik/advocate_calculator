from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, date
from dateutil.parser import parse
from json import dumps
import os
import re

# open a new chromedriver window
path_to_chromedriver = os.environ['PATH_TO_CHROMEDRIVER']
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

_date_selectors = {
    'Event': '.created',
    'Email': '.details div:last-of-type',
    'Twitter': '.details div:last-of-type'
}

def get_date_selector(the_type):
    '''finds the css selector that corresponds to an interaction's type'''
    keys = [key for key in _date_selectors.keys() if the_type.startswith(key)]
    try: return _date_selectors[keys[0]]
    except IndexError: raise KeyError

def log_unrecognized_type(top_elem):
    '''logs interactions that the program wasn't prepared to handle'''
    with open('unrecognized_types.log', 'a') as f:
        f.write(top_elem.get_attribute('class') + '\t')
        f.write(top_elem.get_attribute('innerHTML') + '\n')

def get_element(locator, driver=browser, timeout=30):
    '''Waits until a web element is be visible, then returns it.

    Parameters:
        driver (webdriver) - the webdriver to look in (default=browser)
        locator (locator) - the webelement locator object
        timeout (int) - seconds to wait before timeout (default=60)
    Returns:
        The web element found using the locator
    Raises:
        TimeoutException - when no element is found before timeout
    '''
    _is_visible = EC.visibility_of_element_located
    return wait(driver, timeout).until(_is_visible(locator))

def get_type(top_elem):
    '''finds an interaction's type'''
    class_name = top_elem.get_attribute('class').encode('utf8')
    class_name = class_name.split(' hovered')[0]
    return re.sub('(.+)ContactWidget( ?.*)', r'\1\2', class_name)

def get_date(date_elem):
    '''Finds the date from an HTML element

    Parameters:
        date_elem (webelement) - contains the a date
    Returns:
        string representation of the date in ISO format
    '''
    date_string = date_elem.text.split('-')[0]
    return parse(date_string, fuzzy=True).date().isoformat()

def get_sender(sender_elem):
    '''finds an interaction's sender'''
    name = sender_elem.text.encode('utf8')
    if sender_elem.tag_name is 'a':
        return { name : sender_elem.attribute('href').encode('utf8') }
    else:
        return { name : 'notMatched' }

def get_popup_element():
    '''waits for a popup window to appear, then returns it'''
    return browser.get_element((By.CSS_SELECTOR, 'div.nmbl-PopupWindow'))

def get_contacts(contacts_elem):
    '''finds all of the interaction's contacts

    Parameters:
        contacts_elem (webelement) - the parent of the contact elements
    Returns:
        a dictionary of all contacts found in the popup
    '''
    contacts = {}
    # find the contacts who have ids
    for link in contacts_elem.find_elements_by_tag_name('a'):
        if link.get_attribute('class') == 'contact':
            contacts[link.text.encode('utf8')] = link.get_attribute('href').encode('utf8')
        # if this is an "X others" link, open the popup and add its contacts
        elif link.get_attribute('class') == 'gwt-Anchor':
            link.click()
            contacts.update(get_contacts(get_popup_element()))
            contacts_elem.find_element_by_css_selector('span.last').click()
    # find the contacts who don't have ids
    for span in contacts_elem.find_elements_by_css_selector('span.notMatched'):
        contacts[span.text.encode('utf8')] = 'notMatched'
    else: return contacts

# go to nimble.com
url = "https://nginx.nimble.com/#app/contacts/view?id=5581fe938e08ab59fe6dd915"
browser.get(url)

# get information from environment variables
email = os.environ['NIMBLE_EMAIL']
password = os.environ['NIMBLE_PASSWORD']

# find the login form elements, fill in the form, and then submit it
login_form_email = get_element((By.ID, 'login-f_email'))
login_form_password = get_element((By.ID, 'login-f_password'))
login_form_email.send_keys(email)
login_form_password.send_keys(password)
login_form_password.submit()

# navigate to the interaction list
get_element((By.LINK_TEXT, "Pending & History")).click()
get_element((By.LINK_TEXT, "Show more >>")).click()

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
            data = {}

            elem = table.find_element_by_xpath('.//tr[%d]/td/div' % read_count)
            data['type'] = get_type(elem)

            try:
                # adds the interaction's date to the 'data' dictionary
                selector = get_date_selector(data['type'])
                date_elem = elem.find_element_by_css_selector(selector)
                data['date'] = get_date(date_elem)
            except KeyError:
                log_unrecognized_type(elem)
                continue

            try:
                # adds the interaction's subject to the 'data' dictionary
                data['subject'] = elem.find_element_by_css_selector('.subject').text.encode('utf8')
            except NoSuchElementException:
                data['subject'] = '(no subject)'

            try:
                # adds the interaction's sender to the 'data' dictionary
                sender_elem = elem.find_element_by_css_selector('.details div.gwt-HTML *:only-child')
                data['sender'] = get_sender(sender_elem)

                # adds the contacts who were involved in the interaction
                contacts_elem = elem.find_element_by_css_selector('.ExpandedMoreContactsListWidget')
                contacts = get_contacts(contacts_elem)
                if contacts: data['contacts'] = contacts
            except NoSuchElementException:
                pass


            # append this dictionary to the neo4j submit list
            submit_list.append(data)

# displays the data in json format
print dumps(submit_list, indent=4)

#~ browser.close()

# TODO: submit submit_list to neo4j somehow


#~ def get_data(urls):
#~ # given a list of urls
    #~ for url in urls
        #~ dirty_data = get_data(url)
        #~ clean_data = cleaner(dirty_data)
        #~ send data to graph database
