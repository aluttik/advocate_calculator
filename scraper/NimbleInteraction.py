import re
from datetime import datetime, date
from selenium.common.exceptions import NoSuchElementException


class NimbleInteractionUknownType(Exception):

    def __init__(self, body):
        __error_message = "Unknown Interaction Type"
        __elem_class = body.get_attribute('class')
        __elem_html = body.get_attribute('innerHTML').encode('utf8')
        with open("unrecognized_types.log", "a") as f:
            f.write(__elem_class + "\n")
            f.write(__elem_html + "\n")
            f.write("\n")
        self.message = "ERROR:" + __error_message + ":" + __elem_class
    def __str__(self):
        return str(self.message)


class NimbleInteraction(object):

    def __init__(self, row):
        self.body = row

        # establish the type of interaction
        self.__type_search = re.search('(.+)ContactWidget( .+)?', self.body.get_attribute('class'))
        self.type = self.__type_search.group(1)
        if self.__type_search.group(2):
            self.subtype = self.__type_search.group(2)

        # parse out the required information
        if self.type == 'Event':
            self.__parse_event()
        elif self.type == 'Twitter':
            self.__parse_twitter()
        elif self.type == 'Email':
            self.__parse_email()
        else:
            raise NimbleInteractionUnknownType(self.body)


    def __is_valid_time(self, text):
        if re.search('at \d?\d:\d\d [apAP][mM]', text):
            return True
        else:
            return False


    def __find_year(self, search):
        if search.group(2):
            return search.group(2)
        else:
            return str(date.today().year)


    def __find_date(self, css_selector):
        self.__element = self.body.find_element_by_css_selector(css_selector)
        self.__search = re.search('on ([A-Za-z]{3} \d?\d)(, \d{4})?', self.__element.text)
        if self.__search:
            self.__year = self.__find_year(self.__search)
            return datetime.strptime('%s, %s' % (self.__search.group(1), self.__year), '%b %d, %Y').date()
        elif self.__is_valid_time(self.__element.text):
            return date.today()
        else:
            raise


    def __find_subject(self, css_selector):
        try:
            return self.body.find_element_by_css_selector(css_selector).text
        except NoSuchElementException:
            return '(no subject)'


    def __parse_event(self):
         self.date = self.__find_date('div.created')
         self.subject = self.__find_subject('div.subject')


    def __parse_twitter(self):
        self.date = self.__find_date('div.details div:last-of-type')
        self.subject = self.__find_subject('div.subject')


    def __parse_email(self):
        self.date = self.__find_date('div.details div:last-of-type')
        self.subject = self.__find_subject('div.subject')


#~ table > tbody > tr:nth-child(21) > td > div > div > div.details > div:nth-child(4)

