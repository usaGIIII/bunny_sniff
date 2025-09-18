#!/usr/bin/env python3
# // Script for wifi configuration on pi via ssh, or anything on ssh for that matter
#    Ensure that you have wireless_tools installed (arch) or at least iwlist - mainly for pi project

# // Imports
import os
import subprocess
import re
import sys

# Functionality

# Get Network Interfaces: 

def get_network_interfaces():
    """Function that gets network interface from user and returns it"""
    print("// Interfaces:")
    os.system("ip route list")
    interface = input("// Please input network interface: ")
    return interface
# Get available networks: 

def get_networks(interface):
    """Function that returns the available WiFi networks """
    print("// WiFi Network Scan Commencing...")
    # Start sub-process that attempts to scan networks 
    try:
        scan_results = subprocess.check_output(["sudo", "iwlist", interface, "scan"], universal_newlines=True)
        # Extract the SSIDs from the scan results: 
        available_networks = re.findall(r'ESSID:"([^"]*)', scan_results)

        # Perform check to ensure unique networks only are returned
        unique_networks = []
        for network in available_networks:
            if network and network not in unique_networks:
                unique_networks.append(network)
        return unique_networks

    except Exception as e:
        print(f"// Error during network scan: {e}")

# Select Network:
def select_network(networks):
    if not networks: 
        print("// No Networks found...")
        return None
    print("\n// Available Networks:\n")
    for i, network in enumerate(networks, 1):
        print(f"    {i}: {network}")

    while True:
        try:
            choice = int(input("\n Select Network:"))
            if 1 <= choice <= len(networks):
                return networks[choice -1]
            else: 
                print("// Invalid Selection..Try Again:")
        except ValueError as e:
            raise e


def select_configuration_type():
    choice = input("// Do you want to connect via config file?")
    if choice == "Y":
        configure_network_from_file()
    else: 
        print("// Available Networks:")
        os.system("nmcli dev wifi list")
        ssid = input("// Please input desired SSID")
        configure_network(ssid)

# WiFi network configuration

def configure_network(ssid, password=None):
    # Configure the device to connect to a specific network:
    if not password:
        password = input("// Input Network Password: \n")

    # Need to provide the path to wpa_supplicant.conf - this is where we store our chosen network details
    wpa_supplicant_path = "/etc/wpa_supplicant/wpa_supplicant.conf"
    #first_run = input("// Do you want to create a new wpa_supplicant.conf file? Y/n: ")
    # Make sure that we have a backup of our previous conf - dev idea - we can save these to connect to known networks @ a later time

    #if first_run == "Y":
     #   create_config_cmd = f"sudo touch {wpa_supplicant_path}"

    print("// Creating backup config file")
    backup_cmd = f"sudo cp {wpa_supplicant_path} {wpa_supplicant_path}.bak"
    # Then execute the command using the os lib: 
    os.system(backup_cmd)
        
    # Creating the configuration template: - Need to write something that checks if this file is present in the first place
    network_config = f'''ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev update_config=1
country=UK
network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
'''
    print(network_config)
    # We then want to write this configuration to a temp file: 
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
        f.write(network_config)

# Restart networking
    choice = input("// Do you want to restart WiFi & reconnect? Y/n: ")
    if choice == "Y":
        os.system("sudo systemctl restart wpa_supplicant")
        os.system("sudo wpa_cli -i wlan0 reconfigure")
    else:
        print("// Config Updated...")
def configure_network_from_file():
    """
    A function that configures network based on predefined config files:
    """
    print("// Available Network Configs")
    # Show available configuraiton files:
    os.system("nmcli connection show")
    chosen_config = input("// Please input selected config file name: ")
    print(f"// Loading: {chosen_config}, if you are on ssh you may beed to reconnect on the new network")
    config_command = f"sudo nmcli connection up id {chosen_config}"
    os.system(config_command)
    os.system("nmcli dev wifi list")
if __name__ == "__main__":
    # We want to put an option in here so that we can select what option that we want (config, or select new connection)
    interface = get_network_interfaces()
    x = get_networks(interface)
    y = select_network(x)
    #configure_network(y)
    select_configuration_type()

