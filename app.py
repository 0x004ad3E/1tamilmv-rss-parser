import json
import logging
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
from bs4 import BeautifulSoup


FEEDS_FILE = Path("/app/feeds.txt")
OUTPUT_DIR = Path("/output")

LOG_FILE = OUTPUT_DIR / "rss-parser.log"
RESULTS_FILE = OUTPUT_DIR / "results.json"

DELTA_DAYS = 1 #yesterday
RESOLUTION = "720p"

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Feed configuration
# ----------------------------------------------------------------------

def load_feeds():
    feeds = []

    with FEEDS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            feeds.append(line)

    return feeds


# ----------------------------------------------------------------------
# Date handling
# ----------------------------------------------------------------------

def get_yesterday():
    return datetime.now().date() - timedelta(days=DELTA_DAYS)


def get_entry_date(entry):
    published = entry.get("published")

    if not published:
        return None

    try:
        return parsedate_to_datetime(published).date()
    except (TypeError, ValueError) as error:
        logger.warning(
            "Could not parse publication date '%s': %s",
            published,
            error,
        )
        return None


# ----------------------------------------------------------------------
# Description parsing
# ----------------------------------------------------------------------

def parse_description(description):
    soup = BeautifulSoup(
        description or "",
        "html.parser",
    )

    # First image
    first_img = soup.find("img")

    if first_img:
        first_image_url = first_img.get("src")
    else:
        first_image_url = None

    # Matching magnet links
    magnet_links = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()

        if not href:
            continue

        if not href.lower().startswith("magnet:"):
            continue

        if RESOLUTION.lower() not in href.lower():
            continue

        magnet_links.append(href)

    # Remove duplicates
    magnet_links = list(dict.fromkeys(magnet_links))

    return first_image_url, magnet_links


# ----------------------------------------------------------------------
# RSS processing
# ----------------------------------------------------------------------

def process_feed(feed_url, yesterday):
    logger.info("Processing feed: %s", feed_url)

    try:
        feed = feedparser.parse(feed_url)
    except Exception:
        logger.exception(
            "Failed to parse feed: %s",
            feed_url,
        )
        return []

    if feed.bozo:
        logger.warning(
            "Feed reported a parsing problem: %s",
            feed_url,
        )

    tags = "series" if "series" in feed_url.lower() else "movies"
    results = []

    for entry in feed.entries:

        entry_date = get_entry_date(entry)
        if entry_date is None:
            continue

        if entry_date != yesterday:
            continue

        title = entry.get("title", "")
        topic_url = entry.get("link", "")
        published = entry.get("published", "")
        description = entry.get("description", "")

        first_image, magnet_links = parse_description(
            description
        )

        if not magnet_links:
            logger.info(
                "Matching date but no %s magnet link: %s",
                RESOLUTION,
                title,
            )
            continue

        result = {
            "feed": feed_url,
            "title": title,
            "published": published,
            "date": entry_date.isoformat(),
            "topic_url": topic_url,
            "first_image": first_image,
            "magnet_links": magnet_links,
            "tags": tags
        }

        results.append(result)

        logger.info(
            "Matched entry: %s",
            title,
        )

    logger.info(
        "Finished feed: %s (%d matching entries)",
        feed_url,
        len(results),
    )

    return results


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():

    logger.info("========================================")
    logger.info("RSS parser started")

    yesterday = get_yesterday()

    logger.info(
        "Looking for entries dated: %s",
        yesterday,
    )

    try:
        feeds = load_feeds()
    except Exception:
        logger.exception("Failed to load feeds.txt")
        return

    logger.info(
        "Loaded %d RSS feeds",
        len(feeds),
    )

    all_results = []

    for feed_url in feeds:
        results = process_feed(
            feed_url,
            yesterday,
        )

        all_results.extend(results)

    try:
        with RESULTS_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                all_results,
                file,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(
            "Wrote %d results to %s",
            len(all_results),
            RESULTS_FILE,
        )

    except Exception:
        logger.exception(
            "Failed to write results"
        )

    logger.info(
        "RSS parser finished. Total results: %d",
        len(all_results),
    )

    logger.info("========================================")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception(
            "Unhandled exception"
        )
