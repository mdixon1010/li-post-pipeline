import os
import logging
from typing import List
import yaml
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

# Constants
YML_CONFIG = os.environ.get("YML_CONFIG", "./config/system_prompts.yml")


def review_drafts_openai(posts: List[str]) -> str:
    """Selects the best post from three provided drafts using OpenAI's
    GPT model.

    This function reads a system prompt configuration from a YAML file ,
    constructs a user message containing the drafts, and sends the input to
    OpenAI's chat completions API to determine the best draft.

    Args:
        posts (List[str]): A list of three draft posts as strings.

    Returns:
        str: The best post as determined by the GPT model.

    Raises:
        ValueError: If `posts` does not contain exactly three non-empty
        strings.
        FileNotFoundError: If the YAML configuration file is not found.
        KeyError: If the `reviewer_system_message` key is missing in the YAML
        file. Exception: If an error occurs during the API call.
    """
    # Validate API key
    openai_api_key = os.environ.get("OPENAI_KEY")
    if not openai_api_key:
        logging.error("OPENAI_KEY is not set in environment variables.")
        error = """Missing API key for OpenAI. Set the OPENAI_KEY
        environment variable."""
        raise EnvironmentError(error)

    # Validate input
    if not isinstance(posts, list) or len(posts) != 3 or not all(isinstance(post, str) and post.strip() for post in posts):
        error = """Invalid input: `posts` must be a list of exactly
        three non-empty strings."""
        logging.error(error)

        val_error = """`posts` must be a list of exactly three
        non-empty strings."""
        raise ValueError(val_error)

    # Load system message from configuration file
    try:
        with open(YML_CONFIG, 'r') as conf_file:
            conf = yaml.safe_load(conf_file)

    except FileNotFoundError:
        error = f"Configuration file not found at: {YML_CONFIG}"
        logging.error(error)
        raise FileNotFoundError(error)

    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

    system_message = conf.get('reviewer_system_message')

    if not system_message:
        logging.error("Missing `reviewer_system_message` in configuration file.")
        raise KeyError("The key `reviewer_system_message` is missing in the configuration file.")

    logging.info("System message loaded successfully.")

    # Construct user message
    user_message = (
        f"""Given the three posts below (each between the <post> tags) output
        the best post word for word.

        # POST #1 <post> {posts[0]} <post>

        # POST #2 <post> {posts[1]} <post>

        # POST #3 <post> {posts[2]} <post>"""
    )

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)

        # Send API request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )

        # Check if response is valid
        if not response.choices or not response.choices[0].message or not response.choices[0].message.content:
            raise ValueError("Invalid response format from OpenAI API.")

        best_post = response.choices[0].message.content
        logging.info("Successfully retrieved best post from OpenAI.")

        return best_post

    except Exception as e:
        logging.error(f"An error occurred during the OpenAI API call: {e}")
        raise
