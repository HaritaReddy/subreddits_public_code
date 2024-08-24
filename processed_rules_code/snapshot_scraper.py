import json
from waybackpy import WaybackMachineCDXServerAPI
import time

"""
Input: Reads subreddits from the year json files in subreddits_by_year
Output: Write the year file to subreddits_snapshots_by_year
For each year, 
  For each subreddit
    Fetch all the snapshots in the range July 2019 to July 2022
"""

# Include all year files inside the subreddits_by_year/ folder that you want to process
input_files = ['2010.json', '2016.json', '2017.json']

for file in input_files:
    year = int(file[0:4])
    print(year)
    
    # This is for storing the list of wayback machine snapshots for each subreddit. This is finally written as a file for each year in subreddits_snapshots_by_year
    subreddit_snapshots_per_year = {}
    
    subreddits = json.loads(open('subreddits_by_year/' + file,"r").read())
    for subreddit in subreddits:
        print(subreddit)
        subreddit_snapshots_per_year[subreddit] = []
        # Get snapshots using Wayback machine
        url = "http://www.reddit.com/r/" + subreddit + "/"
        user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
        try:
          cdx = WaybackMachineCDXServerAPI(url=url, user_agent=user_agent)
          snapshots = cdx.snapshots()
          for snapshot in snapshots:
             archive_url = snapshot.archive_url
             snapshot_date = archive_url.split("/")[4]
             snapshot_year = int(snapshot_date[:4])
             snapshot_month = int(snapshot_date[4:6])
             # Collects snapshots in the duration July 2019-June 2022 and check the count (as a filtering condition)
             # This condition can be changed based on the duration of the evaluation period. In this code we are
             # getting snapshots for July 2019-June 2022. This was later backfilled to get snapshots back until April 2018.
             if snapshot_year in [2020, 2021] or (snapshot_year == 2019 and snapshot_month >= 7) or (snapshot_year == 2022 and snapshot_month < 7):
                 subreddit_snapshots_per_year[subreddit].append(archive_url)
        except:
          continue
        time.sleep(2)
    with open("subreddits_snapshots_by_year/" + str(year) + ".json", "w") as outfile:
        json.dump(subreddit_snapshots_per_year, outfile)
    time.sleep(5)
