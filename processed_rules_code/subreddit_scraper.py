"""
This file tries to scrape content from the rules widget for each subreddit.
Input: Reads subreddits from the year json files in subreddits_snapshots_by_year/
Output: Write one file for each subreddit in the year subfolder within raw_scraped_rules/.
For each year, 
  For each subreddit
    Get the raw content of the rules widget
"""

import os
import json
import json
import datetime
from bs4 import BeautifulSoup
import re
import requests
import time

def scrape_content(url):
    page_text = requests.get(url).content
    soup = BeautifulSoup(page_text, 'html.parser')
    try:
        rules  = soup.find("div", {"class": "md"})
        final_rules = rules.text
    except Exception:
        final_rules = ""
    return final_rules


# Include all year files inside the subreddits_by_year/ folder that you want to process
input_files = ['2010.json', '2016.json', '2017.json']

for file in input_files:
    file_year = int(file[0:4])
    subreddit_snapshots = json.loads(open('subreddits_snapshots_by_year/' + file,"r").read())
    print(file_year)
    for subreddit in subreddit_snapshots:
        if os.path.exists("raw_scraped_rules/" + str(file_year) + "/" + subreddit + ".json"):
          continue
        dir_path = "raw_scraped_rules/" + str(file_year) + "/"
        num_files = len([entry for entry in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, entry))])
        print(subreddit)
        current_snapshots = subreddit_snapshots[subreddit]
        if len(current_snapshots) == 0:
            continue 
        current_snapshots.sort()

        subreddit_dict = {}
        
        
        prev_date = datetime.date(2000, 1, 1)
        for snapshot in current_snapshots:
            timestamp = snapshot.split("/")[4][0:8]
            year = int(timestamp[:4])
            month = int(timestamp[4:6])
            day = int(timestamp[6:8])
            curr_date_int = int(timestamp)
            curr_date_formatted = datetime.date(year, month, day)
            diff = curr_date_formatted - prev_date
            if diff.days < 1:
                # Avoid taking snapshots on the same day
                continue
            print(snapshot)
            try:
                tries = 5
                got_snapshot = False
                while tries > 0:
                    response = requests.get(snapshot)
                    if response.status_code != 200:
                        tries = tries - 1
                        print("Sleeping and trying again")
                        time.sleep((tries*10))
                        continue
                    else:
                        text = response.text
                        got_snapshot = True
                        print("Got snapshot")
                        break
                if got_snapshot == False:
                    subreddit_dict[curr_date_int] = "REQUEST_ERROR"
                    continue
                """
                Try with new version first
                """
                req_part = ""
                try:
                    print("Trying with new version assumption")
                    soup = BeautifulSoup(''.join(text.lower()))
                    split_items = soup.prettify().split('r/' + subreddit.lower() + ' rules')
                    # Find the tag just before rules:
                    i = len(split_items[0])-1
                    while i > 0:
                        if split_items[0][i] == "<":
                            break
                        i = i - 1
                    tag_to_search = split_items[0][i:]
                    req_part = split_items[1].split(tag_to_search)[0]
                    req_part = re.sub("<[^>]*>", "", req_part)
                    req_part = re.sub("\t", "", req_part)
                    req_part = re.sub("\n", "", req_part)
                    subreddit_dict[curr_date_int] = [req_part, "New"]
                except:
                    req_part = ""
                if req_part == "":
                    subreddit_dict[curr_date_int] = "SCRAPING_ERROR"
            except:
                subreddit_dict[curr_date_int] = "SCRAPING_ERROR"
                continue
            prev_date = curr_date_formatted
            time.sleep(7)

        with open("raw_scraped_rules/" + str(file_year) + "/" + subreddit + ".json", "w") as outfile:
            json.dump(subreddit_dict, outfile)
        time.sleep(10)
