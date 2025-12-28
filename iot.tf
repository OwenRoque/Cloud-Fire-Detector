# ============================================================================
# IoT Thing - Nodo Fog (Laptop B con Greengrass)
# ============================================================================
resource "aws_iot_thing" "fog_node" {
  name = "fog-node-001"

  attributes = {
    type     = "fog-gateway"
    location = "planta-industrial"
  }
}

# ============================================================================
# IoT Policy - Permisos para Fog Node (Publish + Subscribe + Receive)
# ============================================================================
resource "aws_iot_policy" "iot_policy" {
  name = "fire-detection-iot-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect"
        ]
        Resource = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:client/$${iot:Connection.Thing.ThingName}"
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Publish"
        ]
        Resource = [
          "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/industria/*/alertas",
          "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/industria/*/sensores"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Subscribe"
        ]
        Resource = [
          "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topicfilter/industria/*/comandos"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Receive"
        ]
        Resource = [
          "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/industria/*/comandos"
        ]
      }
    ]
  })
}

# Data sources para ARNs dinámicos
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# ============================================================================
# Certificado X.509 para autenticación mTLS
# ============================================================================
resource "aws_iot_certificate" "cert" {
  active = true
}

resource "aws_iot_policy_attachment" "policy_attach" {
  policy = aws_iot_policy.iot_policy.name
  target = aws_iot_certificate.cert.arn
}

resource "aws_iot_thing_principal_attachment" "thing_attach" {
  thing     = aws_iot_thing.fog_node.name
  principal = aws_iot_certificate.cert.arn
}

# ============================================================================
# IoT Rule - Procesar alertas de incendio desde MQTT → Lambda
# ============================================================================
resource "aws_iot_topic_rule" "fire_alert_rule" {
  name        = "fire_alert_processor"
  description = "Detecta alertas de incendio confirmadas y las envía a Lambda"
  enabled     = true
  sql         = "SELECT * FROM 'industria/+/alertas' WHERE fuego_detectado = true"
  sql_version = "2016-03-23"

  lambda {
    function_arn = aws_lambda_function.fire_handler.arn
  }
}

# Permiso para que IoT Rule invoque Lambda
resource "aws_lambda_permission" "iot_invoke_lambda" {
  statement_id  = "AllowIoTRuleInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fire_handler.function_name
  principal     = "iot.amazonaws.com"
  source_arn    = aws_iot_topic_rule.fire_alert_rule.arn
}
