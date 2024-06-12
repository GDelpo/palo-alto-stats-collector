import logging
import os

# Crea la carpeta para los logs si no existe
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Crea un logger para los errores
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)

# Crea un handler para escribir los errores en un archivo
error_handler = logging.FileHandler(os.path.join(log_folder, 'error.log'), encoding='utf-8')
error_handler.setLevel(logging.ERROR)

# Crea un formatter y añádelo al handler
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)

# Añade el handler al logger
error_logger.addHandler(error_handler)

# Crea un logger para la información del proceso
info_logger = logging.getLogger('info_logger')
info_logger.setLevel(logging.INFO)

# Crea un handler para escribir la información del proceso en un archivo
info_handler = logging.FileHandler(os.path.join(log_folder, 'proceso.log'), encoding='utf-8')
info_handler.setLevel(logging.INFO)

# Crea un formatter y añádelo al handler
info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(info_formatter)

# Añade el handler al logger
info_logger.addHandler(info_handler)