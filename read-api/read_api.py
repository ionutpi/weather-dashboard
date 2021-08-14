import requests
import pandas as pd

f = open("api-key.txt","r")
lines = f.readlines()
api_key = lines[0]

station = '06184' # 6187 
start_datetime='2021-08-14T00:00:00Z/..'  # 'datetime': start_datetime
period = 'latest-hour'

url = ' https://dmigw.govcloud.dk/v2/metObs/collections/observation/items' # url for the current api version
r = requests.get(url, params={'api-key': api_key, 'stationId': station, 'period': period}) # Issues a HTTP GET request
json = r.json()
features = json["features"]

data = [item["properties"] for item in features]

df = pd.DataFrame(data)
print(df)
print(df.groupby('parameterId').count())
print(df.groupby('parameterId').mean())