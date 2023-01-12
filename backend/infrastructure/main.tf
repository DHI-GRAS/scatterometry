terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.38.0"
    }
    local = {}
  }
}
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "resourcegroup" {
  name     = "development"
  location = "westeurope"

  tags = {
    "BillTo" = "GRAS"
    "Client" = "GRAS-general-purpose"
    "Owner"  = "JOSL"
  }
}

data "azurerm_subscription" "current" {}

resource "random_password" "postgres_server_password" {
  length           = 16
  special          = true
  override_special = "_"
}

variable "postgres_server_username" {
  default = "dnageneral"
}

resource "azurerm_postgresql_flexible_server" "postgres_server" {
  name                = "dna"
  resource_group_name = azurerm_resource_group.resourcegroup.name
  location            = "northeurope"
  sku_name            = "GP_Standard_D2ds_v4"
  zone                = "1"

  storage_mb = 131072
  version    = "14"
  #   administrator_login    = var.postgres_server_username
  #   administrator_password = random_password.postgres_server_password.result

  tags = {
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

resource "azurerm_postgresql_flexible_server_configuration" "add_azure_extensions" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.postgres_server.id
  value     = "postgis,timescaledb"
}

resource "azurerm_postgresql_flexible_server_configuration" "add_shared_preload_libraries" {
  name      = "shared_preload_libraries"
  server_id = azurerm_postgresql_flexible_server.postgres_server.id
  value     = "timescaledb"
}

# resource "azurerm_postgresql_database" "scatterometry_database" {
#   name                = "scatterometry"
#   resource_group_name = azurerm_resource_group.resourcegroup.name
#   server_name         = azurerm_postgresql_flexible_server.postgres_server.name
#   charset             = "UTF8"
#   collation           = "English_United States.1252"
# }
