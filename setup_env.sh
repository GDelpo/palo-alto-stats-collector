# Obtener la ruta del directorio actual
ruta_actual=$(pwd)

# Verificar si existe la carpeta 'env'
if [ ! -d "env" ]; then
  echo "La carpeta 'env' no existe. Creando entorno virtual..."
  python3 -m venv env
  echo "Entorno virtual 'env' creado."
else
  echo "La carpeta 'env' ya existe. No se requiere crear el entorno virtual."
fi

# Activar el entorno virtual
echo "Activando el entorno virtual..."
source "$ruta_actual/env/bin/activate"

# Instalar las dependencias desde requirements.txt
echo "Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

echo "Está listo para probar, lanzar el programa"