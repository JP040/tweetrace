from twitter_config import Twitter
from tweepy import OAuthHandler, Stream, API
from tweepy.streaming import StreamListener
from sqlalchemy import create_engine
import time
import logging
import db_config
from urllib3.exceptions import ProtocolError,IncompleteRead


#Connection to the database
HOST = db_config.host 
PORT = db_config.port
USERNAME = db_config.username
PASSWORD = db_config.password
DB = db_config.db

conn_string = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'
engine = create_engine(conn_string, echo=False)

#Creation of temporary table to store raw tweets
query_create_table = """
CREATE TABLE IF NOT EXISTS tweets (
  tweet_id BIGINT,
  created_at TIMESTAMP,
  name VARCHAR(50),
  text TEXT
);
"""
engine.execute(query_create_table)

logging.critical('Start listening to tweets')

#Function to connect to TwitterAPI
def authenticate():
    """Function for handling Twitter Authentication. 
       Script assumes you have a file called config.py
       which stores the 4 required authentication tokens:

       1. API_KEY
       2. API_SECRET
       3. ACCESS_TOKEN
       4. ACCESS_TOKEN_SECRET
    """
    consumer_key = Twitter['consumer_key']
    consumer_secret = Twitter['consumer_secret']
    access_token = Twitter['access_token']
    access_token_secret = Twitter['access_token_secret']

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    return api

# Initialize the StreamListener
class TweetsListener(StreamListener):

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
    def on_connect(self):
        logging.critical('Connected. Listening for incoming tweets')


    def on_status(self, status):
        """Method which defines what is done with
        every single tweet as it is intercepted in real-time"""
    	
        
        if hasattr(status,'retweeted_status'):
            print('RT - skipped')
        else:

            try:      
        
                tweet = {
                    'id': status.id,
                    'text': str(status.extended_tweet["full_text"]),
                    'time': status.created_at
                }

            except AttributeError:
                tweet = {
                    'id': status.id,
                    'text': str(status.text),
                    'time': status.created_at
                }


            print(f'New tweet arrived: {tweet["text"]}')

            query_temp = "INSERT INTO tweets VALUES (%s, %s, %s, %s);"

            try:
                if 'scholz' in (tweet["text"]).lower():
                    engine.execute(query_temp, (tweet["id"], tweet["time"], 'scholz', tweet["text"]))
                if 'habeck' in (tweet["text"]).lower():
                    engine.execute(query_temp, (tweet["id"], tweet["time"], 'habeck', tweet["text"]))
                if 'laschet' in (tweet["text"]).lower():
                    engine.execute(query_temp, (tweet["id"], tweet["time"], 'laschet', tweet["text"]))
            except ValueError:
                logging.critical('Not able to save tweet.Pass!')
            except Exception as e:
                print(e, ' - trying to reconnect and retry')
                new_engine = create_engine(conn_string, echo=False)
                
                if 'scholz' in (tweet["text"]).lower():
                    new_engine.execute(query_temp, (tweet["id"], tweet["time"], 'scholz', tweet["text"]))
                if 'habeck' in (tweet["text"]).lower():
                    new_engine.execute(query_temp, (tweet["id"], tweet["time"], 'habeck', tweet["text"]))
                if 'laschet' in (tweet["text"]).lower():
                    new_engine.execute(query_temp, (tweet["id"], tweet["time"], 'laschet', tweet["text"]))


    def on_error(self, status):
        if status == 420:
            print(f'Erro ocurred! Stop stream - {time.asctime(time.localtime(time.time()))}')
            return False



if __name__ == '__main__':
    api = authenticate()
    listener = TweetsListener()
    stream = Stream(auth = api.auth, listener = listener, tweet_mode='extended')
    stream.filter(track=['habeck','scholz','laschet'], 
        languages=['de'], 
        is_async=True, 
        encoding='utf-8', 
        filter_level='low',
        stall_warnings=True)

