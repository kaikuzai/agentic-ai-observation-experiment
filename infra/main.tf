# =============================================================================
# Observatie Onderzoek - Azure Infrastructure
# =============================================================================
# Dit Terraform configuratie zet de cloud omgeving op voor het observatie-
# onderzoek naar de interactie tussen MCAT-leden en het agentic AI-prototype.
# =============================================================================

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# =============================================================================
# Resource Group
# =============================================================================

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = var.tags
}

# =============================================================================
# Virtual Network & Subnet
# =============================================================================

resource "azurerm_virtual_network" "main" {
  name                = "${var.prefix}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

resource "azurerm_subnet" "main" {
  name                 = "${var.prefix}-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# =============================================================================
# Network Security Groups (NSGs)
# =============================================================================

# NSG-Financieel - Voor VM-FinancieleAdministratie
resource "azurerm_network_security_group" "financieel" {
  name                = "NSG-Financieel"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

resource "azurerm_network_security_rule" "financieel_ssh" {
  name                        = "AllowSSH"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefixes     = var.allowed_ip_addresses
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.financieel.name
}

# NSG-Klantregistratie - Voor VM-Klantregistratie
resource "azurerm_network_security_group" "klantregistratie" {
  name                = "NSG-Klantregistratie"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

resource "azurerm_network_security_rule" "klantregistratie_ssh" {
  name                        = "AllowSSH"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefixes     = var.allowed_ip_addresses
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.klantregistratie.name
}

# NSG-Orderverwerking - Voor VM-Orderverwerking
resource "azurerm_network_security_group" "orderverwerking" {
  name                = "NSG-Orderverwerking"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

resource "azurerm_network_security_rule" "orderverwerking_ssh" {
  name                        = "AllowSSH"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefixes     = var.allowed_ip_addresses
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.orderverwerking.name
}

# NSG-Rapportage - Voor VM-Rapportage
resource "azurerm_network_security_group" "rapportage" {
  name                = "NSG-Rapportage"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

resource "azurerm_network_security_rule" "rapportage_ssh" {
  name                        = "AllowSSH"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefixes     = var.allowed_ip_addresses
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.main.name
  network_security_group_name = azurerm_network_security_group.rapportage.name
}

# NSG-Authenticatie - Voor VM-Authenticatie (DEZE HEEFT GEEN SSH/RDP REGELS - SIMULATIE PROBLEEM)
resource "azurerm_network_security_group" "authenticatie" {
  name                = "NSG-Authenticatie"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

# OPMERKING: De SSH/RDP regels voor NSG-Authenticatie zijn opzettelijk weggelaten
# om het scenario te simuleren waarbij toegang tot een VM niet werkt.
# De deelnemer moet dit probleem troubleshooten met het agentic AI-prototype.

# =============================================================================
# Public IP Addresses
# =============================================================================

resource "azurerm_public_ip" "financieel" {
  name                = "pip-vm-financieel"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

resource "azurerm_public_ip" "klantregistratie" {
  name                = "pip-vm-klantregistratie"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

resource "azurerm_public_ip" "orderverwerking" {
  name                = "pip-vm-orderverwerking"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

resource "azurerm_public_ip" "rapportage" {
  name                = "pip-vm-rapportage"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

resource "azurerm_public_ip" "authenticatie" {
  name                = "pip-vm-authenticatie"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

# =============================================================================
# Network Interfaces
# =============================================================================

resource "azurerm_network_interface" "financieel" {
  name                = "nic-vm-financieel"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.financieel.id
  }

  tags = var.tags
}

resource "azurerm_network_interface_security_group_association" "financieel" {
  network_interface_id      = azurerm_network_interface.financieel.id
  network_security_group_id = azurerm_network_security_group.financieel.id
}

resource "azurerm_network_interface" "klantregistratie" {
  name                = "nic-vm-klantregistratie"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.klantregistratie.id
  }

  tags = var.tags
}

resource "azurerm_network_interface_security_group_association" "klantregistratie" {
  network_interface_id      = azurerm_network_interface.klantregistratie.id
  network_security_group_id = azurerm_network_security_group.klantregistratie.id
}

resource "azurerm_network_interface" "orderverwerking" {
  name                = "nic-vm-orderverwerking"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.orderverwerking.id
  }

  tags = var.tags
}

resource "azurerm_network_interface_security_group_association" "orderverwerking" {
  network_interface_id      = azurerm_network_interface.orderverwerking.id
  network_security_group_id = azurerm_network_security_group.orderverwerking.id
}

resource "azurerm_network_interface" "rapportage" {
  name                = "nic-vm-rapportage"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.rapportage.id
  }

  tags = var.tags
}

resource "azurerm_network_interface_security_group_association" "rapportage" {
  network_interface_id      = azurerm_network_interface.rapportage.id
  network_security_group_id = azurerm_network_security_group.rapportage.id
}

resource "azurerm_network_interface" "authenticatie" {
  name                = "nic-vm-authenticatie"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.authenticatie.id
  }

  tags = var.tags
}

resource "azurerm_network_interface_security_group_association" "authenticatie" {
  network_interface_id      = azurerm_network_interface.authenticatie.id
  network_security_group_id = azurerm_network_security_group.authenticatie.id
}

# =============================================================================
# Virtual Machines
# =============================================================================

# VM-FinancieleAdministratie – facturatie, betalingen, boekhouding
resource "azurerm_linux_virtual_machine" "financieel" {
  name                = "VM-FinancieleAdministratie"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.financieel.id
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(var.tags, {
    purpose = "facturatie, betalingen, boekhouding"
    vm_role = "financieel"
  })
}

# VM-Klantregistratie – klantdata, accounts, onboarding
resource "azurerm_linux_virtual_machine" "klantregistratie" {
  name                = "VM-Klantregistratie"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.klantregistratie.id
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(var.tags, {
    purpose = "klantdata, accounts, onboarding"
    vm_role = "klantregistratie"
  })
}

# VM-Orderverwerking – verwerken en afhandelen van orders
resource "azurerm_linux_virtual_machine" "orderverwerking" {
  name                = "VM-Orderverwerking"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.orderverwerking.id
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(var.tags, {
    purpose = "verwerken en afhandelen van orders"
    vm_role = "orderverwerking"
  })
}

# VM-Rapportage – managementinformatie en dashboards
resource "azurerm_linux_virtual_machine" "rapportage" {
  name                = "VM-Rapportage"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.rapportage.id
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(var.tags, {
    purpose = "managementinformatie en dashboards"
    vm_role = "rapportage"
  })
}

# VM-Authenticatie – inloggen, autorisatie, toegangsbeheer
# DEZE VM HEEFT EEN PROBLEEM: NSG blokkeert SSH/RDP verkeer
resource "azurerm_linux_virtual_machine" "authenticatie" {
  name                = "VM-Authenticatie"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.authenticatie.id
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  tags = merge(var.tags, {
    purpose = "inloggen, autorisatie, toegangsbeheer"
    vm_role = "authenticatie"
  })
}

# =============================================================================
# Storage Account & Blob Container (Knowledge Base)
# =============================================================================

resource "azurerm_storage_account" "main" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = var.tags
}

resource "azurerm_storage_container" "knowledge_base" {
  name                  = "north-river-knowledge-base"
  storage_account_id    = azurerm_storage_account.main.id
  container_access_type = "private"
}
