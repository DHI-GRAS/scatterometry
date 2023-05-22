terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.42.0"
    }
    local = {}
  }
}
provider "azurerm" {
  features {}
}


# Resource Group
resource "azurerm_resource_group" "resource_group" {
  name     = var.resource_group_name
  location = var.location

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

resource "azurerm_postgresql_flexible_server" "postgres_server" {
  name                = "scatterometry"
  resource_group_name = azurerm_resource_group.resource_group.name
  location            = var.location
  sku_name            = "GP_Standard_D2ds_v4"
  zone                = "1"

  storage_mb             = var.postgres_storage_mb
  version                = "14"
  administrator_login    = var.postgres_server_username
  administrator_password = random_password.postgres_server_password.result

  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "dhi_vpn" {
  name             = "dhi-vpn"
  server_id        = azurerm_postgresql_flexible_server.postgres_server.id
  start_ip_address = "193.3.62.162"
  end_ip_address   = "193.3.62.162"
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

resource "azurerm_postgresql_flexible_server_database" "scatterometry" {
  name      = "scatterometry"
  server_id = azurerm_postgresql_flexible_server.postgres_server.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

output "postgres_server_password" {
  value     = random_password.postgres_server_password.result
  sensitive = true
}


# Blob Storage
resource "azurerm_storage_account" "storage_account" {
  name                             = "scatterometry"
  resource_group_name              = azurerm_resource_group.resource_group.name
  location                         = var.location
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
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
  os_type             = "Linux"
  sku_name            = "Y1"

  tags = var.tags
}

resource "azurerm_linux_function_app" "scatterometry_api" {
  name                    = "scatterometry-api"
  location                = var.location
  resource_group_name     = azurerm_resource_group.resource_group.name
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
