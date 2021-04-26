from sqlalchemy import create_engine
import sqlalchemy
import numpy as np
import pandas as pd
import db_config
import torch
import re
import time
from datetime import datetime
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Connect to AWS RDS Postgresql DB
HOST = db_config.host 
PORT = db_config.port
USERNAME = db_config.username
PASSWORD = db_config.password
DB = db_config.db

conn_string = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'
engine = create_engine(conn_string, echo=False)

print('Connection to DB established')

#Initialize BERT Model
model = AutoModelForSequenceClassification.from_pretrained('savedmodels/bert-fine-tuned-gersent-final')
tokenizer = AutoTokenizer.from_pretrained('savedmodels/bert-fine-tuned-gersent-final')

print('BERT model loaded')

def clean_data(data):
    """Processes raw tweets to clean text"""
    
    #Removing URLs with a regular expression
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    data = url_pattern.sub(r'', data)
    
    # Remove mentionings
    data = re.sub(r'@\w*', '', data)
    
    # Remove special characters
    data = re.sub(r"(?=[^\.\?\!])\W", " ", data)
    
    # Remove new line characters
    data = re.sub(r'\s+', ' ', data)
    
    return data.strip()

def predict_sentiment(text):
    text = [clean_data(text)]
    input_ids = tokenizer(text, padding=True, truncation=True, add_special_tokens=True)
    input_ids = torch.tensor(input_ids["input_ids"])
    
    with torch.no_grad():
            logits = model(input_ids)
            
    label_ids = torch.argmax(logits[0], axis=1)
    
    labels = [model.config.id2label[label_id] for label_id in label_ids.tolist()]
    
    return labels[0]

def tweet_to_score(text):
    
    sentiment = predict_sentiment(text)
    
    score = 0
    
    if sentiment == 'negative':
        score = -1
    elif sentiment == 'positive':
        score = 1
    
    return score


if __name__ == '__main__':
    while True:
        
        # Read in table of raw tweets from DB
        try:
            tweets = pd.read_sql('tweets', engine)
        except:
            engine = create_engine(conn_string, echo=False)
            time.sleep(1)
            tweets = pd.read_sql('tweets', engine)
        print('Raw tweets loaded from DB')
        print(f'{len(tweets)} tweets collected')
        #Check if table is empty and if so wait and start over
        if tweets.empty == True:
            print(f'No new tweets in table. Will go to sleep for 5 min. - {time.asctime( time.localtime(time.time()) )}')
            time.sleep(5*60)
            continue

        # Get timestamp of last tweet in table and convert to datetime
        last_tweet = tweets['created_at'][-1:].values[0]
        last_tweet_dt = last_tweet.astype('datetime64[s]').tolist()
        print(f'Last tweet collected from: {last_tweet_dt}')

        # Get Sentiment from BERT German
        tweets['score'] = tweets['text'].apply(tweet_to_score)

        # Store Sentiment Score to Postgresql
        try:
            tweets.to_sql('sentiment_score',engine, index = False,
                            if_exists = 'append', 
                            dtype = {'tweet_id':sqlalchemy.types.BigInteger(),
                            'created_at':sqlalchemy.types.DateTime(timezone=False),
                            'name':sqlalchemy.types.VARCHAR(length=50),
                            'text':sqlalchemy.types.Text,
                            'score':sqlalchemy.types.Integer()})

            
        except:
            print('Trying to reconnect to DB')
            engine = create_engine(conn_string, echo=False)
            time.sleep(2)
            tweets.to_sql('sentiment_score',engine, index = False,
                            if_exists = 'append', 
                            dtype = {'tweet_id':sqlalchemy.types.BigInteger(),
                            'created_at':sqlalchemy.types.DateTime(timezone=False),
                            'name':sqlalchemy.types.VARCHAR(length=50),
                            'text':sqlalchemy.types.Text,
                            'score':sqlalchemy.types.Integer()})
        
        print(f'{len(tweets)} Sentiments loaded to DB')
        time.sleep(2)
        
        # Delete processed tweets from tweets table
        delete_query = """DELETE FROM tweets WHERE created_at <= (%s);"""
        engine.execute(delete_query,last_tweet_dt)

        print('Raw tweets deleted from table')

        #BREAK FOR DEVELOPMENT STAGE
        print('Done! Breaking for now')
        break

        # Wait for 2 min before repeating
        print(f'Waiting for 2 min. - {time.asctime( time.localtime(time.time()) )}')
        time.sleep(2*60)