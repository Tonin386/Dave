from rssi import RSSI_Scan, RSSI_Localizer
import re
import os
import time
from copy import deepcopy
import pprint
import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

import numpy as np
from random import randint

labels = ["C201", "C203", "C204", "C205", "C206", "C207", "C208", "C210", "DC", "MC"]

C201 = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
C203 = [[0, 1, 0, 0, 0, 0, 0, 0, 0, 0]]
C204 = [[0, 0, 1, 0, 0, 0, 0, 0, 0, 0]]
C205 = [[0, 0, 0, 1, 0, 0, 0, 0, 0, 0]]
C206 = [[0, 0, 0, 0, 1, 0, 0, 0, 0, 0]]
C207 = [[0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]
C208 = [[0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]
C210 = [[0, 0, 0, 0, 0, 0, 0, 1, 0, 0]]
DC = [[0, 0, 0, 0, 0, 0, 0, 0, 1, 0]]
MC = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]

def most_frequent(List):
    return max(set(List), key = List.count)

def load_networks():
	data = pd.read_csv("cleaned_data.csv")
	return list(data.columns)[:-1]

def load_random_acquisition():
	data = pd.read_csv("cleaned_data_raw.csv")
	return list(data.values[randint(0, len(data))])

def scan_networks(networks):
	interface = "wlp0s20f3"
	scanner = RSSI_Scan(interface)

	raw_data = scanner.getRawNetworkScan(True)["output"]
	raw_cells = raw_data.decode().split("Cell")
	raw_cells = raw_cells[1:]

	collected_data = []
	addresses = []

	for c in raw_cells:
		lines = c.split("\n")
		network_address = re.sub(r"^.*Address: ", "", lines[0])
		signal_level_text = re.sub("^.*Signal level=", "", lines[3])
		signal_level_value = int(signal_level_text.replace(" dBm ", ""))

		# print("%s %d" % (network_address, signal_level_value))
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


model = pickle.load(open("model_nn.sav", "rb"))
scaler = pickle.load(open("scaler_raw.sav", "rb"))
networks = load_networks()

print("Acquisition des données...")

acquisition_data = []
st = time.time()
data = scan_networks(networks)
acquisition_data.append(clear_data(data, networks))

et = time.time()
elapsed = et - st
df = pd.DataFrame(acquisition_data, columns=networks)
# x_test = scaler.transform(df)
x_test = df.values.tolist()
print(x_test)
# results = model.predict(x_test)
_, results = model.evaluate(x_test, C201)
print("C201", results)
_, results = model.evaluate(x_test, C203)
print("C203", results)
_, results = model.evaluate(x_test, C204)
print("C204", results)
_, results = model.evaluate(x_test, C205)
print("C205", results)
_, results = model.evaluate(x_test, C206)
print("C206", results)
_, results = model.evaluate(x_test, C207)
print("C207", results)
_, results = model.evaluate(x_test, C208)
print("C208", results)
_, results = model.evaluate(x_test, C210)
print("C210", results)
_, results = model.evaluate(x_test, DC)
print("DC", results)
_, results = model.evaluate(x_test, MC)
print("MC", results)
# print("Vous vous trouvez en", labels[int(most_frequent(list(results)))])
