import os
import json
from dataframes import save_to_excel
from device_data_collector import collect_data_from_devices
from html_data_extractor import extract_and_process_html_tables
from logger import info_logger, error_logger
from utils import ensure_dir_exists, get_most_recent_file, get_source_dir


json_source_dir = get_source_dir('json')
json_source_dir_exist = ensure_dir_exists(json_source_dir)

if json_source_dir_exist:
    json_file = get_most_recent_file(json_source_dir, '.json')
    if not json_file:
        extract_and_process_html_tables()
        exit()
    else:
        info_logger.info(f'Processing JSON file: {json_file}')
        devices = collect_data_from_devices()
        if devices:
            for device in devices:
                model_type = device.identify_model()
                if model_type:
                    with open(json_file, 'r') as file:
                        data = json.load(file)
                    if data: 
                        for item in data:
                            if model_type in item:
                                prefered_version = item[model_type].get(device.sw_version.rsplit('.', 1)[0])[0]
                                if prefered_version != device.sw_version:
                                    device.sw_version_prefered = prefered_version
                                else:
                                    device.sw_version_prefered = 'is up to date with prefered version'
                                
            save_to_excel(devices, 'output.xlsx')  

        else:
            error_logger.error('No devices were processed.')
            exit()



