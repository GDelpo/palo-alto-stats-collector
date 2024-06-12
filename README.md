## Proyecto de Recopilación y Procesamiento de Información de Dispositivos

Este proyecto consta de dos archivos principales: `main.py` y `models.py`, diseñados para recopilar y procesar información de dispositivos de red. El objetivo principal es obtener datos relevantes sobre dispositivos y almacenarlos de manera estructurada para su posterior análisis o presentación.

### Estructura del Proyecto

- **main.py**: Este archivo contiene el código principal del proyecto. Se encarga de interactuar con los dispositivos de red, enviar solicitudes a través de la API, procesar las respuestas y almacenar la información obtenida. También contiene funcionalidades para manejar los archivos de entrada y salida, así como para realizar tareas de procesamiento de datos.

- **models.py**: Aquí se definen las clases `Device` y `License`, que representan los objetos de dispositivo y licencia, respectivamente. Estas clases proporcionan métodos para estructurar y manipular la información relacionada con los dispositivos y sus licencias.

### Funcionalidad

#### main.py

- **Funciones Principales:**
  - `check_response(result_dict)`: Verifica si la respuesta de la API es exitosa.
  - `get_api_key(result_dict)`: Obtiene la clave API de la respuesta.
  - `get_full_url(ip, uri, api_key=None)`: Construye la URL completa para las solicitudes a la API.
  - `get_response(url)`: Envía una solicitud GET a la URL especificada y devuelve la respuesta XML parseada como un diccionario.
  - `save_to_txt(result_dict, filename='output.txt')`: Guarda un diccionario en un archivo de texto en formato JSON.
  - `process_device_info(info)`: Procesa la información del dispositivo y crea un nuevo objeto `Device`.
  - `save_to_excel(devices, filename='output.xlsx')`: Guarda la información del dispositivo en un archivo de Excel.

- **Función Principal:**
  - `main()`: Función principal para recuperar y procesar la información del dispositivo.

#### models.py

- **Clases:**
  - `License`: Representa una licencia asociada a un dispositivo.
  - `Device`: Representa un dispositivo de red con sus atributos y licencias correspondientes.

### Relación entre Archivos

- `main.py` utiliza las clases y métodos definidos en `models.py` para estructurar y procesar la información del dispositivo.
- `models.py` proporciona las clases `Device` y `License`, que son utilizadas para crear objetos de dispositivo y licencia en `main.py`.

### Ejecución del Proyecto

Para ejecutar el proyecto, simplemente ejecute el archivo `main.py`. Asegúrese de tener las dependencias necesarias instaladas, como `requests`, `xmltodict`, `dotenv` y `pandas`. También se deben configurar las variables de entorno `USER_IP` y `PASSWORD_IP` con las credenciales adecuadas para acceder a los dispositivos de red.

```bash
python main.py
```

### Consideraciones

- Es importante configurar las variables de entorno `USER_IP` y `PASSWORD_IP` con las credenciales adecuadas para acceder a los dispositivos de red.
- Se debe tener en cuenta que este proyecto está diseñado para interactuar con dispositivos específicos a través de su API, por lo que es necesario adaptarlo según los requisitos y las características del entorno de red específico.

### TODO

- Obtener lista de IPs de un archivo.
- Crear automáticamente un archivo de las versiones recomendadas.
- Agregar información al DataFrame final con esta información.
- Pulir procesos y optimizar el código.
- Considerar la implementación de multiprocesamiento para mejorar el rendimiento.
- Dividir la lista de IPs para procesamiento paralelo o distribuido.
- Dividir en más archivos .py para que quede mejor estructurado el proyecto y sea más legible