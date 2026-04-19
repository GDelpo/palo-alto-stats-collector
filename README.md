# palo-alto-stats-collector

<p>
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="Status" src="https://img.shields.io/badge/status-stable-green">
</p>

> Consulta la API XML de dispositivos Palo Alto Networks, recopila información (modelo, versión, licencias) y exporta a Excel. Incluye fallback a extracción desde HTML tables.

## Features

- Consulta multi-device vía API XML de Palo Alto (WSAA + API key).
- Parseo y consolidación en objetos `Device` y `License` (ver `models.py`).
- Exportación a Excel (`openpyxl`) con una fila por device.
- **Fallback**: si no hay respuesta de la API, extrae datos desde archivos HTML tables pegados del portal de soporte.
- Cross-check de versión de firmware vs versión "preferida" (a través de un JSON de referencia).
- Logging centralizado en `logger.py`.

## Quickstart

### Requirements

- Python 3.9+
- Credenciales con permiso de consulta a la XML API de cada firewall
- Acceso de red a los dispositivos

### Install

```bash
git clone https://github.com/GDelpo/palo-alto-stats-collector.git
cd palo-alto-stats-collector
python -m venv env
source env/bin/activate          # Linux/macOS
# .\env\Scripts\Activate.ps1     # Windows
pip install -r requirements.txt
```

O usar el helper:

```bash
./setup_env.sh
```

### Configure

```bash
cp .env.example .env
# Editar .env con credenciales y lista de IPs a consultar
```

### Run

```bash
python main.py
```

O el helper `run.sh` que activa el venv y lanza `main.py`:

```bash
./run.sh
```

## Configuration

| Variable | Descripción |
|----------|-------------|
| `USER_IP` | Usuario con permiso de consulta a la XML API |
| `PASSWORD_IP` | Password del usuario |
| `URIS` | Lista de IPs o FQDNs de firewalls a consultar, separadas por `\|` |

## Architecture

```
palo-alto-stats-collector/
├── main.py                  # Entry point
├── device_data_collector.py # Orquesta llamadas API XML
├── html_data_extractor.py   # Fallback: parsea HTML tables con BeautifulSoup
├── dataframes.py            # Exportación a Excel
├── models.py                # Clases Device, License
├── utils.py                 # Helpers (paths, fechas, parsing)
├── logger.py                # Setup de logging
├── setup_env.sh / run.sh    # Wrappers de conveniencia
├── requirements.txt
└── .env.example
```

**Stack:** `requests` + `xmltodict` para el API XML, `beautifulsoup4` para el fallback HTML, `pandas` + `openpyxl` para la exportación.

## License

[MIT](LICENSE) © 2026 Guido Delponte
