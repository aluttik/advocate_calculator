from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


def click_link(driver, text, timeout=60):
    '''
    description:
        waits for a hyperlink to be clickable, then clicks it

    input:
        (webdriver) driver =  the web driver that's being used 
        (string) text = the text of the link to click on
        (int) timeout = seconds to wait before timing out (optional)

    output:
        None
    '''
	wait = WebDriverWait(driver, timeout)
	wait.until(EC.element_to_be_clickable(
		(By.LINK_TEXT, text)
	)).click()

#open a new chrome web driver
path_to_chromedriver = os.environ['PATH_TO_CHROMEDRIVER']
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

#go to nimble.com
url = "https://nginx.nimble.com/#app/contacts/view?id=5581fe938e08ab59fe6dd915"
browser.get(url)

#wait for elements to appear
browser.implicitly_wait(3)

#find the elements by ID
login_form_email = browser.find_element_by_id('login-f_email')
login_form_password = browser.find_element_by_id('login-f_password')

#get login information from config variables
email = os.environ['NIMBLE_EMAIL']
password = os.environ['NIMBLE_PASSWORD']

#fill in login form and submit
login_form_email.send_keys(email)
login_form_password.send_keys(password)
login_form_password.submit()

#navigate to interaction list
click_link(browser, "Pending & History")
click_link(browser, "Show more >>")


#new_scraped_interactions = {}
#interaction_table = browser.find_element_by_class_name("topWidget").find_elements_by_class_name()
#interaction = browser.find_element_by_class_name("topWidget")
#interaction_between = interaction.find_elements_by_class_name("contact")
#interaction_type = interaction.find

#interaction_participants = []
#for contact in interaction_between:
#    interaction_participants.append(str(contact.text))
#new_scraped_interactions["interaction_participants"] = interaction_participants

#print new_scraped_interactions
#scrape most recent interaction element
#grab the most recent interaction data from the db
#if scraped element != most recent element
#    stop
#new_scraped_interactions.push(scraped_elements)
#scroll down the page
#scrape all interaction elements




#def get_data(url):
    #

# given a list of urls
    #for url in urls
        #dirty_data = get_data(url)
        #clean_data = cleaner(dirty_data)
        #send data to graph database
