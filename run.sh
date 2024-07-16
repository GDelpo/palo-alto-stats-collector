# Obtener la ruta del directorio actual
ruta_actual=$(pwd)

# Cambiar al directorio actual
cd "$ruta_actual" || { echo "Error: No se pudo cambiar al directorio $ruta_actual"; exit 1; }

# Definir la ruta del Python del entorno virtual y el script principal
ruta_python="$ruta_actual/env/bin/python3"
script_principal="$ruta_actual/main.py"

# Ejecutar main.py usando el Python del entorno virtual
echo "Ejecutando $script_principal usando $ruta_python..."
"$ruta_python" "$script_principal"