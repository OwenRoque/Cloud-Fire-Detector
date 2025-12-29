# ============================================================================
# AWS IoT Greengrass v2 - Fog Computing Layer (Infraestructura IAM)
# ============================================================================
# NOTA: Los componentes y deployments de Greengrass v2 se gestionan mediante:
#   1. AWS CLI (instalación manual del Core Device)
#   2. Scripts de automatización (ver /fog/setup_greengrass.sh)
# Este archivo crea SOLO la infraestructura IAM necesaria.
# ============================================================================

# ============================================================================
# IAM Role para Greengrass Core Device
# ============================================================================
resource "aws_iam_role" "greengrass_core_role" {
  name = "GreengrassCoreTokenExchangeRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "credentials.iot.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "greengrass_core_policy" {
  role       = aws_iam_role.greengrass_core_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGreengrassResourceAccessRolePolicy"
}

# ============================================================================
# IoT Role Alias para credenciales temporales
# ============================================================================
resource "aws_iot_role_alias" "greengrass_alias" {
  alias    = "GreengrassCoreTokenExchangeRoleAlias"
  role_arn = aws_iam_role.greengrass_core_role.arn
}

# Política adicional para IoT Core + DynamoDB + S3
resource "aws_iam_role_policy" "greengrass_additional" {
  name = "GreengrassAdditionalPermissions"
  role = aws_iam_role.greengrass_core_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Publish",
          "iot:Subscribe",
          "iot:Connect",
          "iot:Receive"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.fire_images.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.fire_events.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# ============================================================================
# Thing Group para organizar nodos Fog
# ============================================================================
resource "aws_iot_thing_group" "fog_nodes" {
  name = "fog-computing-nodes"

  properties {
    attribute_payload {
      attributes = {
        environment = "production"
        type        = "fog-gateway"
      }
    }
  }
}

resource "aws_iot_thing_group_membership" "fog_node_membership" {
  thing_name       = aws_iot_thing.fog_node.name
  thing_group_name = aws_iot_thing_group.fog_nodes.name
}

# ============================================================================
# S3 Bucket para artefactos y configuración de Greengrass
# ============================================================================
resource "aws_s3_bucket" "greengrass_artifacts" {
  bucket = "fire-detection-greengrass-artifacts-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "greengrass_artifacts_block" {
  bucket = aws_s3_bucket.greengrass_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ============================================================================
# Subir configuración del Fog Processor a S3
# ============================================================================
resource "aws_s3_object" "fog_config" {
  bucket = aws_s3_bucket.greengrass_artifacts.bucket
  key    = "config/fog_config.json"
  content = jsonencode({
    sensorCameraMap = var.sensor_camera_map
    thresholds = {
      temperature = 60.0
      light       = 800.0
      humidity    = 30.0
    }
    local_mqtt_broker = var.fog_mqtt_broker_ip
    local_mqtt_port   = 1883
    iot_endpoint      = data.aws_iot_endpoint.endpoint.endpoint_address
    aws_region        = var.aws_region
  })
  content_type = "application/json"
}

# ============================================================================
# Data Source: AWS IoT Endpoint
# ============================================================================
data "aws_iot_endpoint" "endpoint" {
  endpoint_type = "iot:Data-ATS"
}
