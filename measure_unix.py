from rssi import RSSI_Scan, RSSI_Localizer
import re
import os
import time
import json
from copy import deepcopy

zone_label = input("Enter zone label: ")
zone_index = int(input("Enter zone index: "))
# networks_ssid = [] #Put the names of the networks that interest us.
networks_address = ["C0:25:5C:69:42:E4", "C0:25:5C:69:42:E9", "C0:25:5C:69:42:ED", "C0:25:5C:69:42:E3", "C0:25:5C:69:42:E1", "C0:25:5C:69:42:EE"] #Put the IPv6 adresses of the networks that interest us.
print("You will need to make 20 measures. Every time you will need to move, you'll be asked so.")
position = int(input("Please input the original position. Measurement will start once you pressed enter: "))
if position < 0:
	position = 0

def scan_networks():
	interface = "wlp0s20f3"
	scanner = RSSI_Scan(interface)

	raw_data = scanner.getRawNetworkScan(True)["output"]
	raw_cells = raw_data.decode().split("Cell")
	raw_cells = raw_cells[1:]

	collected_data = []

	for c in raw_cells:
		lines = c.split("\n")
		network_address = re.sub(r"^.*Address: ", "", lines[0])
		signal_level_text = re.sub("^.*Signal level=", "", lines[3])
		signal_level_value = int(signal_level_text.replace(" dBm ", ""))
		network_ssid = re.sub("^.*ESSID:", "", lines[5]).replace('"', '')

		# print("%s %d" % (network_address, signal_level_value))
		network_data = {
			"ssid": network_ssid,
			"address": network_address,
			"signalStrength": signal_level_value
		}
		collected_data.append(network_data)

	return collected_data

def save_data(data, position, acquisition):
	path = "data/%s/%d/%d.json" % (zone_label, position, acquisition)
	os.makedirs(os.path.dirname(path), exist_ok=True)

	ordered_data = {}
	for d in data:
		if d["address"] in ordered_data.keys():
			ordered_data[d["address"]]["signalStrength"].append(d["signalStrength"])
		else:
			ordered_data[d["address"]] = {}
			ordered_data[d["address"]]["signalStrength"] = [d["signalStrength"]]
			ordered_data[d["address"]]["ssid"] = d["ssid"]

	json_string = json.dumps(ordered_data, indent=4)
	with open(path, "w") as file:
		file.write(json_string)

def clear_data(data):
	c_data = deepcopy(data)
	for d in data:
		if not d["address"] in networks_address:
			c_data.remove(d)

	return c_data

for i in range(20):
	for j in range(1):
		acquisition_data = []
		st = time.time()
		for k in range(50):
			data = scan_networks()
			acquisition_data.extend(clear_data(data))
			print("%d/50" % (k+1))

		et = time.time()
		elapsed = et - st
		print("Exec time: %f seconds" % elapsed)
		save_data(acquisition_data, position, j)
		if j == 2:
				break
		print("Waiting 5 seconds before acquisition #%d..." % (j+1))
		time.sleep(5)
	position += 1
	input("Press enter once you're ready to do measure #%d" % position)