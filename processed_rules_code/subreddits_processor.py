
"""
Processes rules in raw_scraped_rules/ by breaking down the content in the rules widget based on the enumeration.
Input: Reads each subreddit file from the yearly subfolders in raw_scraped_rules/
Output: Write one file for each subreddit in the year subfolder within processed_rules/.
For each year, 
  For each subreddit
    Break down the raw content into a list of rules.
"""
import os
import json
import pickle
import heapq
from datetime import datetime
import spacy
import en_core_web_lg
import nltk
import re
from nltk.stem import WordNetLemmatizer


blacklisted_patterns = ["days ago", "day ago", "months ago", "month ago", "years ago", "year ago", "hours ago", "hour ago", "hide report"]

roman_numerals = set({"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"})

snapshots_path = "raw_scraped_rules/"
dirs = os.listdir(snapshots_path)

issue_count = 0
subreddits = set()

for dir in dirs:
    year = int(dir[:4])
    snapshots_subdirs = os.listdir(snapshots_path + dir + "/")

    for file in snapshots_subdirs:
        subreddit = file[:-5]
        all_rules = json.loads(open(snapshots_path + dir + "/" + file,"r").read())
        processed_subreddit_rules = {}
        prev_rules = None

        for key, value in sorted(all_rules.items()):
            successfully_scraped = False

            if value != "" and value[1] == "New":
                split_rules = re.split(' \d+\. ', " ".join(value[0].split()))

                # The following snippet is to exclude snapshots with abnormal rule lengths (>= 1000 characters) or contains
                # blacklisted phrases as listed in blacklisted_patterns
                skip_snapshot = False
                match = -1

                for rule in split_rules:
                    for pattern in blacklisted_patterns:
                        match = max(rule.find(pattern), match)
                    if len(rule) >= 1000 or match >= 0:
                        skip_snapshot = True

                if not skip_snapshot:
                    final_rules = []
                    try:
                        for i in range(0, len(split_rules)):
                            if len(split_rules[i]) == 0 or split_rules[i].isspace():
                                continue
                            if len(split_rules[i]) > 0 and split_rules[i][0].isdigit() and split_rules[i][1] == ".":
                                split_rules[i] = split_rules[i][2:]

                            split_rules[i] = split_rules[i].lower()
                            # Eliminate Roman Numerals at the beginning
                            for num in roman_numerals:
                                comb = num + "."
                                if split_rules[i].startswith(comb):
                                    split_rules[i] = split_rules[i][len(comb):]
                            split_rules[i] = split_rules[i].strip()
                            if split_rules[i] not in ['', ' ', 'rule']:
                                final_rules.append(split_rules[i])
                        successfully_scraped = True
                        processed_subreddit_rules[key] = final_rules
                    except:
                        pass

            if not successfully_scraped:
                # Check if previous there were rules present
                if prev_rules is not None and len(prev_rules) > 0:
                    processed_subreddit_rules[key] = prev_rules
                else:
                    processed_subreddit_rules[key] = []


            prev_rules = processed_subreddit_rules[key].copy()

        with open("processed_rules/" + str(dir) + "/" + subreddit + ".json", "w") as outfile:
            json.dump(processed_subreddit_rules, outfile)

