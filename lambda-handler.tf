# Recibe evento IoT
# Guarda en DynamoDB
# Publica en SNS

resource "aws_lambda_function" "fire_handler" {
  function_name = "fire-event-handler"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "fire_handler.lambda_handler"
  runtime       = "python3.11"

  filename         = "lambda/fire_handler.zip"
  source_code_hash = filebase64sha256("lambda/fire_handler.zip")

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.alerts.arn
      TABLE_NAME    = "fire-events"
    }
  }
}
