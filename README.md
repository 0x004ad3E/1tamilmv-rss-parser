# 1tamilmv-rss-parser
parse rss feed and get new entries since yesterday

* Feeds file contains the rss feeds to parse. Add or remove rss feeds as required
* Results available in output/results.json
* Update the RESOLUTION variable as required to choose resolution of new entries that are retrieved. Default is 720p. Can be 4K, 1080p, 720p. It can actually filter the entries based on whatever string that is provided here. (It looks for the string the url)
* Update DELTA_DAYS to choose look back period. Default is 1 day (new entries since yesterday)

