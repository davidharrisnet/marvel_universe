import glob
import re
import json
import os

marvel_langchain = "/home/bilbo/dev/data/avengers"
issue_summaries = os.path.join(marvel_langchain, "issue_summaries")
issue_json = os.path.join(marvel_langchain, "issue_clean_json")

def clean_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        text =  ' '.join(lines)
        cleantext = re.sub(r'[^a-zA-Z0-9!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\s]+', '', text)
        cleantext = cleantext.replace("\n", "")
        filename = filepath[filepath.rfind("\\")+1:]
        dirpath = os.path.dirname(filepath)
        destdir = dirpath.replace('issue_summaries_xmen', 'issue_xmen_clean_json')
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        dest_filepath = os.path.join(destdir, filename)   
    with open(dest_filepath,"w", encoding='utf-8') as f:
        f.write(cleantext)



def get_text_from_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        text =  data['full_text']
        cleantext = re.sub(r'[^a-zA-Z0-9!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\s]+', '', text)
        cleantext = cleantext.replace("\n", " ")
        filename = filepath[filepath.rfind("\\")+1:]
        dirpath = os.path.dirname(filepath)
        destdir = dirpath.replace('issue_summaries_xmen', 'clean_fulltext_xmen')
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        filename = filename.replace(".json", ".txt")

        dest_filepath = os.path.join(destdir, filename)        
        with open(dest_filepath,"w", encoding='utf-8') as f:
            f.write(cleantext)


if __name__ == "__main__":


    print("cleaning text")

    issue_summaries = "issue_summaries_xmen"
    issue_json_path = issue_summaries+ '/**/*.json'
    #print(os.listdir(issue_summaries))
    files = glob.glob(issue_json_path)
    for f in files:
        clean_text(f)
    print("done")
    '''

 
    issue_json_path = "issue_summaries_xmen"+ '/**/*.json'
    #print(os.listdir(issue_summaries))
    files = glob.glob(issue_json_path)
    for f in files:
        get_text_from_json(f)
    print("done")
    '''