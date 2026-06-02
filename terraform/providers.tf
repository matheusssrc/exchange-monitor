provider "aws" {
  region = var.aws_region

  # Schematic only — never applied. Skip credential/metadata lookups so that
  # `terraform validate` works without real AWS credentials.
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true

  default_tags {
    tags = {
      Project   = "trillia-exchange-monitor"
      ManagedBy = "terraform"
      Owner     = "Matheus"
    }
  }
}
