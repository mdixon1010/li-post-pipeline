import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup
import requests
from scraper import scrape_article

# Sample RSS feed data for testing
RSS_FEED_DATA = """
<rss>
  <channel>
    <item>
      <title>BigQuery Table Partitioning — A Comprehensive Guide</title>
      <category>Data</category>
      <category>Google Cloud</category>
      <content:encoded>
        <![CDATA[<p>This is a comprehensive guide on BigQuery table partitioning.</p>]]>
      </content:encoded>
      <guid>https://example.com/article1</guid>
    </item>
    <item>
      <title>Introduction to Kubernetes</title>
      <category>DevOps</category>
      <category>Containers</category>
      <content:encoded>
        <![CDATA[<p>Learn the basics of Kubernetes.</p>]]>
      </content:encoded>
      <guid>https://example.com/article2</guid>
    </item>
  </channel>
</rss>
"""

@patch("requests.get")
def test_scrape_article_success(mock_get):
    """
    Test that scrape_article successfully retrieves the correct article data.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = RSS_FEED_DATA

    feed_url = "https://example.com/feed"
    article_title = "BigQuery Table Partitioning — A Comprehensive Guide"

    expected_output = {
        "title": "BigQuery Table Partitioning — A Comprehensive Guide",
        "tags": ["Data", "Google Cloud"],
        "article_content": "<p>This is a comprehensive guide on BigQuery table partitioning.</p>",
        "link": "https://example.com/article1",
    }

    result = scrape_article(feed_url, article_title)

    # Normalize content for comparison
    result_content = BeautifulSoup(result["article_content"], "html.parser").get_text().strip()
    expected_content = BeautifulSoup(expected_output["article_content"], "html.parser").get_text().strip()

    print (result_content)
    print (expected_content)
    
    assert result["title"] == expected_output["title"]
    assert result["tags"] == expected_output["tags"]
    assert result["link"] == expected_output["link"]
    assert result_content == expected_content


@patch("requests.get")
def test_scrape_article_not_found(mock_get):
    """
    Test that scrape_article returns None when the specified article is not found.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = RSS_FEED_DATA

    feed_url = "https://example.com/feed"
    article_title = "Nonexistent Article Title"

    result = scrape_article(feed_url, article_title)
    assert result is None


@patch("requests.get")
def test_scrape_article_request_failure(mock_get):
    """
    Test that scrape_article raises an exception when the HTTP request fails.
    """
    mock_get.side_effect = requests.exceptions.RequestException("Request failed")

    feed_url = "https://example.com/feed"
    article_title = "BigQuery Table Partitioning — A Comprehensive Guide"

    with pytest.raises(requests.exceptions.RequestException):
        scrape_article(feed_url, article_title)


@patch("requests.get")
def test_scrape_article_invalid_feed(mock_get):
    """
    Test that scrape_article returns None when the feed contains no valid articles.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "<rss></rss>"  # Empty feed

    feed_url = "https://example.com/feed"
    article_title = "BigQuery Table Partitioning — A Comprehensive Guide"

    result = scrape_article(feed_url, article_title)
    assert result is None
