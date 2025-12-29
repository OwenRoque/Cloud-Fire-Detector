"""
Módulo para manejo de imágenes y subida a S3
"""
import boto3
import base64
import os
from datetime import datetime
from botocore.exceptions import ClientError

S3_BUCKET_NAME = "fire-detection-images-577272335685"
AWS_REGION = "us-east-1"

class ImageManager:
    def __init__(self, logger):
        self.logger = logger
        try:
            self.s3_client = boto3.client('s3', region_name=AWS_REGION)
            self.logger.info(f" S3 client inicializado (bucket: {S3_BUCKET_NAME})")
        except Exception as e:
            self.logger.warning(f" No se pudo inicializar S3 client: {e}")
            self.s3_client = None
    
    def upload_to_s3(self, image_data_base64, sensor_id, zona):
        """
        Sube imagen a S3 desde datos base64
        
        Args:
            image_data_base64: Imagen codificada en base64
            sensor_id: ID del sensor
            zona: Zona donde se detectó el fuego
            
        Returns:
            dict con s3_key, s3_url y bucket, o None si falla
        """
        if not self.s3_client:
            self.logger.warning(" S3 client no disponible, saltando subida")
            return None
        
        if not image_data_base64:
            self.logger.warning(" No hay datos de imagen para subir")
            return None
        
        try:
            # Decodificar base64
            image_bytes = base64.b64decode(image_data_base64)
            
            # Generar key para S3
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"detections/{zona}/{sensor_id}/{timestamp}.jpg"
            
            self.logger.info(f" Subiendo imagen a S3: {s3_key}")
            
            # Subir a S3
            self.s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=image_bytes,
                ContentType='image/jpeg',
                Metadata={
                    'sensor_id': sensor_id,
                    'zona': zona,
                    'timestamp': timestamp
                }
            )
            
            # Generar URL
            s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            
            self.logger.info(f" Imagen subida exitosamente a S3")
            self.logger.info(f"   Key: {s3_key}")
            
            return {
                "s3_key": s3_key,
                "s3_url": s3_url,
                "bucket": S3_BUCKET_NAME
            }
        
        except ClientError as e:
            self.logger.error(f" Error subiendo a S3: {e}")
            return None
        except Exception as e:
            self.logger.error(f" Error inesperado al subir imagen: {e}", exc_info=True)
            return None
    
    def save_local_copy(self, image_data_base64, sensor_id, zona):
        """
        Guarda copia local de la imagen (opcional)
        
        Args:
            image_data_base64: Imagen codificada en base64
            sensor_id: ID del sensor
            zona: Zona donde se detectó el fuego
            
        Returns:
            path de la imagen guardada, o None si falla
        """
        try:
            # Crear directorio si no existe
            local_dir = os.path.join(os.path.dirname(__file__), "..", "images", zona)
            os.makedirs(local_dir, exist_ok=True)
            
            # Decodificar y guardar
            image_bytes = base64.b64decode(image_data_base64)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(local_dir, f"{sensor_id}_{timestamp}.jpg")
            
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            self.logger.info(f" Copia local guardada: {image_path}")
            return image_path
        
        except Exception as e:
            self.logger.error(f" Error guardando copia local: {e}")
            return None
