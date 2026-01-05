# Observatie Onderzoek Azure Sandbox

## Overview

This repository contains a scenario-driven Azure sandbox for observation research, designed to simulate and manage a cloud environment for the North River organization. The project uses a multi-agent architecture (helper, knowledge, network, resource agents) and Terraform for provisioning Azure resources.

---

## Contents

- **infra/**: Terraform scripts for creating VMs, NSGs, storage, and policies
- **mcat_agents/**: Python agents and tools
  - **agents/**: Helper, knowledge, network, resource agents
  - **tools/**: Agent-specific tools (cloud_resources, ai_search, blob_storage, network_functions)
- **tests/**: Test files for agent workflows and functionality
- **requirements.txt**: Python dependencies

---

## Architecture

### Agents

- **helper_agent**: Orchestrates all other agents, answers user questions
- **knowledge_agent**: Searches the knowledge base (AI Search, Blob Storage)
- **network_agent**: Manages and inspects Network Security Groups (NSGs)
- **resource_agent**: Manages Azure resources (VMs, resource groups, status)

### Tools

- **cloud_resources.py**: Resource management (VMs, resource groups, status)
- **ai_search.py**: AI Search functionality for knowledge documents
- **blob_storage.py**: Blob Storage management (read, write, create, delete)
- **network_functions.py**: NSG management (rules, ports, associations, changes)

---

## Installation

1. **Clone the repository**
   ```sh
   git clone <repo-url>
   cd observatie-onderzoek
   ```
2. **Install Python dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Initialize Terraform**
   ```sh
   cd infra
   terraform init
   terraform plan
   terraform apply
   ```
4. **Configure .env**
   Create a `.env` file in the root with:
   ```env
   AZURE_STORAGE_ACCOUNT_NAME=northriverknowledgebase
   AZURE_STORAGE_ACCOUNT_KEY=<your_access_key>
   AZURE_STORAGE_ACCOUNT_URL=https://northriverknowledgebase.blob.core.windows.net
   # Add other secrets as needed
   ```
   **Note:** Never commit your `.env` or secrets to Git.

---

## Usage

- **Call agents**: Via Python scripts or through the helper_agent
- **Knowledge base**: Manage documents via Blob Storage tools
- **Network troubleshooting**: Use NSG tools for connectivity checks and rule management
- **Resource management**: VM status, resource groups, start/stop actions

---

## Security

- **No hardcoded credentials**: All secrets are loaded via environment variables
- **.env in `.gitignore`**: Ensure your `.env` file is never committed
- **Approval modes**: Write actions (e.g., adding/removing NSG rules, modifying blobs) require explicit approval

---

## Testing

- **Test files**: Unit tests for agent workflows are in `tests/`
- **Run tests**:
  ```sh
  python -m unittest discover tests
  ```

---

## Scenario

This project is designed for observation research in an Azure environment. The North River organization has multiple VMs (FinancieleAdministratie, Klantregistratie, Orderverwerking, Rapportage, Authenticatie) and a knowledge base. Agents assist with troubleshooting, knowledge management, and resource management.

---

## Contact & Support

For questions or support: contact the MCAT team.

---

## License

MIT License
