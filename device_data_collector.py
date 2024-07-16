# Importaciones de bibliotecas estándar de Python
import os

# Importaciones de bibliotecas externas
import requests
import urllib3
import xmltodict
from dotenv import load_dotenv

# Importaciones locales
from dataframes import read_from_csv
from models import Device
from logger import info_logger, error_logger

# Load the environment variables
load_dotenv()

# Deshabilitar la advertencia de solicitud HTTPS no verificada
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    """
    Generates an API key for the specified IP address using the provided user and password.

    Args:
        ip (str): The IP address of the device.
        user_ip (str): The username for authentication.
        password_ip (str): The password for authentication.

    Returns:
        str or None: The generated API key if successful, None otherwise.
    """
    uri = f"/api/?type=keygen&user={user_ip}&password={password_ip}"
    full_url = get_full_url(ip, uri)
    result_dict = send_get_request_and_parse_response(full_url)
    if result_dict:
        info_logger.info(f"API key successfully generated for {ip}")
        return get_api_key(result_dict)
    return None

def get_full_url(ip, uri, api_key=None):
    """
    Construct the full URL based on the IP, URI, and API key.

    Parameters:
    ip (str): The IP address of the device.
    uri (str): The URI path for the API request.
    api_key (str, optional): The API key for authentication. Defaults to None.

    Returns:
    str: The full URL constructed based on the provided parameters.
    """
    if api_key is None:
        return f'https://{ip}{uri}'
    return f"https://{ip}/api/?type=op&cmd={uri}&key={api_key}"
    
def send_get_request_and_parse_response(url):
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
        response = requests.post(url, verify=False, timeout=10)
        response.raise_for_status()
        result_dict = xmltodict.parse(response.text)
        if check_response(result_dict):
            return result_dict
    except requests.exceptions.RequestException as e:
        error_logger.error(f"Request failed -> {url}: {e}")
    return None

def create_device_from_info(info):
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

def generate_full_paths(ip, api_key):
    """
    Generate full paths for the given IP address and API key.

    Args:
        ip (str): The IP address.
        api_key (str): The API key.

    Returns:
        list: A list of tuples containing the full URL and corresponding URI.
    """
    # Get the URIs from the environment variables
    list_uris = os.getenv('URIS').split('|')
    # Create a list to store the full paths
    list_uri_full_path = []
    # Iterate over the list of URIs and generate the full paths
    for uri in list_uris:
        # Generate the full URL
        full_url = get_full_url(ip, uri, api_key)
        # Append the data to the list
        list_uri_full_path.append((uri, full_url))
    return list_uri_full_path

def retrieve_data_from_multiple_uris(ip, api_key):
    # Generate the full paths
    list_full_uri_paths = generate_full_paths(ip, api_key)
    # List to store all the data retrieved from the device
    data_total = []
    # Iterate over the list of URIs and retrieve the information
    for uri, uri_path in list_full_uri_paths:
        # Get the response from the URI path
        result_dict = send_get_request_and_parse_response(uri_path)
        # If the response is successful, extract the information
        if result_dict:
            info = result_dict['response'].get('result')
            # Append the information to the data_total list
            if info:
                info_logger.info(f"Data retrieved from {uri}")
                data_total.append(info)
            else:
                error_logger.error(f"No data retrieved ({ip}) from {uri}")

    return data_total

def process_device_list(list_ips):
    """
    Process the device information for a list of IP addresses.

    Args:
        list_ips (list): A list of IP addresses.

    Returns:
        None
    """
    # Retrieve the credentials from the environment variables
    user_ip = os.getenv('USER_IP')
    password_ip = os.getenv('PASSWORD_IP')

    # Check if the credentials are set
    if not user_ip or not password_ip:
        error_logger.error("USER_IP or PASSWORD_IP not set in environment variables.")
        exit()
    # List to store all the devices objects
    list_of_devices_obj = []
    # counter
    counter = 1
    # Iterate over the list of IP addresses
    for ip in list_ips:
        print(f"Processing device {counter} of {len(list_ips)}")
        info_logger.info(f"Starting process for: {ip}")       
        # Generate the API key
        api_key = generate_api_key(ip, user_ip, password_ip)
        # If the API key was successfully generated, retrieve the device information
        if api_key:
            print(f"API key generated for {ip}")
            # List to store all the data retrieved from the device
            data_total = retrieve_data_from_multiple_uris(ip, api_key)
            # Process the device information and create a new Device object
            new_device = create_device_from_info(data_total)
            # If a new device was created, append it to the devices list
            if new_device:
                # Append the new device to the list
                list_of_devices_obj.append(new_device)
                info_logger.info(f"Device information processed for {ip}")                
            else:
                error_logger.error(f"Failed to process device information for {ip}")
        else:
            error_logger.error(f"Failed to generate API key for {ip}")
            print(f"API key not generated for {ip}")
        counter += 1
            
    # Return the list of devices objects
    return list_of_devices_obj

def collect_data_from_devices(csv_file_path=None):
    devices = None
    if csv_file_path:
        # List of IP addresses to retrieve the information from
        list_ips = read_from_csv(csv_file_path)
        # Log the start of the process    
        info_logger.info(f'Start the process of retrieving device information of {len(list_ips)}')
        # List to store all the devices objects
        devices = process_device_list(list_ips)
        if len(devices) > 0:
            info_logger.info(f'Number of devices processed: {len(devices)}')
        else:
            error_logger.error('No devices were processed.')
        # Log the end of the process
        info_logger.info('End of the process of retrieving device information.')
        info_logger.info(f"{'-'*50}")
    else:
        error_logger.error('No CSV file provided.')
        
    # Return the devices list       
    return devices
    

if __name__ == '__main__':

    devices = collect_data_from_devices()
    if devices:
        for device in devices:
            print(device)
            print(device.identify_model())
        