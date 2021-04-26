# Tweetrace
# 🏁 🏁 🏁
## Overview
Small data pipeline project to stream tweets, analyze their underlying sentiments and display results in a Streamlit front-end. For final output see https://tweetrace.herokuapp.com/

## Requirements
- Twitter credentials to access API - see https://developer.twitter.com/en/apply-for-access
- Access to a PostgreSQL database (e.g. on AWS or locally hosted)
- tweepy - to access the Twitter API - `pip install tweepy`
- sqlalchemy - to access the SQL database - `pip install sqlalchemy`
- pandas - for data wrangling - `pip install pandas`
- transformers - to load BERT model for sentiment analysis - `pip install transformers`
- torch - to use BERT model for predictions - see https://pytorch.org/ 
