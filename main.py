import os
import requests
import xmltodict
from dotenv import load_dotenv
from models import Device
import pandas as pd

def check_response(result_dict):
    """
    Check if the response in the result dictionary is successful.

    Args:
        result_dict (dict): The dictionary containing the response.

    Returns:
        bool: True if the response is successful, False otherwise.
    """
    is_successful_response = False
    response = result_dict.get('response', {})
    if response.get('@status') == 'success':
        is_successful_response = True
    return is_successful_response

def get_api_key(result_dict):
    """
    Retrieves the API key from the given result dictionary.

    Args:
        result_dict (dict): The dictionary containing the API response.

    Returns:
        str or None: The API key if it exists in the result dictionary, None otherwise.
    """
    if check_response(result_dict):
        # Check if the 'result' key exists in the response
        return result_dict['response']['result'].get('key')
    return None

def get_full_url(ip, uri, api_key=None):
    """Construct the full URL based on the IP, URI, and API key."""
    if api_key is None:
        return f'https://{ip}{uri}'
    return f"https://{ip}/api/?type=op&cmd={uri}&key={api_key}"
    
def get_response(url):
    """
    Sends a GET request to the specified URL and returns the parsed XML response as a dictionary.

    Args:
        url (str): The URL to send the GET request to.

    Returns:
        dict: The parsed XML response as a dictionary, or None if the request failed.

    Raises:
        requests.exceptions.RequestException: If the GET request fails.

    """
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        result_dict = xmltodict.parse(response.text)
        if check_response(result_dict):
            return result_dict
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return None

def save_to_txt(result_dict, filename='output.txt'):
    """
    Save a dictionary to a text file in JSON format.

    Args:
        result_dict (dict): The dictionary to be saved.
        filename (str, optional): The name of the output file. Defaults to 'output.txt'.
    """
    import json
    with open(filename, 'w') as f:
        json.dump(result_dict, f, indent=4)

def process_device_info(info):
    """
    Process device information and create a new Device object.

    Args:
        info (list): A list of dictionaries containing device information.

    Returns:
        Device: A new Device object with the processed information.

    """
    new_device = None

    for item in info:
        if isinstance(item, dict):
            system_info = item.get('system')
            
            if system_info:
                new_device = Device(
                    system_info.get('hostname'), system_info.get('model'), system_info.get('serial'),
                    system_info.get('ip-address'), system_info.get('sw-version'),
                    system_info.get('global-protect-client-package-version'), system_info.get('app-version'),
                    system_info.get('av-version'), system_info.get('threat-version'),
                    system_info.get('wildfire-version'), system_info.get('url-filtering-version'),
                    system_info.get('device-certificate-status')
                )
            licenses_info = item.get('licenses')
            if licenses_info:
                licenses = licenses_info.get('entry', [])
                for license in licenses:
                    if new_device:  # Ensure new_device is defined before calling add_license
                        new_device.add_license(license.get('feature'), license.get('issued'), license.get('expired'))
    return new_device

def save_to_excel(devices, filename='output.xlsx'):
    """
    Save device information to an Excel file.

    Args:
        devices (list): A list of device objects.
        filename (str, optional): The name of the output Excel file. Defaults to 'output.xlsx'.
    """
    
    all_data = []

    for device in devices:
        device_dict = device.to_dict()
        licenses = device_dict.pop('licenses')
        
        device_df = pd.json_normalize(device_dict, sep='_')
        
        for i, license in enumerate(licenses):
            license_df = pd.json_normalize(license, sep='_')
            license_df.columns = [f'license_{i}_{col}' for col in license_df.columns]
            device_df = pd.concat([device_df, license_df], axis=1)
        
        all_data.append(device_df)

    # Combine all individual DataFrames into one
    final_df = pd.concat(all_data, ignore_index=True)

    # Save the combined DataFrame to Excel
    final_df.to_excel(filename, index=False)
    print("Data saved to 'devices_info_combined.xlsx'.")

def main():
    """Main function to retrieve and process device information."""
    load_dotenv()

    list_uris = [
        "<show><system><info></info></system></show>",
        "<show><redistribution><service><status/></service></redistribution></show>",
        "<show><redistribution><agent><state>all</state></agent></redistribution></show>",
        "<show><user><user-id-service><status></status></user-id-service></user></show>",
        "<show><user><user-id-agent><statistics></statistics></user-id-agent></user></show>",
        "<show><user><user-id-service><client>all</client></user-id-service></user></show>",
        "<request><license><info><%2Finfo><%2Flicense><%2Frequest>"
    ]
    list_ips = ['192.0.2.254']
    devices = []

    user_ip = os.getenv('USER_IP')
    password_ip = os.getenv('PASSWORD_IP')

    if not user_ip or not password_ip:
        print("USER_IP or PASSWORD_IP not set in environment variables.")
        return

    for ip in list_ips:
        data_total = []
        uri = f"/api/?type=keygen&user={user_ip}&password={password_ip}"
        full_url = get_full_url(ip, uri)
        
        result_dict = get_response(full_url)
        api_key = get_api_key(result_dict)

        if api_key:
            for uri in list_uris:
                full_url = get_full_url(ip, uri, api_key)
                result_dict = get_response(full_url)
                if result_dict:
                    info = result_dict['response'].get('result')
                    if info:
                        data_total.append(info)
            new_device = process_device_info(data_total)
            if new_device:
                devices.append(new_device)
    
    if devices:
        save_to_excel(devices)    
     
if __name__ == '__main__':
    main()
