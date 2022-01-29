import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
       self.browser.quit()

    def test_can_see_blog_posts_from_current_account_holders_and_create_an_account(self):
        # User has stumbled upon this great online blogging app
        # They go checkout its homepage
        self.browser.get('http://localhost:5000/')

        # They realise the title and header mention Blog
        self.assertIn('Blog', self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, 'h1')
        self.assertIn('Blog Post', header_text.text)


        # They also realise the posts of members with accounts on the left half 
        # of the page

        # They are prompted to login if they have an account or create a new account


