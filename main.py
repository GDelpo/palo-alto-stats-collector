# Importaciones de bibliotecas estándar de Python
import os

# Importaciones de bibliotecas externas
import requests
import pandas as pd
import xmltodict
from dotenv import load_dotenv

# Importaciones locales
from models import Device
from logger import info_logger, error_logger


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

def generate_api_key(ip, user_ip, password_ip):
    uri = f"/api/?type=keygen&user={user_ip}&password={password_ip}"
    full_url = get_full_url(ip, uri)
    
    result_dict = get_response(full_url)
    if result_dict:
        return get_api_key(result_dict)
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
        response = requests.post(url, verify=False)
        response.raise_for_status()
        result_dict = xmltodict.parse(response.text)
        if check_response(result_dict):
            return result_dict
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Request failed -> {url}: {e}")
    return None

def process_device_info(info):
    """
    Process device information and create a new Device object.

    Args:
        info (list): A list of dictionaries containing device information.

    Returns:
        Device: A new Device object with the processed information.

    """
    new_device = None
    # Iterate over the list of dictionaries
    for item in info:
        # Check if the item is a dictionary
        if isinstance(item, dict):
            system_info = item.get('system')
            # If the 'system' key exists in the dictionary, extract the information
            if system_info:
                new_device = Device(
                    system_info.get('hostname'), system_info.get('model'), system_info.get('serial'),
                    system_info.get('ip-address'), system_info.get('sw-version'),
                    system_info.get('global-protect-client-package-version'), system_info.get('app-version'),
                    system_info.get('av-version'), system_info.get('threat-version'),
                    system_info.get('wildfire-version'), system_info.get('url-filtering-version'),
                    system_info.get('device-certificate-status')
                )
            # Extract the licenses information
            licenses_info = item.get('licenses')
            # If the 'licenses' key exists in the dictionary, extract the information
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

    try:
        # Combine all individual DataFrames into one
        final_df = pd.concat(all_data, ignore_index=True)

        # Save the combined DataFrame to Excel
        final_df.to_excel(filename, index=False)
        # Log the information
        info_logger.info(f"All devices information saved to {filename}")
    except Exception as e:
        error_logger.error(f"Error saving device information to Excel: {e}")

if __name__ == '__main__':

    # Load the environment variables
    load_dotenv()

    # Dividir la cadena en una lista de URIs usando el delimitador '|'
    list_uris = os.getenv('URIS').split('|')

    # List of IP addresses to retrieve the information from
    list_ips = ['192.0.2.254'] # Pasar a un archivo de configuración, crear un método para leerlo

    # List to store all the devices objects
    devices = []

    # Retrieve the credentials from the environment variables
    user_ip = os.getenv('USER_IP')
    password_ip = os.getenv('PASSWORD_IP')

    # Check if the credentials are set
    if not user_ip or not password_ip:
        error_logger.error("USER_IP or PASSWORD_IP not set in environment variables.")
        exit()
    
    # Iterate over the list of IP addresses
    for ip in list_ips:
        info_logger.info(f"Starting procces for: {ip}")
        # List to store all the data retrieved from the device
        data_total = []
        # Generate the API key
        api_key = generate_api_key(ip, user_ip, password_ip)
        # If the API key was successfully generated, retrieve the device information
        if api_key:
            info_logger.info(f"API key generated for {ip}")
            # Iterate over the list of URIs and retrieve the information
            for uri in list_uris:
                # Construct the full URL
                full_url = get_full_url(ip, uri, api_key)
                result_dict = get_response(full_url)
                # If the response is successful, extract the information
                if result_dict:
                    info = result_dict['response'].get('result')
                    # Append the information to the data_total list
                    if info:
                        info_logger.info(f"Data retrieved from {uri}")
                        data_total.append(info)
                    else:
                        error_logger.error(f"No data retrieved ({ip}) from {uri}")
            # Process the device information and create a new Device object
            new_device = process_device_info(data_total)
            # If a new device was created, append it to the devices list
            if new_device:
                devices.append(new_device)
                info_logger.info(f"Device information processed for {ip}")                
            else:
                error_logger.error(f"Failed to process device information for {ip}")
        else:
            error_logger.error(f"Failed to generate API key for {ip}")

    # Save the device information to an Excel file
    if devices:
        for device in devices:
            print(device)

        save_to_excel(devices)

    info_logger.info(f"{'-'*50}")