from rssi import RSSI_Scan, RSSI_Localizer
import re
import os
import time

zone_label = "B208"
zone_index = 0
# networks_ssid = [] #Put the names of the networks that interest us.
networks_address = [""] #Put the IPv6 adresses of the networks that interest us.

def scan_networks():
	interface = "wlp0s20f3"
	scanner = RSSI_Scan(interface)

	raw_data = scanner.getRawNetworkScan()["output"]
	raw_cells = raw_data.decode().split("Cell")
	raw_cells = raw_cells[1:]
	print(len(raw_cells))

	collected_data = []

	for c in raw_cells:
		lines = c.split("\n")
		network_address = re.sub(r"^.*Address: ", "", lines[0])
		signal_level_text = re.sub("^.*Signal level=", "", lines[3])
		signal_level_value = int(signal_level_text.replace(" dBm ", ""))
		network_ssid = lines[5].replace("ESSID:", "").replace('"', '')

		print("%s %d" % (network_address, signal_level_value))
		network_data = {
			"ssid": network_ssid,
			"address": network_address,
			"signalStrength": signal_level_value
		}
		collected_data.append(network_data)

	return collected_data

def save_data(d):
	print("TODO")

for i in range(3):
	data = scan_networks()
	for d in data:
		if d["address"] in networks_address:
			save_data(d)

	if i == 2:
		break
	print("Waiting 5 seconds before the next measure...")
	time.sleep(5)


