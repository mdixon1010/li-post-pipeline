import requests
from bs4 import BeautifulSoup
from bs4.builder import XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)


def scrape_article(feed_url: str, article: str):
    """
    Scrapes an RSS feed and extracts articles, including titles, tags, and content.
    Optionally filters and returns details for a specific article based on its title.

    Args:
        feed_url (str): The URL of the RSS feed to scrape.
        article (str): The title of the article to filter. Defaults to None.

    Returns:
        list[dict]: A list of dictionaries, each containing:
            - "title" (str): The title of the article.
            - "tags" (list[str]): A list of tags (categories) associated with the article.
            - "article_content" (str): The full content of the article.
            If `article` is provided, the list will contain at most one dictionary for the matching article.
    """
    # Send a GET request to the RSS feed URL
    r = requests.get(feed_url)

    # Parse the response using BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')

    # Clean up content by removing CDATA markers
    content = str(soup).replace('<![CDATA[', '').replace(']]>', '')
    content = BeautifulSoup(content, 'html.parser')

    # Find all article entries in the feed
    articles = content.find_all('item')

    for article_entry in articles:

        title = article_entry.find('title').text
        tags = [tag.text for tag in article_entry.find_all('category')]
        article_content = article_entry.find('content:encoded').text
        link = article_entry.find('guid').text

        article_dict = {
            "title": title,
            "tags": tags,
            "article_content": article_content,
            "link": link
        }

        if title == article:
            return article_dict

    return None


if __name__ == "__main__":

    feed = "https://medium.com/feed/@matt.dixon1010"
    article_title = 'BigQuery Table Partitioning — A Comprehensive Guide'

    article_data = scrape_article(feed, article_title)

    print(article_data)
