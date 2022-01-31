import time
import unittest
from selenium import webdriver
from project.app import app
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
       self.browser.quit()

    def check_for_posts_in_list(self, post_title, post_text):
        posts = self.browser.find_element(By.CLASS_NAME, 'entries')
        post = self.browser.find_element(By.CLASS_NAME, 'entry')
        self.assertIn(post_title, post.text)
        self.assertIn(post_text, post.text)

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

    def test_can_log_in_successfully_and_create_and_delete_posts(self):
        driver = self.browser
        driver.get('http://localhost:5000/login')

        # They create an account and land on a page prompting them to create a blog post
        input_box = driver.find_element(By.ID, 'login-username')
        input_box.send_keys(app.config['USERNAME'])
        input_box = driver.find_element(By.ID, 'login-password')
        input_box.send_keys(app.config['PASSWORD'])
        input_box = driver.find_element(By.ID, 'login-btn')
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        wait = WebDriverWait(driver, 10)
        wait.until(lambda driver: driver.current_url != 'http://localhost:5000/login')
        
        # The user is invited to enter a title and post for their blog post
        input_box = driver.find_element(By.ID, 'title-input')

        self.assertEqual(
            input_box.get_attribute('placeholder'),
            'Enter a blog title'
        )
        input_box.send_keys('Blog title')

        input_box = driver.find_element(By.ID, 'post-input')
        self.assertEqual(
            input_box.get_attribute('placeholder'),
            'Write a post'
        )

        input_box.send_keys('New post.')

        send_post_button = driver.find_element(By.ID, 'post-btn')
        send_post_button.send_keys(Keys.ENTER)

        time.sleep(1)

        self.check_for_posts_in_list('Blog title', 'New post.')


if __name__ == "__main__":
    unittest.main()