# LinkedIn Post Pipeline Tool

## How to Setup

1. Clone the repo

1. Create a python virtual envrionment \
`python3 -m venv lipost` 

1. Activate your virtual environment \
`source lipost/bin/activate`

1. Install dependencies with `pip` \
`pip install -r requirements.txt`

1.  Create an environment file using the format in `env/.env_sample`

1. Source your env file \
` source env/.env`

1. Create LinkedIn post from Medium article \
`python src/li_post_pipeline.py ARTICLE_TITLE=title USER=user`\
\
Example: \
`python src/li_post_pipeline.py "BigQuery Table Partitioning — A Comprehensive Guide" matt.dixon1010`


## Helpful Links
- https://pub.towardsai.net/scraping-your-medium-stories-a3a078ab2e7f
- [OpenAI API Key Usage Activity Page](https://platform.openai.com/usage/activity)

## Services Used: 
- [ChatGPT API](https://platform.openai.com/)

## Pre Push to Origin
### Run Tests
`pytest tests/`

### Check Test Coverage
`pytest --cov=src tests/`

### Check Linting
`flake8 src/`



## To Do

### General
- Smoke test/ update things
- Fill in gitignore
- Start version controlling this on GH

### Post Generator 
- productionalize the post pipeline
- create tests for post pipeline
- create tests for scraper
- increase test coverage


I have the following python file used in a larger codebase.  Please provide google style docstrings and format the code using PEP8 standards. Also, if there are things that should be tidied up before releasing to production let me know, but dont modify the code. 