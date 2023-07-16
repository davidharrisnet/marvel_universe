
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import soup_page
import string

def soupit(driver):
    page_source = driver.page_source
    current_url = driver.current_url
    soup = BeautifulSoup(page_source, "html.parser")

    #navs = soup.find_all("div", {"class": "hatnote navigation-not-searchable"})
    links = soup.find_all("a")
    print(links)




def download_all():

    links = ["0-9"] + [f"{letter}" for letter in string.ascii_uppercase]

    # create webdriver object
    options = webdriver.FirefoxOptions()

    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    #options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    URL = "https://en.wikipedia.org/wiki/Lists_of_Marvel_Comics_characters"
    # get geeksforgeeks.org
    driver.get(URL)

    # get element
    page_source = driver.page_source

    for link in links:

        try:
            page = f"List of Marvel Comics characters: {link}"

            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT,page))
            )

            # click the element
            element.click()


            soupit(driver)

            #element = driver.find_element(By.LINK_TEXT, "Next >")
            #page_source = driver.page_source

            driver.execute_script("window.history.go(-1)")
        except Exception as e:
            print(e)

    driver.close()

if __name__ == "__main__":
    download_all()