import os
import json
from dataframes import save_to_excel
from device_data_collector import collect_data_from_devices
from html_data_extractor import extract_and_process_html_tables
from utils import get_most_recent_file, get_source_dir


def update_device_with_json(json_file, devices):
    with open(json_file, 'r') as file:
        data = json.load(file)

    for device in devices:
        model_type = device.identify_model()
        if model_type:
            for item in data:
                if model_type in item:
                    prefered_version = item[model_type].get(device.sw_version.rsplit('.', 1)[0], [None])[0]
                    if prefered_version and prefered_version != device.sw_version:
                        device.sw_version_prefered = prefered_version
                    else:
                        device.sw_version_prefered = 'is up to date with prefered version'
    return devices


def process_json_file(json_source_dir):
    while not os.path.exists(json_source_dir) or not os.listdir(json_source_dir):
        print('No JSON files found. Attempting to extract data from HTML tables.')
        is_completed = extract_and_process_html_tables()
        
        if is_completed:
            print('Data extracted from HTML tables and saved in JSON file.')
        else:
            print('Could not extract data from HTML tables. Check the logs for more information.')
            return None

    json_file = get_most_recent_file(json_source_dir, '.json')
    return json_file


def main():
    print('Starting main process...')
    json_source_dir = get_source_dir('json')
    json_file = process_json_file(json_source_dir)
    
    if json_file:
        print('Proceeding to collect data from devices...')
        devices = collect_data_from_devices(get_most_recent_file(get_source_dir(), '.csv'))
        if devices:
            print('Data collected from devices. Updating devices with JSON data...')
            processed_devices = update_device_with_json(json_file, devices)
            print('Devices updated with JSON data. Saving data to Excel file...')
            save_to_excel(processed_devices, 'output.xlsx')
            print('Data saved to Excel file.')
        else:
            print('No devices found. Check the logs for more information.')
    else:
        print('Failed to process JSON file. Exiting.')
    


if __name__ == "__main__":
    main()
