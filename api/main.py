from fastapi import FastAPI, UploadFile, File, HTTPException
from minio import Minio
from minio.error import S3Error
import os
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Request
from typing import List
from fastapi.responses import StreamingResponse
from io import BytesIO


app = FastAPI()

# Configurações do MinIO
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true" 
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "mybucket")

# Inicializa o cliente MinIO
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

@app.on_event("startup")
async def startup_event():
    """Cria o bucket MinIO se ele não existir ao iniciar a aplicação."""
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"Bucket '{MINIO_BUCKET}' criado com sucesso.")
        else:
            print(f"Bucket '{MINIO_BUCKET}' já existe.")
    except S3Error as e:
        print(f"Erro ao verificar/criar bucket: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar MinIO: {e}")

@app.get("/")
async def read_root():
    return {"message": "API FastAPI com integração MinIO S3!"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    """Faz upload de um arquivo para o MinIO."""
    try:
        size = file.size
        file_name = file.filename
        file_content_type = file.content_type

        minio_client.put_object(
            MINIO_BUCKET,
            file_name,
            data= file.file, #BLOB 
            length=size,
            content_type=file_content_type
        )
        
        return {"filename": file_name, "message": "Arquivo enviado com sucesso para o MinIO!"}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar arquivo para o MinIO: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

@app.get("/list_objects/")
async def list_objects():
    """Lista objetos em um bucket do MinIO."""
    try:
        objects = list(minio_client.list_objects(MINIO_BUCKET))
        object_names = [obj.object_name for obj in objects]
        return {"bucket": MINIO_BUCKET, "objects": object_names}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar objetos no MinIO: {e}")


@app.get("/download/{object_name}")
async def download_file(object_name: str):
    """Baixa um arquivo do MinIO e retorna como um download."""
    try:
       
        response = minio_client.get_object(MINIO_BUCKET, object_name)
        
       
        file_data = BytesIO(response.read())
        response.close()
        response.release_conn()

       
        content_type = "application/octet-stream"
        if "." in object_name:
            ext = object_name.split(".")[-1]
            content_type = f"application/{ext}"  

        
        return StreamingResponse(
            file_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={object_name}",
                "Content-Length": str(len(file_data.getvalue())),
            }
        )
    except S3Error as e:
        if "NoSuchKey" in str(e):
            raise HTTPException(status_code=404, detail=f"Arquivo '{object_name}' não encontrado no bucket '{MINIO_BUCKET}'.")
        raise HTTPException(status_code=500, detail=f"Erro ao baixar arquivo do MinIO: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
