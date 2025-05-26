terraform_version_constraint  = ">= 1.7.5, < 1.8.0"
terragrunt_version_constraint = ">= 0.58.2, < 0.59.0"

locals {
  # Prefix for all workspace names in terraform cloud
  tfc_workspace_prefix = null

  common_vars      = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  env_vars         = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  account_vars     = read_terragrunt_config(find_in_parent_folders("account.hcl"))
  region_vars      = read_terragrunt_config(find_in_parent_folders("region.hcl"))
  application_vars = read_terragrunt_config(find_in_parent_folders("application.hcl"))

  aws_account_id = local.account_vars.locals.aws_account_id
  aws_profile    = local.account_vars.locals.aws_profile
  aws_region     = local.region_vars.locals.aws_region

  tfc_organization = "nexar"
  _prefix          = local.tfc_workspace_prefix != null ? "${local.tfc_workspace_prefix}-" : ""
  tfc_workspace    = "${local._prefix}${replace(path_relative_to_include(), "/", "-")}-${local.account_vars.locals.aws_account_id}-${local.region_vars.locals.aws_region}"

  provider_versions = local.common_vars.locals.provider_versions
}

inputs = {
  responsible    = local.common_vars.locals.responsible
  accountable    = local.common_vars.locals.accountable
  department     = local.common_vars.locals.department
  operating_unit = local.common_vars.locals.operating_unit
  environment    = local.env_vars.locals.environment
  region         = local.region_vars.locals.aws_region
  application    = (local.application_vars.locals.application != null ?
    local.application_vars.locals.application : local.common_vars.locals.application)
}

# Generate an AWS provider block
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
    provider "aws" {
      region = "${local.aws_region}"
      allowed_account_ids = ["${local.aws_account_id}"]
      %{if local.common_vars.locals.ci == true}
      assume_role {
        role_arn = "arn:aws:iam::${local.aws_account_id}:role/DevOpsIaCRole"
        external_id = "terragrunt-ci"
      }
      %{else}
      profile = "${local.aws_profile}"
      %{endif}
    }
  EOF
}

generate "remote_state" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
    terraform {

      cloud {
        organization = "${local.tfc_organization}"
        workspaces {
          name = "${local.tfc_workspace}"
        }
      }
    }
  EOF
}

generate "provider-versions" {
  path      = "versions.tf"
  if_exists = "overwrite"
  contents  = <<-EOF
    terraform {

      required_providers {
        aws = {
          source  = "hashicorp/aws"
          version = "${local.provider_versions.aws}"
        }
        random = {
          source  = "hashicorp/random"
          version = "${local.provider_versions.random}"
        }
        archive = {
          source  = "hashicorp/archive"
          version = "${local.provider_versions.archive}"
        }
        local = {
          source  = "hashicorp/local"
          version = "${local.provider_versions.local}"
        }
        github = {
          source  = "integrations/github"
          version = "${local.provider_versions.github}"
        }
      }
    }
  EOF
}