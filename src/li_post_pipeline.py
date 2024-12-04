import argparse
from scraper import scrape_article
from writer import write_post_openai
from reviewer import review_drafts_openai
from typing import List



def scrape_medium_article(feed: str, article_title: str ) -> dict[str]: 

    article_data = scrape_article(feed, article_title )
    return(article_data)


def create_post_draft(article_text: str) -> str:
    
    post_draft = write_post_openai(article_text)
    return(post_draft)


def rank_post_drafts(drafts: List[str]) -> str:
    
    final_draft = review_drafts_openai(drafts)
    return(final_draft)


def add_bolierplate (post_body: str, tags: List[str], article_url: str) -> str:

    tag_str = " #".join(tags).lstrip().replace('-', '')
    
    final_post = post_body + '\n\n' + f"Check it out the article here --> {article_url}"
    final_post = final_post + '\n\n' + "Until, next time… ☟" 
    final_post = final_post + '\n' + "https://www.beardeddata.com"
    final_post = final_post + '\n\n' + "#" + tag_str
    return(final_post)
    

def main(feed: str, article_title: str):
    """
    Main function to scrape a Medium article and create a draft post with a title, username, and content.
    
    Args:
        feed (str): The feed URL of the Medium user.
        article_title (str): The title of the article to scrape.
        username (str): The username of the Medium author.
    """
    # Scrape post and grab context/metadata
    article_data = scrape_medium_article(feed, article_title)

    title = article_data.get('title')
    tags = article_data.get('tags')
    text = article_data.get('article_content')
    link = article_data.get('link')

    article_text = title + '\n' + text

    # Create draft post bodies
    drafts = []
    for i in range(3): 
        draft_post_body = create_post_draft(article_text)

        print(f"Option #{i + 1}")
        print(draft_post_body)
        print('\n')
        drafts.append(draft_post_body)

    # Grab the best one
    final_draft = rank_post_drafts(drafts)

    print("Final Draft")
    print(final_draft)
    print('\n')

    # Add boilerplate to it
    final_post = add_bolierplate(final_draft, tags, link)

    print("!------------------ Final Post ------------------!")
    print(final_post)
    print('\n')


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Scrape a Medium article and generate draft posts.")
    parser.add_argument('article_title', type=str, help='The title of the article to scrape')
    parser.add_argument('username', type=str, help='The username of the Medium author')

    # Parse the arguments
    args = parser.parse_args()

    
    feed = f"https://medium.com/feed/@{args.username}"


    # Call the main function with arguments
    main(feed, args.article_title, )