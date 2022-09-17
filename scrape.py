from re import S
from turtle import delay
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import cfscrape
import cloudscraper
import sys
import os


def cfs():
    #scraper = cfscrape.create_scraper(delay=10)
    scraper = cloudscraper.create_scraper(delay=10,
                                          interpreter='nodejs',
                                          captcha={
                                              'provider': '2captcha',
                                              'api_key': 'b32b351a3bb2c44dcfd1938f7272962d'
                                          })
    with open("/var/www/FlaskApp/FlaskApp/logs/test.log", "w") as f:
        t = scraper.get(
            "https://tracker.gg/valorant/profile/riot/katpotatoo%23meow/overview").text
        f.write(t)
        return t


def scrape():
    chrome_option = Options()
    chrome_option.add_argument("--remote-debugging-port=9222")
    chrome_option.add_argument("--headless")  # open Browser in maximized mode
    # open Browser in maximized mode
    chrome_option.add_argument("--start-maximized")
    chrome_option.add_argument("--no-sandbox")  # bypass OS security model
    # overcome limited resource problems
    chrome_option.add_argument("--disable-dev-shm-usage")
    # overcome limited resource problems
    chrome_option.add_argument("features=\"html.parser\"")
    chrome_option.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_option.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(executable_path="/var/www/FlaskApp/FlaskApp/static/chromedriver/chromedriver", options=chrome_option,
                              service_log_path="/var/www/FlaskApp/FlaskApp/logs/geckodriver.log")
    # driver = webdriver.Firefox(executable_path="/var/www/FlaskApp/FlaskApp/static/geckodriver",
    # service_log_path="/var/www/FlaskApp/FlaskApp/logs/geckodriver.log",
    #  log_path='/var/www/FlaskApp/FlaskApp/logs/geckodriver.log')

    driver.get(
        'https://tracker.gg/valorant/profile/riot/katpotatoo%23meow/overview')

    content = driver.page_source
    soup = BeautifulSoup(content)
    #rank = soup.find('span', attrs={'class': 'stat__value'})
    rank = soup.findAll()
    driver.quit()
    return rank
