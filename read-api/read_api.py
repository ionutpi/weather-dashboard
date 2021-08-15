import requests
import pandas as pd
from prefect import task, Task, Flow

f = open("api-key.txt","r")
lines = f.readlines()
api_key = lines[0]

station = '06184'
period = 'latest-hour'
url = ' https://dmigw.govcloud.dk/v2/metObs/collections/observation/items'


@task
def read_api(url: str, station: str, period: str) -> dict:
    r = requests.get(url, params={'api-key': api_key, 'stationId': station, 'period': period})
    raw_data = r.json()
    return raw_data

@task
def process_raw_data(raw_data: dict) -> pd.DataFrame:
    features = raw_data["features"]
    data = [item["properties"] for item in features]
    df = pd.DataFrame(data)
    return df

@task 
def process_df(df):
    df.groupby('parameterId').mean().to_csv('data.csv')

with Flow("weather data") as flow:
    data = read_api(url, station, period)
    df = process_raw_data(data)
    process_df(df)

state = flow.run()
print(state)