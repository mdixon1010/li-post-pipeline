import pytest
from unittest.mock import patch, MagicMock
from li_post_pipeline import (
    scrape_medium_article,
    create_post_draft,
    rank_post_drafts,
    add_boilerplate,
)


def test_scrape_medium_article_success():
    mock_feed = "https://medium.com/feed/@testuser"
    mock_title = "Test Article"
    mock_article_data = {
        "title": "Test Article",
        "tags": ["Tag1", "Tag2"],
        "article_content": "This is the content of the test article.",
        "link": "https://example.com/article",
    }

    with patch("li_post_pipeline.scrape_article", return_value=mock_article_data) as mock_scrape:
        result = scrape_medium_article(mock_feed, mock_title)
        mock_scrape.assert_called_once_with(mock_feed, mock_title)
        assert result == mock_article_data


def test_scrape_medium_article_not_found():
    mock_feed = "https://medium.com/feed/@testuser"
    mock_title = "Nonexistent Article"

    with patch("li_post_pipeline.scrape_article", return_value=None):
        with pytest.raises(ValueError, match=f"Article '{mock_title}' not found in feed: {mock_feed}"):
            scrape_medium_article(mock_feed, mock_title)


def test_create_post_draft_success():
    mock_article_text = "Test article content."
    mock_draft = "This is a test draft post."

    with patch("li_post_pipeline.write_post_openai", return_value=mock_draft) as mock_write:
        result = create_post_draft(mock_article_text)
        mock_write.assert_called_once_with(mock_article_text)
        assert result == mock_draft


def test_create_post_draft_error():
    mock_article_text = "Test article content."

    with patch("li_post_pipeline.write_post_openai", side_effect=Exception("OpenAI error")):
        with pytest.raises(Exception, match="OpenAI error"):
            create_post_draft(mock_article_text)


def test_rank_post_drafts_success():
    mock_drafts = ["Draft 1", "Draft 2", "Draft 3"]
    mock_best_draft = "Draft 2"

    with patch("li_post_pipeline.review_drafts_openai", return_value=mock_best_draft) as mock_review:
        result = rank_post_drafts(mock_drafts)
        mock_review.assert_called_once_with(mock_drafts)
        assert result == mock_best_draft


def test_rank_post_drafts_error():
    mock_drafts = ["Draft 1", "Draft 2", "Draft 3"]

    with patch("li_post_pipeline.review_drafts_openai", side_effect=Exception("Review error")):
        with pytest.raises(Exception, match="Review error"):
            rank_post_drafts(mock_drafts)


def test_add_boilerplate_success():
    mock_post_body = "This is the main body of the post."
    mock_tags = ["Tag1", "Tag2"]
    mock_article_url = "https://example.com/article"

    expected_output = (
        "This is the main body of the post.\n\n"
        "Check out the article here --> https://example.com/article\n\n"
        "Until next time… ☟\n"
        "https://www.beardeddata.com\n\n"
        "#Tag1 #Tag2"
    )

    result = add_boilerplate(mock_post_body, mock_tags, mock_article_url)
    assert result == expected_output


def test_add_boilerplate_empty_tags():
    mock_post_body = "This is the main body of the post."
    mock_tags = []
    mock_article_url = "https://example.com/article"

    expected_output = (
        "This is the main body of the post.\n\n"
        "Check out the article here --> https://example.com/article\n\n"
        "Until next time… ☟\n"
        "https://www.beardeddata.com\n\n"
        "#"
    )

    result = add_boilerplate(mock_post_body, mock_tags, mock_article_url)
    assert result == expected_output
