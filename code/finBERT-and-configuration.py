from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
import pandas as pd
import datetime as dt
import datedelta
import yfinance as yf
import alpaca_trade_api as tradeapi
import os

# Setting up Alpaca api

ENDPOINT = 'https://api.alpaca.markets'
KEY = 'Contact ntcherev for details'
SECRET_KEY = 'Contact ntcherev for details'

api = tradeapi.REST(key_id=KEY, secret_key=SECRET_KEY, 
                    base_url=ENDPOINT, api_version='v2')

# Access to the finBERT model

finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer)

# helper variables and dataframe initialization

directory = 'out-text-analysis'
iter = 0
format = ' %B %d, %Y.'
invalid_days = set([5, 6, 0])

final_df=pd.DataFrame(columns = ['TIC','cur_price','old_price', 'new_price', 'old_week_price', 'new_week_price',
                                  'date', 'posRel', 'negRel', 'pos', 'neg', 'sector', 'industry', 'beta', 'mktcap'] )

# iterate through every file in the directory

for filename in os.listdir(directory):
    print(iter)

    try:
        f = os.path.join(directory, filename)
        a_file = open(f)
        file_contents = a_file.read()
        
        contents_split = file_contents.splitlines()
        ticker = contents_split[-1].split(' ')[1]

        sentences = ' '.join(contents_split[13:]).split(".")

      # Make sure that the returns from surrounding dates of the earning call fall on valid trading days to avoid issues with Alpaca

        date = dt.datetime.strptime(contents_split[8].split('ending')[1], format)
        if date.weekday() in invalid_days:
            date = date + 3*datedelta.DAY
        cur_date = date.strftime("%Y-%m-%d")
        month_back = date - datedelta.MONTH

        if month_back.weekday() in invalid_days:
            month_back = month_back + 3*datedelta.DAY

        week_back = date - datedelta.WEEK
        if week_back.weekday() in invalid_days:
            week_back = week_back + 3*datedelta.DAY

        week_forward = date + datedelta.WEEK
        if week_forward.weekday() in invalid_days:
            week_forward = week_forward+ 3*datedelta.DAY


        month_forward = date + datedelta.MONTH
        if month_forward.weekday() in invalid_days:
            month_forward = month_forward + 3*datedelta.DAY

        month_back_str = month_back.strftime("%Y-%m-%d")
        month_forward_str = month_forward.strftime("%Y-%m-%d")
        week_forward_str = week_forward.strftime("%Y-%m-%d")
        week_back_str = week_back.strftime("%Y-%m-%d")


        week_back_price = api.get_bars(ticker, '1Day', week_back_str, week_back_str, adjustment='raw').df.close[0]
        week_forward_price = api.get_bars(ticker, '1Day', week_forward_str, week_forward_str, adjustment='raw').df.close[0]
        month_back_price = api.get_bars(ticker, '1Day', month_back_str, month_back_str, adjustment='raw').df.close[0]
        month_forward_price = api.get_bars(ticker, '1Day', month_forward_str, month_forward_str, adjustment='raw').df.close[0]
        call_price = api.get_bars(ticker, '1Day', cur_date, cur_date, adjustment='raw').df.close[0]

        print('Prices loaded')

        # Calculate our sentiment scores from FinBERT analysis
      
        results = nlp(sentences)

        num = len(results)
        positive = 0

        neutral = 0
        negative = 0
        for sentence in results:
            if sentence['label'] == 'Neutral':
                neutral = neutral + 1
            elif sentence['label'] == 'Positive':
                positive = positive + 1
            else:
                negative = negative + 1
                
        negative_rel = negative/num
        positive_rel = positive/num

        print("Sentiment worked!")

       # Pull metadata from yfinance
      
        try:
            yfinfo = yf.Ticker(ticker)
            sector = yfinfo.info['sector']
            industry = yfinfo.info['industry']
            mktcap = yfinfo.info['marketCap']
            beta = yfinfo.info['beta']
            print('Metadata secured')

        except:
            print('Metadata failed')
            sector = 'NA'
            industry = 'NA'
            mktcap = -9999
            beta = -9999

        final_df.loc[len(final_df.index)] = [ticker, call_price, month_back_price,
                                        month_forward_price, week_back_price, week_forward_price,cur_date, positive_rel, negative_rel,
                                        positive, negative, sector, industry, beta, mktcap]

        print(ticker + " worked! " + str(iter) + " Done")


    except Exception as e:
        print(e)
        print(str(iter) + " failed!")
    
    iter += 1

# Save final dataframe
        
final_df.to_csv('finalData.csv')
