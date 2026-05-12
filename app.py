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
    # Sanitizar el nombre del archivo para evitar problemas con caracteres especiales
    # (Ghostscript interpreta % como secuencia especial de paginación)
    safe_filename = "".join(c if c.isalnum() or c in "._- " else "_" for c in file.filename)
    # Guardar el archivo PDF subido temporalmente
    temp_input_path = f"/tmp/{safe_filename}"
    with open(temp_input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Comprimir el archivo PDF con Ghostscript
    temp_output_path = f"/tmp/compressed_{safe_filename}"
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
    original_stem = os.path.splitext(file.filename)[0]
    return FileResponse(
    temp_output_path, 
    media_type="application/pdf",
    headers={"Content-Disposition": f"attachment; filename={original_stem}_comprimido.pdf"}
)
