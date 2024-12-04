import pytest
from unittest.mock import patch, mock_open

from reviewer import review_drafts_openai

# Mock constants
VALID_POSTS = ["Post 1 content", "Post 2 content", "Post 3 content"]
MOCK_YAML_CONTENT = "reviewer_system_message: This is a system message."
MOCK_API_RESPONSE = "Best Post"

from unittest.mock import MagicMock

def test_valid_input():
    """Test valid input produces expected results."""
    with patch("builtins.open", mock_open(read_data=MOCK_YAML_CONTENT)), \
         patch("os.environ.get", side_effect=lambda key: "mock_api_key" if key == "OPENAI_KEY" else None), \
         patch("reviewer.OpenAI") as mock_openai:
        # Mock API response
        mock_client = mock_openai.return_value
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        # Set up the mock objects
        mock_message.content = MOCK_API_RESPONSE
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Run the function and verify the result
        result = review_drafts_openai(VALID_POSTS)
        assert result == MOCK_API_RESPONSE
        mock_openai.assert_called_once()



def test_invalid_posts():
    """Test function raises ValueError for invalid posts."""
    invalid_posts = ["Only one post"]  # Not three posts
    with pytest.raises(ValueError, match="`posts` must be a list of exactly three non-empty strings."):
        review_drafts_openai(invalid_posts)

def test_missing_api_key():
    """Test function raises EnvironmentError when API key is missing."""
    with patch("os.environ.get", return_value=None), \
         patch("builtins.open", mock_open(read_data=MOCK_YAML_CONTENT)):
        with pytest.raises(EnvironmentError, match="Missing API key for OpenAI."):
            review_drafts_openai(VALID_POSTS)

def test_missing_config_file():
    """Test function raises FileNotFoundError when the config file is missing."""
    with patch("builtins.open", side_effect=FileNotFoundError), \
         patch("os.environ.get", return_value="mock_api_key"):
        with pytest.raises(FileNotFoundError, match="Configuration file not found at"):
            review_drafts_openai(VALID_POSTS)

def test_missing_reviewer_system_message():
    """Test function raises KeyError when `reviewer_system_message` is missing."""
    with patch("builtins.open", mock_open(read_data="{}")), \
         patch("os.environ.get", return_value="mock_api_key"):
        with pytest.raises(KeyError, match="The key `reviewer_system_message` is missing in the configuration file."):
            review_drafts_openai(VALID_POSTS)

def test_openai_api_error():
    """Test function handles OpenAI API errors."""
    with patch("builtins.open", mock_open(read_data=MOCK_YAML_CONTENT)), \
         patch("os.environ.get", return_value="mock_api_key"), \
         patch("reviewer.OpenAI") as mock_openai:
        # Mock API error
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            review_drafts_openai(VALID_POSTS)
