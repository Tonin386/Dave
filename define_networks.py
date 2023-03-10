from rssi import RSSI_Scan, RSSI_Localizer
import re
import os
import time
import json
from copy import deepcopy
import pprint

def scan_networks():
	interface = "wlp0s20f3"
	scanner = RSSI_Scan(interface)

	scanner.getRawNetworkScan(True)
	scanner.getRawNetworkScan(True)
	scanner.getRawNetworkScan(True)
	scanner.getRawNetworkScan(True)
	scanner.getRawNetworkScan(True)
	raw_data = scanner.getRawNetworkScan(True)["output"]
	raw_cells = raw_data.decode().split("Cell")
	raw_cells = raw_cells[1:]

	collected_data = []
	addresses = []

	for c in raw_cells:
		lines = c.split("\n")
		network_address = re.sub(r"^.*Address: ", "", lines[0])
		network_ssid = re.sub("^.*ESSID:", "", lines[5]).replace('"', '')

		# print("%s %d" % (network_address, signal_level_value))
		network_data = {
			"address": network_address,
			"ssid": network_ssid,
		}
		if not "\\x00" in network_ssid:
			collected_data.append(network_data)


	collected_data.sort(key=lambda d: d['address'])
	for i in range(len(collected_data)):
		print(i, collected_data[i])

	return collected_data

def save_data(data):
	path = "networks.json"

	json_string = json.dumps(data, indent=4)
	with open(path, "w") as file:
		file.write(json_string)


save_data(scan_networks())