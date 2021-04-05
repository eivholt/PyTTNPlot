# %%
import sys
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
import datetime
import requests
import secrets

from requests.exceptions import HTTPError

print(f"Name of the script      : {sys.argv[0]}")
print(f"Arguments of the script : {sys.argv[1:]}")

# Initialise a figure. subplots() with no args gives one plot.
fig, axs = plt.subplots(sharex="all", sharey="all")

# Call api
try:
    secrets = secrets.Secrets()
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
    temperatureDataFrame = pd.DataFrame.from_dict(temperaturesAsJson) #pd.read_json(temperaturesAsJson)

#with open('ttn.json') as jsonFile:
#    deviceDataDict = json.load(jsonFile) 
#temperatureDataFrame = pd.DataFrame(deviceDataDict)

temperatureDf = temperatureDataFrame[temperatureDataFrame.tempc1 != -127][temperatureDataFrame.tempc2 != -127]
temperatureDf["datetime"] = pd.to_datetime(temperatureDf["time"])

groupedByDeviceIdDf = temperatureDf[["device_id", "tempc1", "tempc2", "datetime"]].groupby("device_id")

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