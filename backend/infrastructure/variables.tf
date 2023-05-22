variable "resource_group_name" {
  description = "Name of resource group"
  default     = "scatterometry" #"scatterometry-prod"
  type        = string
}

variable "location" {
  description = "Location of resource group"
  default     = "northeurope"
  type        = string
}

variable "tags" {
  description = "Tags applied to common resources"
  default = {
    "BillTo"        = "GRAS"
    "ContactPerson" = "THNS"
    "CostCenter"    = "18099901"
    "CostCenter2"   = "missing tag value"
    "Department"    = "GRAS-ADM"
    "MacoTask"      = "730"
    "MacoTask2"     = "missing tag value"
    "Owner"         = "JOSL"
    "Type"          = "GRAS"
  }
}

# Database
variable "postgres_server_username" {
  default = "scatterometry_db_user"
}

variable "postgres_storage_mb" {
  default = 524288
  type    = number
}
