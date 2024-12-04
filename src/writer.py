import os
import yaml
import logging
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

# Constants
YML_CONFIG = os.environ.get("YML_CONFIG", "./config/system_prompts.yml")

def write_post_openai(medium_content: str) -> str:
    """
    Generates a LinkedIn post body based on a Medium article's content using OpenAI's GPT model.

    This function communicates with OpenAI's API to create a LinkedIn post body based on the
    provided Medium article. The output is tailored to be engaging, avoiding hashtags, markdown
    formatting, and emojis, focusing instead on clear, concise, and impactful text designed
    for maximum impressions.

    Args:
        medium_content (str): The content of the Medium article to base the LinkedIn post on.

    Returns:
        str: The generated LinkedIn post content.

    Raises:
        ValueError: If the OpenAI API key is missing or invalid.
        FileNotFoundError: If the configuration YAML file cannot be found.
        ValueError: If there is an issue parsing the YAML file or the response from OpenAI.
        Exception: If an error occurs during the API call or response handling.
    """
    # Check if OpenAI API key is set
    openai_api_key = os.environ.get("OPENAI_KEY")
    if not openai_api_key:
        logging.error("OPENAI_KEY is not set in environment variables.")
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")

    # Load YAML configuration with error handling
    try:
        with open(YML_CONFIG, 'r') as conf_file:
            conf = yaml.safe_load(conf_file)

    except FileNotFoundError:
        logging.error(f"Configuration file not found at: {YML_CONFIG}")
        raise FileNotFoundError(f"Configuration file {YML_CONFIG} not found.")
    
    except yaml.YAMLError as e:
        logging.error("Error parsing YAML file: {e}")
        raise ValueError(f"Error parsing YAML file: {e}")

    system_message = conf.get('writer_system_message')

    if not system_message:
        logging.error("Missing `reviewer_system_message` in configuration file.")
        raise ValueError("The 'writer_system_message' key is missing in the configuration.")
    
    logging.info("System message loaded successfully.")

    user_message = (
        f"""Given the Medium article content between the <article> tags, generate the body of a LinkedIn post.
        <article> {medium_content} <article>"""
    )

    try:

        client = OpenAI(api_key=openai_api_key)

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

        draft = response.choices[0].message.content
    
        logging.info("Successfully generated draft from OpenAI.")

        return draft

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise  