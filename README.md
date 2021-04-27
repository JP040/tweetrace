# Tweetrace (work in progress)
# 🏁 🏁 🏁
## Overview
Small data pipeline project to stream tweets relating to three selected German politicians, analyze their underlying sentiments and display results as scores in a Streamlit front-end. For final output see https://tweetrace.herokuapp.com/

## Requirements
### General
- Twitter credentials to access API - see https://developer.twitter.com/en/apply-for-access
- Access to a PostgreSQL database (e.g. on AWS or locally hosted)
### Dependencies
- tweepy - to access the Twitter API - `pip install tweepy`
- sqlalchemy - to access the SQL database - `pip install sqlalchemy`
- pandas - for data wrangling - `pip install pandas`
- transformers - to load BERT model for sentiment analysis - `pip install transformers`
- torch - to use BERT model for predictions - see https://pytorch.org/ 
- streamlit - to create the front-end - `pip install streamlit`
- matplotlib - to use for data visualization - `pip install matplotlib`
- plotly - to use for interactive data visualization - `pip install plotly`

## Getting started
Clone the repository - `git clone https://github.com/JP040/tweetrace.git`

### Config files - *twitter_config.py*, *db_config.py*
After successfully applying for Twitter API access fill in the received access details in the *twitter_config.py* file.
Enter you connection details for the database you want to use in the *db_config.py* file.

### Twitter stream - *get_tweets_streaming.py*
The `stream.filter` method in *get_tweets_streaming.py* can be adjusted, e.g. to track a different set of words, names etc. or filter tweets in a different language than German. 

See Tweepy documentation for further information on parameters https://docs.tweepy.org/en/latest/stream.html

### Sentiment analysis - *get_sentiments.py*
Processing the tweets and deriving their underlying sentiments is based on a fine-tuned BERT model from the Transformers Library (https://huggingface.co/oliverguhr/german-sentiment-bert). The code can be adjusted to use other models suitable for sentiment classification from the Transformers Library by replacing the current repository reference in the following code block with the repository of another model:
    
    model = AutoModelForSequenceClassification.from_pretrained('...')
    tokenizer = AutoTokenizer.from_pretrained('...')
    
The labels ("positive", "negative", "neutral") for sentiment classification might be different in other models and break the code when tranforming the predicted sentiment of a tweet to *+1*, *-1* or *0*. Therefore, the `tweet_to_score` function might need to be adjusted.

### Streamlit - *streamlit_app.py*
In order to run the Streamlit front-end enter `streamlit run streamlit_app.py`
