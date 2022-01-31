import time
import unittest
from selenium import webdriver
from project.app import app
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


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
        page_text = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn('Log in', page_text.text)

    def test_can_log_in_successfully(self):

        self.browser.get('http://localhost:5000/login')
        
        # They create an account and land on a page prompting them to create a blog post
        input_box = self.browser.find_element(By.ID, 'login-username')
        input_box.send_keys(app.config['USERNAME'])
        input_box = self.browser.find_element(By.ID, 'login-password')
        input_box.send_keys(app.config['PASSWORD'])
        input_box = self.browser.find_element(By.ID, 'login-btn')
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        # The user is invited to enter a title and post for their blog post
        input_box = self.browser.find_element(By.ID, 'title-input')
        self.assertEqual(
            input_box.get_attribute('placeholder'),
            'Enter a blog title'
        )

        input_box = self.browser.find_element(By.ID, 'post-input')
        self.assertEqual(
            input_box.get_attribute('placeholder'),
            'Write a post'
        )
