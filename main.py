import os 
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, PHONE_NUMBER, API_KEY_WAPI
import time

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from datetime import datetime

query = 'London'
api_key = API_KEY_WAPI

url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={query}&days=1&aqi=no&alerts=no'

response = requests.get(url).json()
# response.keys()
# response['forecast']['forecastday'][0].keys()
# len(response['forecast']['forecastday'][0]['hour'])
# response['forecast']['forecastday'][0]['hour'][1]

def get_forecast(response, i):
    forecast = response['forecast']['forecastday'][0]['hour'][i]
    date = forecast['time'].split()[0]
    hour = int(forecast['time'].split()[1].split(':')[0])
    condition =forecast['condition']['text']
    temperature = forecast['temp_c']
    rain = forecast['will_it_rain']
    chance_of_rain = forecast['chance_of_rain']

    return date, hour, condition, temperature, rain, chance_of_rain


data = []

for i in tqdm(range(len(response['forecast']['forecastday'][0]['hour'])), colour='green'):
    data.append(get_forecast(response, i))


col = ['Date', 'Hour', 'Condition', 'Temperature', 'Rain', 'Chance_of_rain']

df = pd.DataFrame(data, columns=col)
df = df.astype({'Hour':'int'})
df_rain = df[(df['Rain'] == 1) & (df['Hour'] > 6 ) & (df['Hour'] < 22)]
df_rain = df_rain[['Hour', 'Condition']]
df_rain.set_index('Hour', inplace= True)

sms_template = f"""\nHello! \n\n\nThis is a test Date {df['Date'][0]} City {query} \n\n\n {str(df_rain)}"""

print(sms_template)

time.sleep(2)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

message = client.messages \
                .create(
                    body=sms_template,
                    from_=PHONE_NUMBER,
                    to='+527713295667'
                )

print('Message sent' + message.sid)