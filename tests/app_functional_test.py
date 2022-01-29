from selenium import webdriver
from selenium.webdriver.common.by import By

def test_home_page_includes_hello_world_in_html_body():
    browser = webdriver.Firefox()
    browser.get('http://localhost:5000/')
    body_text = browser.find_element(By.TAG_NAME, 'body')

    assert 'Hello, World!' in body_text.text