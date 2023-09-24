from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
import os
import time

def valid_title(filename):
    filename = filename.strip()
    invalid = '<>:"/\|?* '
    for char in invalid:
        filename = filename.replace(char, '')
    return filename

def click_link(driver, text):
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, text))
    )
    element.click()
    return element

def get_table(driver, class_name):
        table = driver.find_element(By.CLASS_NAME, class_name)
        return table.find_elements(By.TAG_NAME,"td")
     
class Avengers:
    def __init__(self, url, top_dir="issue_summaries_xmen"):
        self.top_dir = top_dir
        self.url = url
        self.driver = self.get_driver()
        self.soup = self.open_page()

    def get_driver(self):
        # create webdriver object
        options = webdriver.FirefoxOptions()

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        #options.add_argument('--headless')
        return webdriver.Firefox(options=options)

    def open_page(self):

        #URL = "https://mightyavengers.net/comics/series"
        URL = f"{self.url}/comics/series/all"
        self.driver.get(URL)
        page_source = self.driver.page_source
        return BeautifulSoup(page_source, "html.parser")



    def get_summaries(self):
        titles = self.soup.find_all("td", class_="views-field views-field-field-comic-titles")
        
        #rows = get_table(self.driver, "views-table cols-3")
        offset = 107
        for index, title in enumerate(titles[offset:]):
            
            link = title.find("a")
            comic_title = link.text
            print(f"{index + offset} {comic_title}")
            if comic_title == "4":
                continue
            # create output directory for this summaries pages
            comic_title_dir = valid_title(comic_title)
            title_dir = os.path.join(self.top_dir, comic_title_dir)
            os.makedirs(title_dir, exist_ok=True)

            comic_title = comic_title.strip()
            try:
                click_link(self.driver, comic_title)
            except Exception as e:
                print(e)
            try:
                click_link(self.driver, "Issue Summaries")
            except Exception as e:
                print(e)
            #url = self.driver.current_url
            #self.driver.get(url)
           
    
            element = click_link(self.driver, '50')
            for _ in range(4):
                element.send_keys(Keys.ARROW_DOWN)
            element.send_keys(Keys.ENTER)
            apply_button =self.driver.find_element(By.ID, "edit-submit-summaries-for-title")
            apply_button.click()
            #summary_url = self.driver.current_url
              
           
           
            
            #element = self.driver.find_element(By.ID, "edit-submit-summaries-for-title")
            #element.click()
                               
            try:    
                #soup = BeautifulSoup(requests.get(summary_url).content, "html.parser") 
                title = Title(self.driver,self.soup, title_dir)
                title.save_issues()
            except Exception as e:
                print(e)
            

class Title():
    def __init__(self, driver, soup, title_dir):
        self.driver = driver        
        self.soup = soup
        self.story_object = {}
        self.title_dir = title_dir  
              
     
    def save_issues(self):       
        summary_tds = get_table(self.driver, "views-table")
        self.summaries(summary_tds)

    def summaries(self, summary_tds):
        for index, summary_td in enumerate(summary_tds):           
            try:
                if index %2 == 0:
                    tds = get_table(self.driver, "views-table")
                    link = tds[index].find_element(By.TAG_NAME, "a")
                    link.click()
                else:
                    continue;
                try:                
                    url = self.driver.current_url
                    
                    print(url)
                    soup = BeautifulSoup(requests.get(url).content, "html.parser")
                    self.save_issue(soup)
                    self.driver.back()
                    click_link(self.driver, "Issue Summaries")
                except Exception as e:
                    print(e)
                    raise ConnectionError(e)
                
            except Exception as e:
                print(e)
        self.driver.back()
        

    def save_issue(self, soup):
        self.title(soup)
        self.brief_description(soup)
        self.full_description(soup)
        self.characters(soup)
        self.story_notes(soup)
        self.save_json(soup)

    def title(self, soup):
        title = soup.find(class_="field-name-field-story-title")
        if title:
            story_title = title.find(class_="field-item even").text
            self.story_object['story_title'] = story_title
        else:
            self.story_object['story_title'] = ""

    def brief_description(self, soup):
        brief = soup.find(class_="field-name-field-story-brief")
        if brief:
            stories = brief.find(class_="field-item even")
            stories_list = []
            for c in stories.children:
                if c != '\n':
                    stories_list.append(c.text)
            self.story_object['brief_description'] = stories_list
        else:
            self.story_object['brief_description'] = []

    def full_description(self, soup):
        story_full = soup.find(class_="field-name-field-story-full")
        if story_full:
            story_full_text = story_full.find(class_="field-item even").text
            self.story_object['full_text'] = story_full_text
        else:
            self.story_object['full_text'] = ""

    def characters(self, soup):
        characters = soup.find(class_="field-name-field-story-chars")
        if characters:
            characters_list = characters.find(class_="field-item even")
            characters_involved = []
            for p in characters_list.find_all("p"):
                characters_involved.append(p.text)
            self.story_object["characters_involved"] = characters_involved
        else:
            self.story_object["characters_involved"] = []

    def story_notes(self, soup):
        story_notes = soup.find(class_="field-name-field-story-notes")
        if story_notes:
            story_notes_text = story_notes.find(class_="field-item even").text
            self.story_object['story_notes'] = story_notes_text
        else:
            self.story_object['story_notes'] = ""

    def save_json(self, soup):

        issue_title = soup.find(id="page-title").text

        issue_title = valid_title(issue_title)
        issue_path = os.path.join(self.title_dir, f"{issue_title}.json")
        with open(issue_path, "w") as f:
            json.dump(self.story_object, f)

def save_one(url,title_dir):
    avengers = Avengers()

    url = "https://uncannyxmen.net/comics/issue/uncanny-avengers-annual-1st-series-1"
    title_dir = "C:\\Users\\Bilbo\\Documents\\dev\\python\\marvel_universe\\data\\avengers\\issue_summaries\\UncannyAvengers(1stseries)"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    title = Title(soup, title_dir)
    title.save_issue(soup)
def main():
    url = "https://uncannyxmen.net"
    avengers = Avengers(url, "issue_summaries_xmen")
    avengers.get_summaries()


if __name__ == "__main__":
    main()
