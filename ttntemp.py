# %%
import sys
import datetime
import argparse
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
import requests
import secrets

from requests.exceptions import HTTPError

argparser = argparse.ArgumentParser(description="Graph temperature measurements.")
argparser.add_argument("--file", nargs='?', type=str, help="path to file containing json list of measurements")
args = argparser.parse_args()
inputPath = args.file

if inputPath is not None:
    temperatureDataFrame = pd.read_json(inputPath)
else:
    # Call api
    try:
        secrets = secrets.Secrets()
        response = "asdf"
        response = requests.get(secrets.dataApiUrl,
            headers={'Accept': 'application/json', 'Authorization': secrets.authorizationKey},)
        response.raise_for_status()
        temperaturesAsJson = response.json()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        exit()
    except Exception as err:
        print(f'Other error occurred: {err}')
        exit()
    else:
        print('Success!')
        temperatureDataFrame = pd.DataFrame.from_dict(temperaturesAsJson)

# Initialise a figure. subplots() with no args gives one plot.
fig, axs = plt.subplots(sharex="all", sharey="all")

temperatureDf = temperatureDataFrame[temperatureDataFrame.tempc1 != -127][temperatureDataFrame.tempc2 != -127]
temperatureDf["datetime"] = pd.to_datetime(temperatureDf["time"])
print(temperatureDf.head())

groupedByDeviceIdDf = temperatureDf[["device_id", "tempc1", "tempc2", "datetime"]].groupby("device_id")
print(groupedByDeviceIdDf.head())

for name, group in groupedByDeviceIdDf:
    group.plot(x="datetime", y="tempc1", ax=axs, label=str("%s: Temp 1" % (name)))
    group.plot(x="datetime", y="tempc2", ax=axs, label=str("%s: Temp 2" % (name)))

timespan = temperatureDf["datetime"].max() - temperatureDf["datetime"].min()
print(timespan)

hours, remainder = divmod(timespan.total_seconds(), 3600)
minutes, seconds = divmod(remainder, 60)

axs.set_title(str("Room temperature last %dH, %dM" % (hours, minutes)))
plt.xlabel("Hour of day")
plt.ylabel("Temperature")
plt.legend()

# Ask Matplotlib to show the plot
plt.show()