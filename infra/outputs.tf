# =============================================================================
# Outputs - Observatie Onderzoek Azure Infrastructure
# =============================================================================

# -----------------------------------------------------------------------------
# Resource Group
# -----------------------------------------------------------------------------

output "resource_group_name" {
  description = "Naam van de aangemaakte resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "ID van de aangemaakte resource group"
  value       = azurerm_resource_group.main.id
}

# -----------------------------------------------------------------------------
# Virtual Machines
# -----------------------------------------------------------------------------

output "vm_financieel_id" {
  description = "ID van VM-FinancieleAdministratie"
  value       = azurerm_linux_virtual_machine.financieel.id
}

output "vm_financieel_public_ip" {
  description = "Publiek IP-adres van VM-FinancieleAdministratie"
  value       = azurerm_public_ip.financieel.ip_address
}

output "vm_klantregistratie_id" {
  description = "ID van VM-Klantregistratie"
  value       = azurerm_linux_virtual_machine.klantregistratie.id
}

output "vm_klantregistratie_public_ip" {
  description = "Publiek IP-adres van VM-Klantregistratie"
  value       = azurerm_public_ip.klantregistratie.ip_address
}

output "vm_orderverwerking_id" {
  description = "ID van VM-Orderverwerking"
  value       = azurerm_linux_virtual_machine.orderverwerking.id
}

output "vm_orderverwerking_public_ip" {
  description = "Publiek IP-adres van VM-Orderverwerking"
  value       = azurerm_public_ip.orderverwerking.ip_address
}

output "vm_rapportage_id" {
  description = "ID van VM-Rapportage"
  value       = azurerm_linux_virtual_machine.rapportage.id
}

output "vm_rapportage_public_ip" {
  description = "Publiek IP-adres van VM-Rapportage"
  value       = azurerm_public_ip.rapportage.ip_address
}

output "vm_authenticatie_id" {
  description = "ID van VM-Authenticatie (heeft connectiviteitsprobleem)"
  value       = azurerm_linux_virtual_machine.authenticatie.id
}

output "vm_authenticatie_public_ip" {
  description = "Publiek IP-adres van VM-Authenticatie"
  value       = azurerm_public_ip.authenticatie.ip_address
}

# -----------------------------------------------------------------------------
# Network Security Groups
# -----------------------------------------------------------------------------

output "nsg_financieel_id" {
  description = "ID van NSG-Financieel"
  value       = azurerm_network_security_group.financieel.id
}

output "nsg_klantregistratie_id" {
  description = "ID van NSG-Klantregistratie"
  value       = azurerm_network_security_group.klantregistratie.id
}

output "nsg_orderverwerking_id" {
  description = "ID van NSG-Orderverwerking"
  value       = azurerm_network_security_group.orderverwerking.id
}

output "nsg_rapportage_id" {
  description = "ID van NSG-Rapportage"
  value       = azurerm_network_security_group.rapportage.id
}

output "nsg_authenticatie_id" {
  description = "ID van NSG-Authenticatie (ontbreekt SSH/RDP regels)"
  value       = azurerm_network_security_group.authenticatie.id
}

# -----------------------------------------------------------------------------
# Storage
# -----------------------------------------------------------------------------

output "storage_account_name" {
  description = "Naam van het storage account"
  value       = azurerm_storage_account.main.name
}

output "storage_account_primary_blob_endpoint" {
  description = "Primary blob endpoint van het storage account"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}

output "knowledge_base_container_name" {
  description = "Naam van de knowledge base container"
  value       = azurerm_storage_container.knowledge_base.name
}

# -----------------------------------------------------------------------------
# Network
# -----------------------------------------------------------------------------

output "virtual_network_id" {
  description = "ID van het virtuele netwerk"
  value       = azurerm_virtual_network.main.id
}

output "subnet_id" {
  description = "ID van het subnet"
  value       = azurerm_subnet.main.id
}

# -----------------------------------------------------------------------------
# Scenario Info
# -----------------------------------------------------------------------------

output "scenario_problem_description" {
  description = "Beschrijving van het probleem voor het observatie-onderzoek"
  value       = <<-EOT
    
    =====================================================================
    SCENARIO PROBLEEM - OBSERVATIE ONDERZOEK
    =====================================================================
    
    De VM 'VM-Authenticatie' heeft geen toegang via SSH of RDP.
    
    OORZAAK: De Network Security Group 'NSG-Authenticatie' heeft geen 
    inbound regels die SSH (poort 22) of RDP (poort 3389) toestaan.
    
    OPLOSSING: Voeg de volgende security regels toe aan NSG-Authenticatie:
    - AllowSSH: Poort 22, van toegestane IP-adressen
    - AllowRDP: Poort 3389, van toegestane IP-adressen
    
    Dit probleem moet door de deelnemer worden opgelost met behulp van
    het agentic AI-prototype.
    =====================================================================
  EOT
}
