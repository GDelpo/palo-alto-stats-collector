import os
import json
from dataframes import save_to_excel
from device_data_collector import collect_data_from_devices
from html_data_extractor import extract_and_process_html_tables
from logger import info_logger, error_logger
from utils import ensure_dir_exists, get_most_recent_file, get_source_dir


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


def main():
    info_logger.info('Starting the program to collect data from devices')
    if not get_most_recent_file(get_source_dir('json'), '.json'):
        info_logger.info('JSON directory does not exist. We try to extract data from HTML tables')
        extract_and_process_html_tables()
        return
    else:
        # devices = collect_data_from_devices()
        # if devices:
        #     processed_devices = update_device_with_json(json_file, devices)
        #     save_to_excel(processed_devices, 'output.xlsx')       
        print('JSON directory exists')
        pass
if __name__ == "__main__":
    main()
    
