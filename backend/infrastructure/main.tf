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


# Resource Group
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


# Database
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
  location            = var.resources_location
  sku_name            = "GP_Standard_D2ds_v4"
  zone                = "1"

  storage_mb = 131072
  version    = "14"
  #   administrator_login    = var.postgres_server_username
  #   administrator_password = random_password.postgres_server_password.result

  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_configuration" "add_azure_extensions" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.postgres_server.id
  value     = "postgis,timescaledb"
}

resource "azurerm_postgresql_flexible_server_configuration" "add_shared_preload_libraries" {
  name      = "shared_preload_libraries"
  server_id = azurerm_postgresql_flexible_server.postgres_server.id
  value     = "pg_cron,pg_stat_statements,timescaledb"
}

# resource "azurerm_postgresql_database" "scatterometry_database" {
#   name                = "scatterometry"
#   resource_group_name = azurerm_resource_group.resourcegroup.name
#   server_name         = azurerm_postgresql_flexible_server.postgres_server.name
#   charset             = "UTF8"
#   collation           = "English_United States.1252"
# }


# Blob Storage
resource "azurerm_storage_account" "storage_account" {
  name                             = "scatterometry"
  resource_group_name              = azurerm_resource_group.resourcegroup.name
  location                         = var.resources_location
  cross_tenant_replication_enabled = false
  account_tier                     = "Standard"
  account_replication_type         = "LRS"
  min_tls_version                  = "TLS1_2"

  tags = var.tags
}

resource "azurerm_storage_container" "storage_container" {
  name                  = "queryresults"
  storage_account_name  = azurerm_storage_account.storage_account.name
  container_access_type = "blob"
}


# Azure function
resource "azurerm_service_plan" "scatterometry_api" {
  name                = "scatterometry-api"
  location            = var.resources_location
  resource_group_name = azurerm_resource_group.resourcegroup.name
  os_type             = "Linux"
  sku_name            = "Y1"

  tags = var.tags
}

resource "azurerm_linux_function_app" "scatterometry_api" {
  name                    = "scatterometry-api"
  location                = var.resources_location
  resource_group_name     = azurerm_resource_group.resourcegroup.name
  builtin_logging_enabled = true
  client_certificate_mode = "Required"
  https_only              = true

  service_plan_id = azurerm_service_plan.scatterometry_api.id

  storage_account_name       = azurerm_storage_account.storage_account.name
  storage_account_access_key = azurerm_storage_account.storage_account.primary_access_key

  tags = var.tags

  site_config {
    app_scale_limit = 200
    always_on       = false
    ftps_state      = "FtpsOnly"


    application_stack {
      python_version = "3.9"
    }

    cors {
      allowed_origins     = ["https://portal.azure.com", ]
      support_credentials = false
    }
  }
}

output "api_url" {
  value = azurerm_linux_function_app.scatterometry_api.default_hostname
}
