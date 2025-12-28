output "iot_endpoint" {
  description = "Endpoint AWS IoT Core (MQTT)"
  value       = data.aws_iot_endpoint.endpoint_address
}

output "iot_thing_name" {
  description = "Thing Name para el teléfono (FOG)"
  value       = aws_iot_thing.phone.name
}

output "iot_certificate_arn" {
  description = "ARN del certificado IoT"
  value       = aws_iot_certificate.cert.arn
}

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