import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlretrieve
import shutil
import os

path = "C:\\Users\\Bilbo\\OneDrive\\Documents\\david\\Work\\Marvel\\wiki_pages"


def download_pdfs(page_source, page_number):
    global path
    pdf_destination = os.path.join(path, page_number)
    os.makedirs(pdf_destination, exist_ok=True)
    soup = BeautifulSoup(page_source, "html.parser")

    reports = soup.find_all("div", {"class": "rslt"})
    doc_count = 0
    for rprt in reports:
        details = rprt.find("div", {"class": "supp"})
        online_date = details.find("span", {"class": ""})
        if online_date is None:
            online_date = details.find("span", {"class": "citation-publication-date"})

        results = rprt.find_all("div", {"class": "links"})

        for links in results:
            views = links.find_all("a", {"class": "view"})
            for view in views:
                link = view['href']
                if link.endswith(".pdf"):
                    doc_count = doc_count + 1
                    print("Downloading file: ", doc_count)

                    # Get response object for link

                    doc_url = f"https://www.ncbi.nlm.nih.gov{link}"

                    HEADERS = {'User-Agent':
                                   'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

                    response = requests.get(doc_url, stream=True, headers=HEADERS)

                    # Write content in pdf file
                    name = link[link.rfind("/") + 1:link.rfind(".")]
                    pdf_path = f"{os.path.join(pdf_destination,name)}.pdf"
                    if not os.path.exists(pdf_path):
                        with open(pdf_path, 'wb') as pdf:
                           response.raw.decode_content = True
                           shutil.copyfileobj(response.raw, pdf)
                        pdf.close()
                    try:
                        with open(f"{pdf_destination}\\{name}.text", 'w') as f:
                            f.write(online_date.text)
                    except Exception as e:
                        print(e)
                        print(f"Page {page_number} document {doc_count} name {name}.pdf")
