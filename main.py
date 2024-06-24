import os
from logger import info_logger, error_logger
from utils import ensure_dir_exists, get_source_dir


json_source_dir = get_source_dir('json')
json_source_dir_exist = ensure_dir_exists(json_source_dir)

if json_source_dir_exist:
    info_logger.info(f"JSON source directory: {json_source_dir}")
    json_source_dir_files = [file for file in os.listdir(json_source_dir) if file.endswith('.json')]
    # Find the most recently modified file
    last_modified_file = max(json_source_dir_files, key=lambda file: os.path.getmtime(os.path.join(json_source_dir, file)))
    # Get the full path of the file
    full_path = os.path.abspath(os.path.join(json_source_dir, last_modified_file))
    print(f"Last modified file: {last_modified_file}")
    print(f"Full path: {full_path}")