import json
import os
from config.settings import *

class AWSIoTClient:
    def __init__(self, logger):
        self.logger = logger
        self.connection = None
        self.connected = False

    def connect(self):
        if not AWS_IOT_ENABLED:
            self.logger.info("🏝️  AWS IoT deshabilitado - Modo Local")
            return

        # Verificar que los certificados existen
        if not os.path.exists(AWS_CERT_PATH):
            self.logger.warning(f"  Certificado no encontrado: {AWS_CERT_PATH}")
            self.logger.warning("🏝️  AWS IoT deshabilitado - Modo Local")
            return

        try:
            from awscrt import mqtt as mqtt_connection_builder
            from awsiot import mqtt_connection_builder as iot_builder

            self.connection = iot_builder.mtls_from_path(
                endpoint=AWS_IOT_ENDPOINT,
                cert_filepath=AWS_CERT_PATH,
                pri_key_filepath=AWS_PRIVATE_KEY_PATH,
                ca_filepath=AWS_ROOT_CA_PATH,
                client_id=AWS_IOT_CLIENT_ID,
                clean_session=False,
                keep_alive_secs=30
            )

            self.connection.connect().result()
            self.connected = True
            self.logger.info("  Conectado a AWS IoT Core")

        except ImportError:
            self.logger.warning("  SDK de AWS IoT no instalado")
            self.logger.warning("🏝️  AWS IoT deshabilitado - Modo Local")
        except Exception as e:
            self.logger.error(f" Error conectando a AWS IoT: {e}")
            self.logger.warning("🏝️  Continuando en Modo Local")

    def publish_alert(self, payload: dict):
        if not self.connected:
            self.logger.info("🏝️  Modo Local: Alerta NO enviada a AWS")
            return

        try:
            from awscrt import mqtt as mqtt_connection_builder
            
            self.connection.publish(
                topic=AWS_IOT_TOPIC_ALERTAS,
                payload=json.dumps(payload),
                qos=mqtt_connection_builder.QoS.AT_LEAST_ONCE
            )
            self.logger.info("  Alerta enviada a AWS IoT Core")
        except Exception as e:
            self.logger.error(f" Error publicando a AWS IoT: {e}")
