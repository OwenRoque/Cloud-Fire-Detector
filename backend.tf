terraform {
  backend "s3" {
    bucket         = "fire-detection-terraform-state-577272335685"
    key            = "global/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
