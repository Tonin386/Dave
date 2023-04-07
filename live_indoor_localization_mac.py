import re
import os
import time
from copy import deepcopy
import pprint
import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from random import randint

labels = ["C201", "C203", "C204", "C205", "C206", "C207", "C208", "C210", "DC", "MC"]

def most_frequent(List):
    return max(set(List), key = List.count)

def load_networks():
	data = pd.read_csv("cleaned_data.csv")
	return list(data.columns)[:-1]

def load_random_acquisition():
	data = pd.read_csv("cleaned_data_raw.csv")
	return list(data.values[randint(0, len(data))])

def scan_networks(networks):
	raw_data = os.popen("sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s").read()
	raw_cells = raw_data.split("\n")
	raw_cells = raw_cells[1:-1]

	collected_data = []
	addresses = []

	for line in raw_cells:

		network_address = ""
		signal_level_text = ""
		signal_level_value = ""
		network_ssid = ""

		i = 0
		while line[i] == " ":
			i += 1

		while line[i] != " ":
			network_ssid += line[i]
			i += 1


		while line[i] == " ":
			i += 1

		while line[i] != " ":
			network_address += line[i].upper()
			i += 1


		while line[i] == " ":
			i += 1

		while line[i] != " ":
			signal_level_text += line[i]
			i += 1

		success = False
		try:
			signal_level_value = int(signal_level_text)
			success = True
		except:
			continue

		# print("%s %d" % (network_address, signal_level_value))
		if success:
			network_data = {
			"address": network_address,
			"signalStrength": signal_level_value
			}
			if not network_address in addresses:
				addresses.append(network_address)
				collected_data.append(network_data)

	for i in range(len(networks)):
		if not networks[i] in addresses:
			network_data = {
				"address": networks[i],
				"signalStrength": None
			}
		if not network_address in addresses:
			addresses.append(network_address)
			collected_data.append(network_data)

	for i in range(len(networks)):
		if not networks[i] in addresses:
			network_data = {
				"address": networks[i],
				"signalStrength": -95
			}
			collected_data.append(network_data)

	collected_data.sort(key=lambda d: d['address'])
	# for i in range(len(collected_data)):
	# 	print(i, collected_data[i])

	return collected_data

def clear_data(data, networks):
	c_data = [np.nan] * len(networks)
	for d in data:
		if d["address"] in networks:
			c_data[networks.index(d["address"])] = d["signalStrength"]

	print(c_data)

	return c_data


model = pickle.load(open("model_raw.sav", "rb"))
scaler = pickle.load(open("scaler.sav", "rb"))
networks = load_networks()

# for i in range(10):
# 	data = load_random_acquisition()
# 	print(data[-1])
# 	data_test = [data[:-1]] * 5
# 	df = pd.DataFrame(data_test, columns=networks)
# 	x_test = scaler.transform(df)
# 	results = model.predict(x_test)
# 	print(results)

print("Initialisation...")
for i in range(3):
	scan_networks(networks)

print("Acquisition des données...")

acquisition_data = []
st = time.time()
for k in range(10):
	data = scan_networks(networks)
	acquisition_data.append(clear_data(data, networks))
	print("%d/10" % (k+1))

et = time.time()
elapsed = et - st
df = pd.DataFrame(acquisition_data, columns=networks)
print("Exec time: %f seconds" % elapsed)
x_test = scaler.transform(df)
print(x_test)
results = model.predict(x_test)
print(results)
print("Vous vous trouvez en", labels[int(most_frequent(list(results)))])