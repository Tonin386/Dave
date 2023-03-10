import os
import time
import json
from copy import deepcopy

zone_label = input("Enter zone label: ")
zone_index = int(input("Enter zone index: "))
networks_ssid = ["UTT", "jpoUTT", "cordeesUTT", "UTTetudiants", "UTTpersonnels", "UTTpersonnels"] #Put the names of the networks that interest us.
networks_address = ["C0:25:5C:69:42:E4", "C0:25:5C:69:42:E9", "C0:25:5C:69:42:ED", "C0:25:5C:69:42:E3", "C0:25:5C:69:42:E1", "C0:25:5C:69:42:EE"] #Put the IPv6 adresses of the networks that interest us.
print("You will need to make 20 measures. Every time you will need to move, you'll be asked so.")
position = int(input("Please input the original position. Measurement will start once you pressed enter: "))
if position < 0:
	position = 0

def scan_networks():
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
				"ssid": network_ssid,
				"address": network_address,
				"signalStrength": signal_level_value
			}
			collected_data.append(network_data)
		if not network_address in addresses:
			addresses.append(network_address)

	for i in range(len(networks_address)):
		if not networks_address[i] in addresses:
			network_data = {
				"address": networks_address[i],
				"ssid": networks_ssid[i],
				"signalStrength": 0
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