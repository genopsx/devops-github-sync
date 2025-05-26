locals {

  # If either of these two variables are set, then we are running in CI.
  # This is important for choosing the auth method.
  ci = (get_env("ATLANTIS_TERRAFORM_VERSION", "") != "") || (get_env("CI", "") == "true") ? true : false

  module_versions = {
    aws_ecr      = "v1.1.0"
    aws_ecs      = "v1.1.0"
    aws_template = "v1.0.0"
  }

  # Minor versions of providers are enforced.
  provider_versions = {
    aws     = "~> 5.49.0, < 6.0.0"
    archive = "~> 2.4.0, < 3.0.0"
    local   = "~> 2.5.1, < 3.0.0"
    random  = "~> 3.6.1, < 4.0.0"
    github  = "~> 6.2.1, < 7.0.0"
  }

  operating_unit = "as"
  application    = "devops"
  responsible    = "nexar.devops@altium.com"
  accountable    = "leigh.gawne@altium.com"
  department     = "nexar"
}