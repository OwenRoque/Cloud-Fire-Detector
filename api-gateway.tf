resource "aws_apigatewayv2_api" "api" {
  name          = "fire-detection-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.fire_handler.invoke_arn
}

resource "aws_apigatewayv2_route" "route" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /fire"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}
