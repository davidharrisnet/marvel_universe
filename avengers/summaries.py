from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
import os
import csv
import time

def valid_title(filename):
    filename = filename.strip()
    invalid = '<>:"/\|?* '
    for char in invalid:
        filename = filename.replace(char, '')
    return filename

def click_link(driver, text):
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, text))
    )
    element.click()
    return element
     
class Avengers:
    def __init__(self, url, output_dir, output_csv):
        self.output_dir = output_dir
        self.csv_file = output_csv
        os.makedirs(self.output_dir, exist_ok=True)
        self.url = url
        self.driver = self.get_driver()
        self.soup = self.open_page()
        with open(self.csv_file, "w") as f:
           writer = csv.writer(f)
           writer.writerow(["Summary_Title", "Summary_Count", "Errors"])
            
    def log_progress(self,comic_title, issues_count):
        with open(self.csv_file, "a", newline='') as f:
           writer = csv.writer(f)
           writer.writerow([comic_title, issues_count, ""])
           
    def get_driver(self):
        # create webdriver object
        options = webdriver.FirefoxOptions()

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        #options.add_argument('--headless') # Uncomment this to see the GUI
        return webdriver.Firefox(options=options)

    def open_page(self):

        #URL = "https://mightyavengers.net/comics/series"
        URL = f"{self.url}/comics/series/all"
        self.driver.get(URL)
        page_source = self.driver.page_source
        return BeautifulSoup(page_source, "html.parser")

    def get_links(self):
        table =  self.driver.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/div[2]/div[4]/table")
        return table.find_elements(By.TAG_NAME, "a")
    
    def get_link(self, index):
        links = self.get_links()
        return links[index]
    
    def click_all(self):
        element = click_link(self.driver, '50')
        for _ in range(4):
            element.send_keys(Keys.ARROW_DOWN)
        element.send_keys(Keys.ENTER)
        apply_button =self.driver.find_element(By.ID, "edit-submit-summaries-for-title")
        apply_button.click()
            
    def get_summaries(self, retry_list=None):
       
        links =  self.get_links()
                
        offset = 0
        for index, _ in enumerate(links[offset:]):
        
            link = self.get_link(index +  offset)
            comic_title = link.text
                
            print(f"{index + offset} {comic_title}")
    
            # create output directory for this summaries pages
            comic_title_dir = valid_title(comic_title)
            title_dir = os.path.join(self.output_dir, comic_title_dir)
         
          
                    
            if ( os.path.exists(title_dir) and len(os.listdir(title_dir)) == 0 ) or ( retry_list is not None and comic_title in retry_list ): 
                                
                os.makedirs(title_dir, exist_ok=True)

                comic_title = comic_title.strip()
                try:                
                    link.click()
                except Exception as e:
                    print(e)
                    link = self.get_link(index +  offset)
                    link.click()
                try:
                    click_link(self.driver, "Issue Summaries")
                except Exception as e:                
                    print("No Issue Summaries Tab")
                    self.driver.back() # back to all menu
                    continue
    
                self.click_all()               
                
                try:                  
                    title = Title(self.driver, title_dir, self.csv_file, comic_title)
                    title.save_issues()                
                except Exception as e:
                    print(e)
                    
                self.driver.back() # back to all menu
            else:
                # log the number of summaries for this title
                summary_count = len(os.listdir(title_dir))
                self.log_progress(comic_title, summary_count)
   

class Title():
    def __init__(self, driver, title_dir, csv_file, comic_title):
        self.comic_title = comic_title
        self.driver = driver                
        self.story_object = {}
        self.title_dir = title_dir  
        self.csv_file = csv_file
       
        
    def get_table(self):            
            table = self.driver.find_element(By.CLASS_NAME, "views-table.cols-2")           
            return table.find_elements(By.TAG_NAME,"td")
           
    def save_issues(self):       
        summary_tds = self.get_table()
        
        self.summaries(summary_tds)

    def summaries(self, summary_tds):
        issues_count = 0        
        errors = ""
        for index, _ in enumerate(summary_tds):           
                       
            try:
                tds = self.get_table()
                link = tds[index].find_element(By.TAG_NAME, "a")
                link.click()
            except Exception:
                continue;
            try:                
                time.sleep(3)
                url = self.driver.current_url
                
                print(url)
                soup = BeautifulSoup(requests.get(url).content, "html.parser")
                self.save_issue(soup)
                issues_count += 1
            except Exception as e:
                print(e) 
                errors  = str(e)    
            try:
                # go back
                self.driver.back()
                time.sleep(1)
                click_link(self.driver, "Issue Summaries") 
                time.sleep(1)                      
            except Exception as e:
                print(e)
                errors = str(e)
                self.log_progress(issues_count,errors)            
            self.log_progress(issues_count,errors)
            
    def log_progress(self, issues_count, errors=""):
        with open(self.csv_file, "a", newline='') as f:
           writer = csv.writer(f)
           writer.writerow([self.comic_title, issues_count, errors])
                           
    def save_issue(self, soup):
        self.title(soup)
        self.brief_description(soup)
        self.full_description(soup)
        self.characters(soup)
        self.story_notes(soup)
        self.save_json(soup)

    def title(self, soup):
        try:

            self.title = soup.find(class_="page__title")
            if self.title:                
                self.story_object['story_title'] = self.title.text                
            else:
                self.story_object['story_title'] = ""
        except:
            self.story_object['story_title'] = ""

    def brief_description(self, soup):
        try:
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
        except:
            self.story_object['brief_description'] = []

    def full_description(self, soup):
        try:
            story_full = soup.find(class_="field-name-field-story-full")
            if story_full:
                story_full_text = story_full.find(class_="field-item even").text
                self.story_object['full_text'] = story_full_text
            else:
                self.story_object['full_text'] = ""
        except:
            self.story_object['full_text'] = ""

    def characters(self, soup):
        try:
            characters = soup.find(class_="field-name-field-story-chars")
            if characters:
                characters_list = characters.find(class_="field-item even")
                characters_involved = []
                for p in characters_list.find_all("p"):
                    characters_involved.append(p.text)
                self.story_object["characters_involved"] = characters_involved
            else:
                self.story_object["characters_involved"] = []
        except:
            self.story_object["characters_involved"] = []

    def story_notes(self, soup):
        try:
            story_notes = soup.find(class_="field-name-field-story-notes")
            if story_notes:
                story_notes_text = story_notes.find(class_="field-item even").text
                self.story_object['story_notes'] = story_notes_text
            else:
                self.story_object['story_notes'] = ""
        except:
            self.story_object['story_notes'] = ""
    def save_json(self, soup):

        issue_title = soup.find(id="page-title").text

        issue_title = valid_title(issue_title)
        issue_path = os.path.join(self.title_dir, f"{issue_title}.json")
        with open(issue_path, "w") as f:
            json.dump(self.story_object, f)

def save_one():
    url = "https://uncannyxmen.net/comics/series/all-new-doop"
    title_dir =        "C:\\Temp\\issue_summaries_xmen2\\AllNewDoop"
    output_csv_path =  "C:\\Temp\\issue_summaries_xmen2\\report.csv"
    avengers = Avengers(url, title_dir, output_csv_path)
    avengers.driver
    
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    title = Title( avengers.driver, title_dir, avengers.csv_file, "All New Doop")
    title.save_issues()

def main():
    """
    error_list =  [
                    "Dark X-Men", # had errors
                    "Dazzler",
                    "Deadpool (2nd series)",
                    "Excalibur (1st series)",
                    "Hulk (1st series)",
                    "Marvel Comics Presents (1st series)",
                    "Marvel Comics Presents (1st series)",
                    "Marvel Super-Heroes (2nd series)",
                    "New Avengers (4th series)",
                    "New Mutants (1st series)",
                    "New Mutants (3rd series)",
                    "New X-Men (1st series)"           
                    "Ultimate Comics X-Men",
                    "Ultimate Fallout",
                    "Ultimate Fantastic Four",
                    "Ultimate Marvel Team-Up",
                    "Ultimate Nightmare",
                    "Ultimate Origins",
                    "Ultimate Power",
                    "Ultimate Spider-Man"
                    "Ultimate X-Men",        
                    "Uncanny Avengers (1st series)",
                    "Uncanny Avengers (2nd series)",
                    "Uncanny Avengers (3rd series)",
                    "Uncanny X-Men (1st series)",
                    "West Coast Avengers (2nd series)",
                    "What If...? (2nd series)",
                    "Wolverine & Jubilee",
                    "Wolverine (1st series)",
                    "Wolverine (2nd series)",
                    "Wolverine (3rd series)",
                    "Wolverine (4th series)",
                    "Wolverine (7th series)",
                    "Wolverine / Captain America"
                    "Wolverine: First Class",
                    "Wolverine: Origins",
                    "Wolverine: The Best There Is",
                    "Wolverine: The End",
                    "X-23 (2nd series)",
                    "X-Factor (1st series)",
                    "X-Factor (3rd series)",
                    "X-Factor (4th series)",
                    "Astonishing X-Men (3rd series)",
                    "X-Force (1st series)",
                    "X-Force (3rd series)",
                    "X-Force (4th series)",
                    "X-Force: Sex and Violence",
                    "X-Force: Shatterstar",
                    "X-Infernus",
                    "X-Man",
                    "X-Men (1st series)",
                    "X-Men (2nd series)",
                    "X-Men (3rd series)",
                    "X-Men (4th series)",
                    "X-Men (5th series)",
                    "X-Men (6th series)",
                    "X-Men / Fantastic Four",
                    "X-Men / Wildcats",
                    "X-Men 2099",
                    "X-Men Adventures (Season I)",
                    "X-Men Adventures (Season II)",
                    "X-Men and Power Pack",        
                    "X-Men Legacy (1st series)",
                    "X-Men Legacy (2nd series)",
                    "X-Men Legends (1st series)",
                    "X-Men Noir",
                    "X-Men Noir: Mark of Cain",
                    "X-Men Origins",
                    "X-Men Unlimited (1st series)",
                    "X-Men Unlimited (2nd series)",
                    "X-Men: Age of Apocalypse",
                    "X-Men: Classic",
                    "X-Men: Colossus Bloodline",
                    "X-Men: Deadly Genesis",
                    "X-Men: Die By the Sword",
                    "X-Men: Divided We Stand",
                    "X-Men: Emperor Vulcan",
                    "X-Men: First Class (2nd series)",
                    "X-Men: First Class Finals",
                    "X-Men: Gold",
                    "X-Men: Kingbreaker",
                    "X-Men: Kitty Pryde: Shadow & Flame",
                    "X-Men: Liberators",
                    "X-Men: Magik",
                    "X-Men: Magneto Testament",
                    "X-Men: Magneto War",
                    "X-Men: Manifest Destiny",
                    "X-Men: Phoenix End Song",
                    "X-Men: Phoenix Warsong",
                    "X-Men: Pixie Strikes Back",
                    "X-Men: Prelude to Schism",
                    "X-Men: Red (1st series)",
                    "X-Men: Red (2nd series)",
                    "X-Men: Search for Cyclops",
                    "X-Treme X-Men (1st series)",
                    "X-Treme X-Men (2nd series)",
                    "X-Treme X-Men : Savage Land",
                    "X-Treme X-Men : X-Posé",
                    "Young X-Men",
                    "Astonishing X-Men (3rd series)",
                    "Avengers West Coast",
                    "Astonishing X-Men" ]
    """
    error_list = [  "X-Men Origins"]




    # self.log_progress(issues_count,errors)

    output_json_path = "C:\\Temp\\issue_summaries_xmen"
    output_csv_path =  "C:\\Temp\\issue_summaries_xmen\\report.csv"
    url = "https://uncannyxmen.net"
    avengers = Avengers(url, output_json_path, output_csv_path)
    avengers.get_summaries(error_list)


if __name__ == "__main__":
        
    main()
    #save_one()
