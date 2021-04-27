# Tweetrace
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

## How it works

### Config files - *twitter_config.py*, *db_config.py*
These files contain the connection details to access the Twitter API and the PostgreSQL database

### Twitter stream - *get_tweets_streaming.py*
Connects to the Twitter API and creates a Stream object to filter tweets in realtime. The filtered tweets are stored in a temporary table in the database. Retweets are ignored.
The `stream.filter` method of the Stream object can be adjusted, e.g. to track a different set of words, names etc. or filter tweets in a different language than German. 
See Tweepy documentation for further information on parameters https://docs.tweepy.org/en/latest/stream.html

### Sentiment analysis - *get_sentiments.py*
Loads a fine-tuned BERT model to process tweets and derive their underlying sentiments. Returns *+1* for as positive, *-1* for a negative and *0* for a neutral sentiment.

The model is based on a already fine-tuned BERT model from the Transformers Library (https://huggingface.co/oliverguhr/german-sentiment-bert) that was further trained with labeled tweets and is saved locally. To enable the code to work without the local copy the path to the locally saved model was replaced by the path to the original model from the Transformers Library.

The processed tweets are stored with their respective score in a different table of the database. Afterwards the raw tweets are deleted from the temporary table.

### Streamlit - *streamlit_app.py*
Calculates the daily mean of the sentiment score and the daily count of collected tweets per politician name. The results are displayed in an interactive Plotly graph.
Configures a Streamlit front-end and embeds the Plotly graph as well as text for Explanation and References.

In order to run the Streamlit front-end enter `streamlit run streamlit_app.py` in the terminal.
