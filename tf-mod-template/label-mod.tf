### This file is synced from the devops-github-sync repository.
### Changes should be made there and synced across.

module "label" {
  # tflint-ignore: terraform_module_pinned_source
  source = "git::git@github.com:genopsx/tf-mod-label.git?ref=v2.0.1"

  department     = var.department
  responsible    = var.responsible
  operating_unit = var.operating_unit
  accountable    = var.accountable
  application    = var.application
  service        = var.service
  environment    = var.environment
  region         = var.region
  prefix         = var.prefix
  suffix         = var.suffix
  backup         = var.backup
  tags           = var.tags
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = null
}

variable "responsible" {
  description = "Email of technical person or a team responsible for the resource."
  type        = string
  default     = "nexar.devops@altium.com"

  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.responsible))
    error_message = "Invalid email address."
  }
}

variable "department" {
  description = <<-EOT
    Business entity within an organization that owns a resource.
    Other values than listed are not allowed.
  EOT
  type        = string
  default     = "nexar"

  validation {
    condition     = contains(["a365", "dss", "cad", "nexar", "it"], var.department)
    error_message = "Allowed values: `a365`, `dss`, `cad`, `nexar`, `it`."
  }
}

variable "accountable" {
  description = "Email of rerson responsible for business and budget of the resource."
  type        = string
  default     = "leigh.gawne@altium.com"

  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.accountable))
    error_message = "Invalid email address."
  }
}

variable "operating_unit" {
  description = <<-EOT
    Business entity within an organization that owns a resource.
    Other values than listed are not allowed.
    Octopart is `search` for the `Search R&D` operating unit.
    Nexar is `as` for the `Application Services R&D` operating unit.
  EOT
  type        = string

  validation {
    condition     = contains(["it", "das", "cad", "pcs", "search", "ipma", "as", "dsc"], var.operating_unit)
    error_message = "Allowed values: `it`, `das`, `cad`, `pcs`, `search`, `ipma`, `as`, `dsa`."
  }
}

variable "application" {
  description = <<-EOT
    Application is a software program that a user interacts with and performs a
    wide range of operations. Some functionalities of an application can be
    delivered as services.  If multiple applications use a resource, then use
    shared. Other values than listed are allowed.
  EOT
  type        = string
}

variable "service" {
  description = <<-EOT
    Service (or microservice) is not visible by a user directly. Usually services
    are single task focused and are part of a bigger system.  If multiple services
    use a resource, then use shared. Other values than listed are allowed.
  EOT
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string

  validation {
    condition     = contains(["prod", "uat", "test", "dev"], var.environment)
    error_message = "Valid values for `env` are: `prod`, `uat`, `test`, `dev`."
  }
}

variable "backup" {
  description = "Whether to enable AWS Backups for this item"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags to add to all resources"
  default     = {}
  type        = map(any)
}

variable "prefix" {
  description = "Custom application name prefix"
  type        = string
  default     = null
}

variable "suffix" {
  description = "Custom application name suffix"
  type        = string
  default     = null
}
