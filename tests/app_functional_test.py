import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
       self.browser.quit()

    def test_home_page_includes_hello_world_in_html_body(self):
        self.browser.get('http://localhost:5000/')
        body_text = self.browser.find_element(By.TAG_NAME, 'body')

        self.assertIn('Hello, World!', body_text.text)

    # User has stumbled upon this great online blogging app
    # They go checkout its homepage

    # They realise the title and header mention blogging app

    # They also realise the posts of members with accounts on the left half 
    # of the page

    # They are prompted to login if they have an account or create a new account


