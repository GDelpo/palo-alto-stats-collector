# Importaciones de bibliotecas estándar de Python
import datetime
import json
import os
import re

# Importaciones de bibliotecas externas
from bs4 import BeautifulSoup  # Para analizar y manipular documentos HTML y XML

# Importaciones locales
from logger import info_logger, error_logger
from utils import ensure_dir_exists, get_most_recent_file, get_source_dir

def remove_specific_attributes_and_tags(html):
    """
    Remueve atributos específicos ('style', 'width', 'height', 'role', 'class', 'id', 'colspan', 'size')
    y tags HTML específicos ('em', 'strong', 'span') de una cadena HTML usando expresiones regulares.

    Args:
    - html (str): Cadena HTML donde se buscarán y eliminarán los atributos y tags.

    Returns:
    - str: Cadena HTML modificada sin los atributos y tags especificados.
    """
    attributes_to_remove = ['style', 'width', 'height', 'role', 'class', 'id', 'colspan', 'size', 'color', 'data-unlink']
    tags_to_remove = ['em', 'strong', 'span', 'font', 'br', 'p', 'h5', 'thead']  # Tags HTML que se desean remover

    # Eliminar atributos específicos
    for attr in attributes_to_remove:
        html = re.sub(rf'\b{attr}="[^"]*"', '', html)

    # Eliminar tags HTML específicos
    for tag in tags_to_remove:
        html = re.sub(rf'<{tag}[^>]*>', '', html)  # Elimina apertura de tag
        html = re.sub(rf'</{tag}>', '', html)      # Elimina cierre de tag

    return html

def search_last_modified_html_file(parent_dir):
    """
    Search for the most recently modified HTML file in the specified directory and return its content.

    Args:
        parent_dir (str): The directory to search within.

    Returns:
        str: The content of the most recently modified HTML file.
    """
    # Initialize the HTML content variable
    html_content = None
    # Search for HTML files in the specified directory
    last_modified_html_file = get_most_recent_file(parent_dir, '.html')

    if last_modified_html_file:
        # Load the HTML file
        with open(last_modified_html_file, 'r', encoding='utf-8') as file:
            html_content = file.read()

    return html_content

def extract_version(content):
    """
    Extracts the version number and the rest of the content from a given string.
    
    Args:
    - content (str): The string containing version information.
    
    Returns:
    - tuple: A tuple containing two elements:
        - version (str or None): The extracted version number.
        - rest (str): The remaining content after removing the version number.
    """
    # Regex pattern to capture the version
    version_pattern = r'^(\d+(?:\.\d+)*)'

    # Applying the pattern to content
    match = re.match(version_pattern, content)

    if match:
        version = match.group(1)
        rest = content[len(version):].strip()
        return version, rest
    else:
        return None, content.strip()

def search_tables(html_content, initial_text, final_text):
    """
    Search for tables within a specific range in an HTML document.

    Args:
        html_content (str): The HTML content to search within.
        initial_text (str): The text of the initial h2 tag to start the range.
        final_text (str): The text of the final h2 tag to end the range.

    Returns:
        list: A list of tuples containing the preceding h2 tag text and the corresponding table (str).

    """
    info_logger.info(f"Searching for tables within the range '{initial_text}' - '{final_text}'")

    # Create the BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the initial h2 tag with specific text
    initial_h2_tag = soup.find('h2', string=initial_text)

    # Find the final h2 tag with specific text
    final_h2_tag = soup.find('h2', string=final_text)

    # Find all tables within the range and save the preceding h2 tag for each table
    tables_in_range = []
    current_tag = initial_h2_tag

    while current_tag and current_tag != final_h2_tag:
        # Check if the current tag is an h2 tag
        if current_tag.name == 'h2':
            current_h2_text = current_tag.text  # Save the text of the current h2 tag
        # Check if the current tag is a table
        if current_tag.name == 'table':
            # Remove specific attributes and tags from the table
            cleaned_table = remove_specific_attributes_and_tags(str(current_tag))
            tables_in_range.append((current_h2_text, cleaned_table))  # Save the h2 text and the table as a tuple
        # Move to the next sibling tag
        current_tag = current_tag.find_next_sibling()

    return tables_in_range

def extract_columns_from_row(row_soup_obj):
    """
    Extracts specific columns from a row represented by a BeautifulSoup object.

    Args:
    - row_soup_obj (BeautifulSoup Tag): The BeautifulSoup object representing the row.

    Returns:
    - list: A list containing the extracted data from the row, structured as [support_preferred, release, release_date, comments].
      If the row does not have exactly 4 <td> elements, returns an empty list.

    Prints:
    - Message indicating if the row does not have the expected format (not 4 <td> elements).
    """
    data_row = []  # List to store the extracted data from the row

    # Find all <td> elements within the row
    tds = row_soup_obj.find_all('td')

    # Extract content from each <td> if there are exactly 4 <td> elements
    if len(tds) == 4:
        #support_preferred = tds[0].text.strip()
        release = tds[1].text.strip()
        release_date = tds[2].text.strip()
        comments = tds[3].text.strip()
        # Append the extracted data to the list 
        data_row = [release, datetime.datetime.strptime(release_date, '%m/%d/%y').strftime('%d/%m/%Y'), comments]
    else:
        error_logger.error("The row does not have the expected format (not 4 <td> elements)")
        
    return data_row


def extract_info_from_table(table_str):
    """
    Extracts information from a HTML table represented as a string.

    Args:
    - table_str (str): The HTML string of the table.

    Returns:
    - dict: A dictionary where keys are version numbers and values are lists of BeautifulSoup objects representing rows.

    Note:
    - This function assumes the presence of BeautifulSoup (bs4) for HTML parsing.
    """
    # Convert the string back to a BeautifulSoup object
    table_soup = BeautifulSoup(table_str, 'html.parser')
    # Initialize the dictionary to store the ordered rows
    ordered_rows = {}
    # Initialize the current version
    for row in table_soup.find_all('tr'):
        cell = row.find('td')
        if cell:
            # Extract the all content of the cell
            content = cell.text.strip()
            if cell.find('h1'):
                # Found a new version
                current_version = extract_version(content)[0] # Extract the version number without the rest of the content like comments
                ordered_rows[current_version] = []
            elif content == 'P':
                # Found a row with data
                row_data = extract_columns_from_row(row)
                if row_data:  # Check if row_data is not empty
                    ordered_rows[current_version].extend(row_data)

    return ordered_rows

def process_info_from_tables(tables_data):
    # Create a list to store the dictionaries
    list_of_dicts = []
    # Process the tables
    for name_of_table, table in tables_data:
        # Create a dictionary to store the information of the table
        table_dict = {}
        # Extract information from the table
        ordered_rows = extract_info_from_table(table)
        # Remove empty keys from the dictionary
        ordered_rows_cleaned = {k: v for k, v in ordered_rows.items() if v}
        # Save the extracted information in a dictionary
        table_dict[name_of_table] = ordered_rows_cleaned
        # Append the dictionary to the list
        list_of_dicts.append(table_dict)

    return list_of_dicts
        

def save_to_json(list_of_dicts):
    """
    Save a list of dictionaries to a JSON file.

    Args:
        source_dir_parent (str): The parent directory of the source directory.
        folder_name (str): The name of the directory where the JSON file will be saved.
        list_of_dicts (list): The list of dictionaries to be saved.

    Returns:
        None
    """
    # Get the source directory for the JSON files
    source_dir_json = get_source_dir('json')
    # Ensure that the directory exists
    source_dir_json_exist = ensure_dir_exists(source_dir_json)
    # Check if the directory was created
    if not source_dir_json_exist:
        info_logger.info(f"Directory {source_dir_json} created.")
    # Current directory + Source parent directory + JSON directory + name.json
    complete_name = os.path.join(source_dir_json, f'data_html_{datetime.date.today()}.json')
    try:
        # Save the list of dictionaries in a file
        with open(complete_name, 'w') as file:
            json.dump(list_of_dicts, file, indent=4)
        info_logger.info(f"Data saved to {complete_name}")
    except Exception as e:
        error_logger.error(f"Error saving data to {complete_name}")
        raise e

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

def extract_and_process_html_tables():
    """
    Extracts and processes HTML tables within a specified range.

    This function performs the following steps:
    1. Starts the HTML data extraction process.
    2. Gets the source directory for the HTML files.
    3. Retrieves the content of the most recently modified HTML file.
    4. Searches for tables within a specific range.
    5. Checks if there are tables within the specified range.
    6. If tables are found, processes the information from the tables and saves it to a JSON file.
    7. If no tables are found, raises a ValueError.

    Returns:
        None
    """
    # Initialize the variable to check if the process is completed
    is_completed = False
    # Start the HTML data extraction process
    info_logger.info("Starting the HTML data extraction process...")
    # Get the source directory for the HTML files
    source_dir_html = get_source_dir('html')
    source_dir_html_exist = ensure_dir_exists(source_dir_html)
    if not source_dir_html_exist:
        info_logger.error(f"Directory {source_dir_html} created. Put the HTML file in this directory with info.")
    else:
        # Get the content of the most recently modified HTML file
        html_content = search_last_modified_html_file(source_dir_html)
        if html_content:
            # Search for tables within a specific range
            tuple_of_tables_data = search_tables(html_content, 'PAN-OS for Firewalls', 'Prisma Access for Panorama')
            # Check if there are tables within the specified range
            if len(tuple_of_tables_data) > 0:
                info_logger.info(f"Found {len(tuple_of_tables_data)} tables within the specified range.") 
                # Create a list to store the dictionaries
                list_of_dicts = process_info_from_tables(tuple_of_tables_data)
                if len(list_of_dicts) > 0:
                    info_logger.info(f"Processed {len(list_of_dicts)} tables.")
                    # Save the list of dictionaries to a JSON file
                    save_to_json(list_of_dicts)
                    is_completed = True
            else:
                error_logger.error("No tables found within the specified range.")                
        else:
            error_logger.error(f'FileNotFoundError: No HTML files found in {source_dir_html} directory.')
    # Check if the process is completed           
    if is_completed:
        info_logger.info("HTML data extraction process completed.")
    else:
        info_logger.error("HTML data extraction process failed. Check the error logs for more information.")
    # End the HTML data extraction process
    info_logger.info(f"{'-'*50}")
    return is_completed
    
if __name__ == '__main__':
    can_complete_the_process = extract_and_process_html_tables()
    print(f"Can complete the process: {can_complete_the_process}")