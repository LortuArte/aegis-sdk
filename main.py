import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Inicializamos el servidor de AEGIS
app = FastAPI(title="AEGIS API")

# Esta ruta le dice al servidor que muestre tu Landing Page (index.html)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Busca el archivo index.html en la misma carpeta que este script
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: No se encuentra el archivo index.html. Asegúrate de haberlo creado en la misma carpeta.</h1>"