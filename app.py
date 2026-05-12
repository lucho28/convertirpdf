from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles
import os
import subprocess

app = FastAPI()

# Montar archivos estáticos (CSS, JS, imágenes)
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

# Configuración para usar Jinja2 en el backend
templates = Jinja2Templates(directory="templates")

# Ruta para mostrar el formulario HTML
@app.get("/")
async def form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para manejar la carga del archivo PDF
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # Guardar el archivo PDF subido temporalmente
    temp_input_path = f"/tmp/{file.filename}"
    with open(temp_input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Comprimir el archivo PDF con Ghostscript
    temp_output_path = f"/tmp/compressed_{file.filename}"
    subprocess.run([
        "gs", 
        "-sDEVICE=pdfwrite", 
        "-dCompatibilityLevel=1.4", 
        "-dPDFSETTINGS=/ebook", 
        "-dNOPAUSE", 
        "-dQUIET", 
        "-dBATCH", 
        f"-sOutputFile={temp_output_path}",
        temp_input_path
    ])

    # Eliminar el archivo temporal de entrada
    os.remove(temp_input_path)

    # Devolver el archivo comprimido como una descarga
    return FileResponse(
    temp_output_path, 
    media_type="application/pdf",
    headers={"Content-Disposition": f"attachment; filename={file.filename}_comprimido.pdf"}
)
