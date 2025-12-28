# Se suscribe a SNS
# Llama a Telegram Bot API

resource "aws_lambda_function" "telegram" {
  function_name = "telegram-notifier"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "telegram.lambda_handler"
  runtime       = "python3.11"

  filename         = "lambda/telegram.zip"
  source_code_hash = filebase64sha256("lambda/telegram.zip")

  environment {
    variables = {
      TELEGRAM_BOT_TOKEN = var.telegram_bot_token
      TELEGRAM_CHAT_ID   = var.telegram_chat_id
    }
  }
}

resource "aws_sns_topic_subscription" "telegram_sub" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.telegram.arn
}

resource "aws_lambda_permission" "sns_permission" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telegram.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.alerts.arn
}
