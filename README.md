# 1tamilmv-rss-parser
parse rss feed and get new entries since yesterday

* feeds.txt file contains the rss feeds to parse. Add or remove rss feeds as required
* Results available in output/results.json
* Update the RESOLUTION variable as required to choose resolution of new entries that are retrieved. Default is 720p. Can be 4K, 1080p, 720p. It can actually filter the entries based on whatever string that is provided here. (It looks for the string in the url)
* Update DELTA_DAYS to choose look back period. Default is 1 day (new entries since yesterday)

* The program runs and exits.
* So create a cron job to run it on schedule.

To run
> pip install --no-cache-dir -r requirements.txt
> 
> python app.py

or 
use with the Dockerfile
> docker compose up --build

To automate getting notification of newly added entries and automating download using qbittorrent,
Refer: [ntfy-qbit-download-automate](https://github.com/0x004ad3E/ntfy-qbit-download-automate)
