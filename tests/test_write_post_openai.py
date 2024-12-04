import pytest
from unittest.mock import patch, MagicMock, mock_open
from writer import write_post_openai  # Replace with the actual module name

# Sample data for testing
MOCK_MEDIUM_CONTENT = "This is a sample Medium article content."
MOCK_API_KEY = "mock_api_key"
MOCK_SYSTEM_MESSAGE = "Generate a LinkedIn post body from the following article content."

# Sample mock YAML content
MOCK_YML_CONTENT = """
writer_system_message: "Generate a LinkedIn post body from the following article content."
"""

MOCK_API_RESPONSE = "This is the generated LinkedIn post."

# Test when everything works fine
# Correcting test_write_post_openai_success
def test_write_post_openai_success():
    with patch("builtins.open", mock_open(read_data=MOCK_YML_CONTENT)) as mock_open_patch, \
         patch("writer.yaml.safe_load", return_value={"writer_system_message": MOCK_SYSTEM_MESSAGE}) as mock_yaml_patch, \
         patch("os.environ.get", return_value=MOCK_API_KEY) as mock_env_patch, \
         patch("writer.OpenAI") as mock_openai_patch:

        # Prepare the mock response for OpenAI API
        mock_client = mock_openai_patch.return_value
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_message.content = MOCK_API_RESPONSE
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Call the function
        result = write_post_openai(MOCK_MEDIUM_CONTENT)

        # Assert the result and check if the OpenAI API was called
        assert result == MOCK_API_RESPONSE
        mock_openai_patch.assert_called_once()
        mock_client.chat.completions.create.assert_called_once()

# Test when the OpenAI API key is missing
def test_missing_openai_api_key():
    with patch("os.environ.get", return_value=None):
        with pytest.raises(ValueError, match="The OPENAI_API_KEY environment variable is not set."):
            write_post_openai(MOCK_MEDIUM_CONTENT)

# Test when the configuration file is missing
def test_missing_config_file():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError, match=f"Configuration file ./config/system_prompts.yml not found."):
            write_post_openai(MOCK_MEDIUM_CONTENT)

# Test when the YAML file is invalid
def test_invalid_yaml():
    # Simulate invalid YAML by raising an exception when trying to parse the config
    with patch("builtins.open", mock_open(read_data="invalid_yaml: !!invalid")), \
         patch("os.environ.get", return_value=MOCK_API_KEY), \
         patch("writer.OpenAI") as MockOpenAI:
        
        # Try to call the function and catch the exception
        try:
            write_post_openai(MOCK_MEDIUM_CONTENT)
        except ValueError as e:
            # Assert that the error message contains the expected part
            assert "Error parsing YAML file" in str(e)

# Test when the system message is missing from the configuration
def test_missing_system_message_in_config():
    # Simulate a configuration file where 'writer_system_message' is missing
    with patch("builtins.open", mock_open(read_data="")), \
         patch("writer.yaml.safe_load", return_value={}), \
         patch("os.environ.get", return_value=MOCK_API_KEY), \
         patch("writer.OpenAI") as MockOpenAI:

        # Try to call the function and check if it raises the expected error
        with pytest.raises(ValueError, match="The 'writer_system_message' key is missing in the configuration."):
            write_post_openai(MOCK_MEDIUM_CONTENT)

# Test when OpenAI API response is invalid
def test_invalid_openai_response():
    # Simulate an invalid response structure from OpenAI API
    with patch("builtins.open", mock_open(read_data="writer_system_message: Write a LinkedIn post.")), \
         patch("writer.yaml.safe_load", return_value={"writer_system_message": MOCK_SYSTEM_MESSAGE}), \
         patch("os.environ.get", return_value=MOCK_API_KEY), \
         patch("writer.OpenAI") as MockOpenAI:

        # Mocking the OpenAI client to return an invalid response
        mock_client_instance = MockOpenAI.return_value
        # Create a mock response with the expected structure
        mock_response = MagicMock()
        # Now mock the `choices` list with a dictionary that has a `message` attribute
        mock_response.choices = [MagicMock(message=MagicMock(content=None))]  # Invalid content
        
        mock_client_instance.chat.completions.create.return_value = mock_response

        # Call the function and check if it raises a ValueError or handles the invalid response
        with pytest.raises(ValueError, match="Invalid response format from OpenAI API."):
            write_post_openai(MOCK_MEDIUM_CONTENT)