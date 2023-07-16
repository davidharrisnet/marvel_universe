import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlretrieve
import shutil

URL = "https://www.ncbi.nlm.nih.gov/pmc/?term=psychology+of+back+pain"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

reports = soup.find_all("div", {"class": "rslt"})
for rprt in reports:
    details = rprt.find("div", {"class": "supp"})
    online_date = details.find("span",{"class" : ""})

    results = rprt.find_all("div", {"class": "links"})

    i = 0
    for links in results:
        views = links.find_all("a", {"class": "view"})
        for view in views:
            link = view['href']
            if link.endswith(".pdf"):
                i += 1
                print("Downloading file: ", i)

                # Get response object for link

                doc_url = f"https://www.ncbi.nlm.nih.gov{link}"

                HEADERS = { 'User-Agent':
                            'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148' }

                response = requests.get(doc_url, stream=True,headers=HEADERS)

                # Write content in pdf file
                name = link[link.rfind("/") +1:link.rfind(".")]
                path = "C:\\Users\\Bilbo\\OneDrive\\Documents\\david\\Work\\BackPainStudy\\pdf_files_download"
                #with open(f"{path}\\{name}.pdf", 'wb') as pdf:
                #    response.raw.decode_content = True
                #    shutil.copyfileobj(response.raw,pdf)
                #pdf.close()
                with open(f"{path}\\{name}.text", 'w') as f:
                    f.write(online_date.text)
                print("File ", i, " downloaded")

