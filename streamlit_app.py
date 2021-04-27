import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import db_config
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# Connect to AWS RDS Postgresql DB
HOST = db_config.host 
PORT = db_config.port
USERNAME = db_config.username
PASSWORD = db_config.password
DB = db_config.db

conn_string = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'
engine = create_engine(conn_string, echo=False)

# Read in sentiment_score table
scores = pd.read_sql('sentiment_score',engine)

# Create data column
scores['date'] = scores['created_at'].dt.date

# Only select tweets from April 13 and onwards
scores = scores[scores['date']>=datetime.date(2021, 4, 13)]

# Group by date and name to obtain daily mean score and daily count
score_daily = scores.groupby(['date','name']).mean()
count_daily = scores.groupby(['date','name']).count()

# Merge both DFs
merged = score_daily.merge(count_daily,left_index=True,right_index=True).reset_index(level='name')
merged['score_x'] = round(merged['score_x'],2)


# Define Series based on name
laschet = merged[merged['name']=='laschet']
habeck = merged[merged['name']=='habeck']
scholz = merged[merged['name']=='scholz']
x = laschet.index

# Function to return n last tweets 
def get_last_tweets(num=3,name=None):
    if name == 'Habeck':
        df = scores[scores['name']=='habeck']
    elif name == 'Laschet':
        df = scores[scores['name']=='laschet']
    elif name == 'Scholz':
        df = scores[scores['name']=='scholz']
    else:
        df = scores
    
    last_tweets = df.iloc[-num:][['created_at','text','score']]

    return last_tweets


# Configuration of streamlit front-end
st.set_page_config(page_title="Tweet Race", layout="wide", page_icon='💬')

st.title('💬 Tweeted sentiments in German politics')

st.subheader("A sentiment analysis for a daily collection of tweets regarding three German politicians.")
st.text("")

# Creating plotly chart
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(x=x, y=laschet['score_x'],
                    mode='lines+markers',
                    name='Laschet', line=dict(color='black')),secondary_y=False)

fig.add_trace(go.Scatter(x=x, y=habeck['score_x'],
                    mode='lines+markers',
                    name='Habeck',line=dict(color='green')),secondary_y=False)

fig.add_trace(go.Scatter(x=x, y=scholz['score_x'],
                    mode='lines+markers', name='Scholz',line=dict(color='red')),secondary_y=False)

fig.add_trace(go.Bar(x=x, y=laschet['score_y'],name='Laschet',
                     marker_color='black',opacity=0.5),secondary_y=True)

fig.add_trace(go.Bar(x=x, y=habeck['score_y'],name='Habeck',
                     marker_color='green',opacity=0.5),secondary_y=True)

fig.add_trace(go.Bar(x=x, y=scholz['score_y'],name='Scholz',
                     marker_color='red',opacity=0.5),secondary_y=True)

fig.update_layout(template='simple_white',title='Daily Sentiment Scores',
                  xaxis_title='Date', yaxis_title='Sentiment Score',
                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

fig.update_layout(font=dict(family="Verdana",color="#666666"))
fig.update_xaxes(linecolor="#666666")
fig.update_yaxes(linecolor="#666666")
fig.update_yaxes(title_text="Total tweets collected", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

# Creating Expander with Explanation and References
with st.beta_expander("Display last collected tweets"):
    col01,col02 = st.beta_columns([1,3])
    with col01:
        name = st.radio(label='Last tweet for:', options=['All','Habeck','Laschet','Scholz'], index=0)
    with col02:
        last = get_last_tweets(name=name)

        for i in last.values:
                st.write(f'{i[1]}')
                st.write(f'Time: {i[0]} | Score: {i[2]}')

with st.beta_expander("Explanation"):
    st.markdown("""
    The program streams tweets containing the selected politician names within the rate limit of the Twitter API. Collected tweets are processed to remove URLs and @ mentionings.
    In order to deduct the sentiment corresponding to the tweet a pretrained 'BERT' model was fine-tuned with a data set of 850 labeled tweets and a validation data set of 150 tweets.
    'BERT' stands for Bidirectional Encoder Representations from Transformers and is a Natural Language Processing Model proposed by researchers at Google Research in 2018. It uses two steps, pre-training and fine-tuning. 
    Due to its unified architecture across different downstream tasks it can be fine-tuned for a variety of final tasks that might not be similar to the task the model was trained on.

    The achieved scores for the validation data set as well as the confusion matrix are shown below. The model returns a value of _+1_ for a positive sentiment, a _-1_ for a negative sentiment and a _0_ for a neutral sentiment.
    The displayed Sentiment Score is the mean of this score per day.
    """)
    col1, col2, col3,col4,col5 = st.beta_columns(5)
    
    with col2:
        st.subheader('')
        st.markdown('METRICS:')
        st.text('Accuracy: 0.66')
        st.text('F1-Score: 0.65')
    with col3:
        st.image('confusion_matrix.png',use_column_width='false')
        

with st.beta_expander("References"):
    st.text("""
    BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
    J. Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova - Computer Science - NAACL-HLT - 2019


    Training a Broad-Coverage German Sentiment Classification Model for Dialog Systems
    Guhr, Oliver  and  Schumann, Anne-Kathrin  and  Bahrmann, Frank  and  Böhme, Hans Joachim - Proceedings of The 12th Language Resources and Evaluation Conference - 2020


    BERT Fine-Tuning Tutorial with PyTorch.
    Chris McCormick and Nick Ryan. (2019, July 22). Retrieved from http://www.mccormickml.com


    https://towardsdatascience.com/keeping-up-with-the-berts-5b7beb92766
    """)
    



