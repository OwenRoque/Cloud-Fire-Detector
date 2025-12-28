# ============================================================================
# Outputs - AWS IoT Core
# ============================================================================
output "iot_endpoint" {
  description = "Endpoint AWS IoT Core (MQTT over TLS)"
  value       = data.aws_iot_endpoint.endpoint.endpoint_address
}

output "iot_thing_name" {
  description = "Thing Name del Nodo Fog"
  value       = aws_iot_thing.fog_node.name
}

output "iot_certificate_arn" {
  description = "ARN del certificado IoT"
  value       = aws_iot_certificate.cert.arn
}

output "iot_certificate_pem" {
  description = "Certificado PEM (guardar como certificate.pem.crt)"
  value       = aws_iot_certificate.cert.certificate_pem
  sensitive   = true
}

output "iot_private_key" {
  description = "Clave privada (guardar como private.pem.key)"
  value       = aws_iot_certificate.cert.private_key
  sensitive   = true
}

output "iot_public_key" {
  description = "Clave pública"
  value       = aws_iot_certificate.cert.public_key
  sensitive   = true
}

# ============================================================================
# Outputs - Greengrass
# ============================================================================
output "greengrass_role_alias" {
  description = "Role Alias para Greengrass Core"
  value       = aws_iot_role_alias.greengrass_alias.alias
}

output "greengrass_artifacts_bucket" {
  description = "Bucket S3 para artefactos de Greengrass"
  value       = aws_s3_bucket.greengrass_artifacts.bucket
}

output "greengrass_config_s3_uri" {
  description = "URI de S3 con la configuración del Fog Processor"
  value       = "s3://${aws_s3_bucket.greengrass_artifacts.bucket}/${aws_s3_object.fog_config.key}"
}

# ============================================================================
# Outputs - Storage y Notificaciones
# ============================================================================

output "s3_bucket_images" {
  description = "Bucket para imágenes de incendio"
  value       = aws_s3_bucket.fire_images.bucket
}

output "sns_topic_arn" {
  description = "SNS Topic de alertas"
  value       = aws_sns_topic.alerts.arn
}

output "api_endpoint" {
  description = "API Gateway endpoint (opcional)"
  value       = aws_apigatewayv2_api.api.api_endpoint
}
