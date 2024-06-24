import os

from logger import error_logger

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