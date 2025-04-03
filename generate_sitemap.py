import feedparser
from datetime import datetime, timedelta
import pytz
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Fetch the RSS feed
rss_url = "https://www.xfeed.ca/blog-feed.xml"
print("Fetching RSS feed from:", rss_url)
feed = feedparser.parse(rss_url)

# Debug: Check if the feed was fetched
print("Number of entries in feed:", len(feed.entries))
if not feed.entries:
    print("Error: No entries found in the RSS feed. Check the URL or feed content.")
    exit()

# Get the current time in UTC
now = datetime.now(pytz.UTC)
time_limit = now - timedelta(hours=48)
print("Current time (UTC):", now)
print("Time limit (48 hours ago):", time_limit)

# Create the root element for the sitemap
urlset = Element("urlset")
urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
urlset.set("xmlns:news", "http://www.google.com/schemas/sitemap-news/0.9")

# Counter for included articles
included_articles = 0

# Process each article in the RSS feed
for entry in feed.entries:
    # Parse the publication date
    try:
        pub_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.UTC)
        print(f"Article: {entry.title}, Published: {pub_date}")
    except AttributeError as e:
        print(f"Error parsing pubDate for article: {entry.title}. Error: {e}")
        continue
    
    # Check if the article is within the last 48 hours
    if pub_date >= time_limit:
        print(f"Including article: {entry.title}")
        # Create a <url> entry
        url = SubElement(urlset, "url")
        loc = SubElement(url, "loc")
        loc.text = entry.link
        
        # Create the <news:news> section
        news = SubElement(url, "news:news")
        publication = SubElement(news, "news:publication")
        name = SubElement(publication, "news:name")
        name.text = "Xfeed"
        language = SubElement(publication, "news:language")
        language.text = "en"
        pub_date_elem = SubElement(news, "news:publication_date")
        pub_date_elem.text = pub_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        title = SubElement(news, "news:title")
        title.text = entry.title
        included_articles += 1
    else:
        print(f"Skipping article (too old): {entry.title}")

# Debug: Check how many articles were included
print(f"Total articles included in sitemap: {included_articles}")

# Convert to a pretty-printed XML string
xml_str = minidom.parseString(tostring(urlset, encoding="utf-8")).toprettyxml(indent="  ")

# Fix the XML declaration to include encoding
xml_str = xml_str.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')

# Debug: Print the generated XML
print("Generated XML:\n", xml_str)

# Write to news-sitemap.xml
with open("news-sitemap.xml", "w", encoding="utf-8") as f:
    f.write(xml_str)
print("Sitemap written to news-sitemap.xml")
