variable "resourcegroup_name" {
  description = "Name of resource group"
  default     = "development" #"scatterometry-prod"
  type        = string
}

variable "resourcegroup_location" {
  description = "Location of resource group"
  default     = "westeurope"
  type        = string
}

variable "tags" {
  description = "Tags applied to common resources"
  default = {
    "BillTo"        = "GRAS"
    "ContactPerson" = "PAKO"
    "CostCenter"    = "18099901"
    "CostCenter2"   = "missing tag value"
    "Department"    = "GRAS-ADM"
    "MacoTask"      = "730"
    "MacoTask2"     = "missing tag value"
    "Owner"         = "JOSL"
    "Type"          = "GRAS"
  }
}
