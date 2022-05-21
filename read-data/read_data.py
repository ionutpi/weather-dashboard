import requests
import pandas as pd
from datetime import timedelta, datetime
from prefect import task, Task, Flow
from prefect.schedules import IntervalSchedule
from sqlalchemy import create_engine

f = open("api-key.txt","r")
lines = f.readlines()
api_key = lines[0]

station = '06080'
period = 'latest-hour'
url = 'https://dmigw.govcloud.dk/v2/metObs/collections/observation/items'


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
    df['created'] = pd.to_datetime(df['created'])
    df['observed'] = pd.to_datetime(df['observed'])
    return df

@task(max_retries=3, retry_delay=timedelta(seconds=30))
def process_df(df):
    engine = create_engine('mysql+mysqlconnector://testuser:testpassword@db/dash')
    df.to_sql('weather', engine, index=False, if_exists='append')
    print("write df")

schedule = IntervalSchedule(
    start_date=datetime.utcnow() + timedelta(seconds=1),
    interval=timedelta(hours=1)
    )

with Flow("weather data", schedule) as flow:
    data = read_api(url, station, period)
    df = process_raw_data(data)
    process_df(df)

state = flow.run()
print(state)