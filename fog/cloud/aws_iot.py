import json
from awscrt import mqtt as mqtt_connection_builder
from awsiot import mqtt_connection_builder as iot_builder
from config.settings import *

class AWSIoTClient:
    def __init__(self, logger):
        self.logger = logger
        self.connection = None
        self.connected = False

    def connect(self):
        if not AWS_IOT_ENABLED:
            return

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

    def publish_alert(self, payload: dict):
        if not self.connected:
            return

        self.connection.publish(
            topic=AWS_IOT_TOPIC_ALERTAS,
            payload=json.dumps(payload),
            qos=mqtt_connection_builder.QoS.AT_LEAST_ONCE
        )
