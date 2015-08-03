from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from NimbleInteraction import NimbleInteraction, NimbleInteractionUnkownType
from datetime import datetime
import os

def click_link(driver, text, timeout=60):
    """
    Waits for a hyperlink to be clickable, then clicks it.

    Parameters:
        driver (webdriver): the webdriver that's being used
        text (str): the text of the link to click on
        timeout (int): seconds to wait before timeout (default 60)

    Returns:
        None

    Raises:
        TimeoutException - when no element is found before timeout
    """
    wait = WebDriverWait(driver, timeout)
    locator = (By.LINK_TEXT, text)
    link = wait.until(EC.element_to_be_clickable(locator))
    link.click()

def get_when_visible(driver, locator, timeout=60):
    """
    Waits until a web element is be visible, then returns it.

    Parameters:
        driver  - the webdriver that's being used
        locator - the webelement locator object
        timeout - seconds to wait before timeout (default 60)

    Returns:
        The web element found using the locator

    Raises:
        TimeoutException - when no element is found before timeout
    """
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.visibility_of_element_located(locator))
    return element

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

# when the list is ready to expand, expand it
# TODO: read the incoming interactions into objects
# TODO: send those interaction objects to the graph database
# TODO: loop until the last interaction read is already in database
# TODO: break when freshly loaded interactions are too old
i = 0
table = browser.find_element_by_class_name('ContactEntitiesTable')
while i < 100:
    if busy_view.is_displayed() is False:
        print '--------------'
        browser.execute_script("scroll(0, document.body.scrollHeight)")
        open_count = len(table.find_elements_by_tag_name('tr'))
        while i < open_count:
            i = i + 1
            interaction_element = table.find_element_by_xpath(".//tr["+str(i)+"]/td/div")
            try:
                interaction = NimbleInteraction(interaction_element)
                print interaction.date, '|', interaction.type, '|',
                print '"' + interaction.subject + '"'
            except NimbleInteractionUnknownType as exception:
                print exception


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
