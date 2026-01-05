# =============================================================================
# Variables - Observatie Onderzoek Azure Infrastructure
# =============================================================================

variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  sensitive   = true
}

variable "resource_group_name" {
  description = "Naam van de Azure Resource Group"
  type        = string
  default     = "north-river-resource-group"
}

variable "location" {
  description = "Azure regio voor alle resources"
  type        = string
  default     = "westeurope"
}

variable "prefix" {
  description = "Prefix voor resource namen"
  type        = string
  default     = "nordriver"
}

variable "tags" {
  description = "Tags voor alle resources"
  type        = map(string)
  default = {
    project     = "observatie-onderzoek"
    environment = "sandbox"
    team        = "MCAT"
    owner       = "Nord River"
  }
}

variable "allowed_ip_addresses" {
  description = "Lijst van toegestane IP-adressen voor beheertoegang tot VMs"
  type        = list(string)
  default = [
    "203.0.113.10",  # Kantoor Amsterdam
    "203.0.113.20",  # Kantoor Rotterdam
    "198.51.100.50", # VPN Gateway
    "192.0.2.100"    # Remote beheer team
  ]
}

variable "vm_size" {
  description = "Grootte van de virtuele machines"
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Administrator gebruikersnaam voor VMs"
  type        = string
  default     = "azureadmin"
}

variable "ssh_public_key" {
  description = "SSH publieke sleutel voor VM toegang"
  type        = string
  sensitive   = true
}

variable "storage_account_name" {
  description = "Naam van het storage account (moet uniek zijn binnen Azure)"
  type        = string
  default     = "northriverstorageaccount"

  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Storage account naam moet 3-24 karakters lang zijn en alleen kleine letters en cijfers bevatten."
  }
}
