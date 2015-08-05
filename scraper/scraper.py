from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, date
from pprint import pprint

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

# open a new chrome web driver
path_to_chromedriver = os.environ['PATH_TO_CHROMEDRIVER']
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

# go to nimble.com
url = "https://nginx.nimble.com/#app/contacts/view?id=5581fe938e08ab59fe6dd915"
browser.get(url)

# get login information from config variables
email = os.environ['NIMBLE_EMAIL']
password = os.environ['NIMBLE_PASSWORD']

# find the login form elements
login_form_email = get_when_visible(browser, (By.ID, 'login-f_email'))
login_form_password = get_when_visible(browser, (By.ID, 'login-f_password'))

# fill in the login form and submit it
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
            read_count = read_count + 1

            # focus on the 'read_count'th element in the interaction list
            elem = table.find_element_by_xpath('.//tr[%d]/td/div' % read_count)

            data = {}

            # finds the interaction's type
            class_name =
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
                    f.write(element.get_attribute('innerHTML') + '\n')

            # adds the interaction's subject to the 'data' dictionary
            try: data['subject'] = elem.find_element_by_css_selector('.subject').text.encode('utf8')
            except NoSuchElementException: data['subject'] = '(no subject)'

            # TODO: add data['participants'][]
            pprint(data, width=10)
            print

            # append this dictionary to the neo4j submit list
            submit_list.append(data)

# TODO: submit submit_list to neo4j somehow

#~ new_scraped_interactions = {}
#~ interaction_table = browser.find_element_by_class_name("topWidget").find_elements_by_class_name()
#~ interaction = browser.find_element_by_class_name("topWidget")
#~ interaction_between = interaction.find_elements_by_class_name("contact")
#~ interaction_type = interaction.find

#~ interaction_participants = []
#~ for contact in interaction_between:
  #~ interaction_participants.append(str(contact.text))
#~ new_scraped_interactions["interaction_participants"] = interaction_participants

#~ # print new_scraped_interactions
#~ # scrape most recent interaction element
#~ # grab the most recent interaction data from the db
#~ if scraped element != most recent element
    #~ #top
#~ new_scraped_interactions.push(scraped_elements)
#~ # scroll down the page
#~ # scrape all interaction elements

#~ def get_data(url):
#~
#~
#~ # given a list of urls
    #~ for url in urls
        #~ dirty_data = get_data(url)
        #~ clean_data = cleaner(dirty_data)
        #~ send data to graph database
