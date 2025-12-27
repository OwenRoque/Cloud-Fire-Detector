# Guarda solo incendios confirmados
# Acceso desde Lambda fire_event_handler
# Escala automáticamente (PAY_PER_REQUEST)
resource "aws_dynamodb_table" "fire_events" {
  name         = "fire-events"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "event_id"

  attribute {
    name = "event_id"
    type = "S"
  }

  tags = {
    Name = "Fire Detection Events"
  }
}
