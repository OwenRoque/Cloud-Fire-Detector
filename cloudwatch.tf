# (Opcional)
# Detecta fallos en procesamiento de alertas
# Avisa si Lambda falla

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "fire-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1

  dimensions = {
    FunctionName = aws_lambda_function.fire_handler.function_name
  }

  alarm_description = "Errores en Lambda fire_event_handler"
}

# Se activa cuando hay incendio real
# Refuerza monitoreo del sistema

resource "aws_cloudwatch_metric_alarm" "fire_detected" {
  alarm_name          = "fire-detected-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "NumberOfMessagesPublished"
  namespace           = "AWS/SNS"
  period              = 60
  statistic           = "Sum"
  threshold           = 0

  dimensions = {
    TopicName = aws_sns_topic.alerts.name
  }

  alarm_description = "Incendio detectado (SNS activado)"
}
