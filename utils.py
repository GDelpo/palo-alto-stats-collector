import datetime
import os

from logger import error_logger, info_logger

def ensure_dir_exists(directory):
    """
    Ensures that the specified directory exists. Creates it if it does not exist.
    
    Args:
    directory (str): The directory path to check and create if necessary.
    
    Returns:
    bool: True if the directory already existed, False if it was created.
    """
    if not os.path.exists(directory):
        error_logger.error(f"Directory {directory} does not exist.")
        os.makedirs(directory)
        return False
    return True
    
def get_source_dir(subdir=''):
    """
    Returns the path to the source directory.
    
    Args:
    subdir (str): Optional subdirectory name within the source directory.
    
    Returns:
    str: Full path to the source directory or its subdirectory.
    """
    current_dir = os.getcwd()
    source_dir_parent = os.path.join(current_dir, 'source')
    if subdir:
        source_dir = os.path.join(source_dir_parent, subdir)
    else:
        source_dir = source_dir_parent
    return source_dir

def get_most_recent_file(directory, file_extension):
    """
    Get the most recently modified file with the specified file extension in the given directory.

    Args:
        directory (str): The directory to search for files.
        file_extension (str): The file extension to filter the files.

    Returns:
        str: The full path of the most recently modified file, or None if no files were found.
    """
    # Log the directory and file extension to search for
    info_logger.info(f'Directory to search for {file_extension} files: {directory}')
    # Initialize the variables to store the most recently modified file and its full path
    full_path_last_modified_file = None
    # Get the list of files with the specified extension
    files = [file for file in os.listdir(directory) if file.endswith(file_extension)]
    
    if not files: # If no files were found
        # Log the error if no files were found
        error_logger.error(f'No {file_extension} files found in {directory}.')        
    else: # If files were found
        info_logger.info(f'Number of {file_extension} files found: {len(files)}')
        # Get the most recently modified file
        last_modified_file = max(files, key=lambda file: os.path.getmtime(os.path.join(directory, file)))
        # Get the full path of the most recently modified file
        full_path_last_modified_file = os.path.abspath(os.path.join(directory, last_modified_file))
        # Log the most recently modified file
        info_logger.info(f'Path of the most recently modified ({datetime.datetime.fromtimestamp(os.path.getmtime(full_path_last_modified_file))}) {file_extension} file: {last_modified_file}')
    return full_path_last_modified_file