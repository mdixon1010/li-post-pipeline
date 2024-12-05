import argparse
import logging
from scraper import scrape_article
from writer import write_post_openai
from reviewer import review_drafts_openai
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

logger = logging.getLogger(__name__)


def scrape_medium_article(feed: str, article_title: str) -> Dict[str, str]:
    """
    Scrapes a Medium article using the feed URL and article title.

    Args:
        feed (str): The RSS feed URL of the Medium user.
        article_title (str): The title of the article to scrape.

    Returns:
        Dict[str, str]: A dictionary containing article metadata such as title, tags,
                        content, and link.

    Raises:
        ValueError: If the article cannot be scraped or is missing required fields.
    """
    try:
        article_data = scrape_article(feed, article_title)
        if not article_data:
            raise ValueError(f"Article '{article_title}' not found in feed: {feed}")
        return article_data
    except Exception as e:
        logger.error("Error scraping article: %s", e)
        raise


def create_post_draft(article_text: str) -> str:
    """
    Creates a draft post from the given article text using OpenAI's API.

    Args:
        article_text (str): The text content of the article.

    Returns:
        str: A draft LinkedIn post body generated from the article.

    Raises:
        RuntimeError: If the draft cannot be created.
    """
    try:
        return write_post_openai(article_text)
    except Exception as e:
        logger.error("Error creating post draft: %s", e)
        raise


def rank_post_drafts(drafts: List[str]) -> str:
    """
    Ranks multiple draft posts and selects the best one using OpenAI's API.

    Args:
        drafts (List[str]): A list of draft posts.

    Returns:
        str: The highest-ranked draft post.

    Raises:
        RuntimeError: If ranking fails.
    """
    try:
        return review_drafts_openai(drafts)
    except Exception as e:
        logger.error("Error ranking drafts: %s", e)
        raise


def add_boilerplate(post_body: str, tags: List[str], article_url: str) -> str:
    """
    Adds boilerplate text, tags, and a link to the final post.

    Args:
        post_body (str): The main body of the post.
        tags (List[str]): A list of tags associated with the article.
        article_url (str): The URL of the original article.

    Returns:
        str: The final formatted post with boilerplate text.
    """
    try:
        tag_str = " #".join(tags).lstrip().replace("-", "")
        final_post = (
            f"{post_body}\n\n"
            f"Check out the article here --> {article_url}\n\n"
            "Until next time… ☟\n"
            "https://www.beardeddata.com\n\n"
            f"#{tag_str}"
        )
        return final_post
    except Exception as e:
        logger.error("Error adding boilerplate: %s", e)
        raise


def main(feed: str, article_title: str):
    """
    Main function to scrape a Medium article and create a draft post.

    Args:
        feed (str): The RSS feed URL of the Medium user.
        article_title (str): The title of the article to scrape.
    """
    try:
        logger.info("Scraping article: %s from feed: %s", article_title, feed)
        article_data = scrape_medium_article(feed, article_title)

        title = article_data.get("title")
        tags = article_data.get("tags", [])
        text = article_data.get("article_content", "")
        link = article_data.get("link", "")

        article_text = f"{title}\n{text}"

        # Create draft post bodies
        drafts = []
        for i in range(3):
            logger.info("Generating draft #%d", i + 1)
            draft_post_body = create_post_draft(article_text)
            drafts.append(draft_post_body)

        # Grab the best one
        final_draft = rank_post_drafts(drafts)
        logger.info("Best draft selected.")

        # Add boilerplate to it
        final_post = add_boilerplate(final_draft, tags, link)
        logger.info("Final post created.")

        print("!------------------ Final Post ------------------!")
        print(final_post)
        print("\n")

    except Exception as e:
        logger.error("An error occurred during execution: %s", e)


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Scrape a Medium article and generate draft posts.")
    parser.add_argument("article_title", type=str, help="The title of the article to scrape")
    parser.add_argument("username", type=str, help="The username of the Medium author")

    # Parse the arguments
    args = parser.parse_args()

    # Construct the feed URL
    feed = f"https://medium.com/feed/@{args.username}"

    # Call the main function with arguments
    main(feed, args.article_title)
