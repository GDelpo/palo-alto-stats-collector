import os
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
        # Process the JSON file
        devices = collect_data_from_devices()
        if devices:
            for device in devices:
                match device.identify_model():
                    case 'PA':
                        model_type = 'Palo Alto'
                    case 'VM':
                        model_type = 'VMware'
                    case _:
                        model_type = None
                if model_type:
                    info_logger.info(f"Device model type: {model_type}")
        else:
            error_logger.error('No devices were processed.')
            exit()



