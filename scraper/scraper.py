from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
import time


path_to_chromedriver = '/Users/SBurns/Downloads/chromedriver'
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

url = "https://nginx.nimble.com/#app/contacts/view?id=5581fe938e08ab59fe6dd915"
browser.get(url)



#wait for element to appear
browser.implicitly_wait(3)
#find the element by ID
login_form_email = browser.find_element_by_id('login-f_email')
login_form_password = browser.find_element_by_id('login-f_password')

# login_form_email.clear()
# login_form_password.clear()

###++++++++++++BROKEN
#fill in form
#TODO: protect these with config vars... ASAP
browser.find_element_by_id('login-f_email').send_keys(email)
browser.find_element_by_id('login-f_password').send_keys(password)

#find signin button and press it
browser.find_element_by_xpath('//*[@id="login_loginButton"]').click()
browser.implicitly_wait(3)

#click on the "Pending & History" tab
browser.find_element_by_xpath('//*[@id="all"]').click()

new_scraped_interactions = {}
interaction_table = browser.find_element_by_class_name("topWidget").find_elements_by_class_name()
interaction = browser.find_element_by_class_name("topWidget")
interaction_between = interaction.find_elements_by_class_name("contact")
interaction_type = interaction.find

interaction_participants = []
for contact in interaction_between:
    interaction_participants.append(str(contact.text))
new_scraped_interactions["interaction_participants"] = interaction_participants

print new_scraped_interactions
#scrape most recent interaction element
#grab the most recent interaction data from the db
#if scraped element != most recent element
    #stop
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
