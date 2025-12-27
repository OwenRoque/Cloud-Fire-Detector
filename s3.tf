resource "aws_s3_bucket" "fire_images" {
  bucket = "fire-detection-images-577272335685"

  force_destroy = false

  tags = {
    Name = "Fire Detection Images"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3_encrypt" {
  bucket = aws_s3_bucket.fire_images.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
