from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
import os


class Avengers:
    def __init__(self, top_dir="issue_summaries"):
        self.top_dir = top_dir

        self.driver = self.get_driver()
        self.soup = self.open_page()

    def get_driver(self):
        # create webdriver object
        options = webdriver.FirefoxOptions()

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        return webdriver.Firefox(options=options)

    def open_page(self):

        URL = "https://mightyavengers.net/comics/series"
        self.driver.get(URL)
        element = self.find_link("ALL")
        # click the element
        element.click()
        page_source = self.driver.page_source
        return BeautifulSoup(page_source, "html.parser")

    def find_link(self, text):
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, text))
        )
        return element

    def get_summaries(self):
        titles = self.soup.find_all("td", class_="views-field views-field-field-comic-titles")
        link_elements = []
        for title in titles:
            link = title.find("a")
            comic_title = link.text
            comic_title = self.valid_title(comic_title)
            title_dir = os.path.join("issue_summaries", comic_title)
            if not os.path.exists(title_dir):
                os.makedirs(title_dir, exist_ok=True)

                s = link.get('href').rfind("/") + 1
                url = self.driver.current_url[:-3] + link.get('href')[s:]
                soup = BeautifulSoup(requests.get(url).content, "html.parser")

                title = Title(soup, title_dir)
                title.save_issues()

    def valid_title(self, filename):
        filename = filename.strip()
        invalid = '<>:"/\|?* '
        for char in invalid:
            filename = filename.replace(char, '')
        return filename


class Title():
    def __init__(self, soup, title_dir):
        self.soup = soup
        self.story_object = {}
        self.title_dir = title_dir

    def save_issues(self):
        summary_links = self.soup.find_all("td", class_="views-field views-field-title views-align-left")
        self.summaries(summary_links)

    def summaries(self, summary_links):
        for summary_link in summary_links:
            issue_link = summary_link.find("a")

            url = "https://mightyavengers.net" + issue_link.get('href')
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            self.save_issue(soup)

    def save_issue(self, soup):
        self.title(soup)
        self.brief_description(soup)
        self.full_description(soup)
        self.characters(soup)
        self.story_notes(soup)
        self.save_json(soup)

    def valid_title(self, filename):
        filename = filename.strip()
        invalid = '<>:"/\|?* '
        for char in invalid:
            filename = filename.replace(char, '')
        return filename

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

        issue_title = self.valid_title(issue_title)
        issue_path = os.path.join(self.title_dir, f"{issue_title}.json")
        with open(issue_path, "w") as f:
            json.dump(self.story_object, f)


def main():
    avengers = Avengers()
    avengers.get_summaries()


if __name__ == "__main__":
    main()
