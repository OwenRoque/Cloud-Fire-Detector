resource "aws_iot_thing" "jetson" {
  name = "jetson-001"
}

resource "aws_iot_policy" "iot_policy" {
  name = "fire-detection-iot-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "iot:Connect",
        "iot:Publish"
      ]
      Resource = "*"
    }]
  })
}

resource "aws_iot_certificate" "cert" {
  active = true
}

resource "aws_iot_policy_attachment" "policy_attach" {
  policy = aws_iot_policy.iot_policy.name
  target = aws_iot_certificate.cert.arn
}

resource "aws_iot_thing_principal_attachment" "thing_attach" {
  thing     = aws_iot_thing.jetson.name
  principal = aws_iot_certificate.cert.arn
}
