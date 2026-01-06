# Agentic AI Observation & Validation Sandbox

## Objective

This repository is designed as a flexible testbed for developing, validating, and comparing different agentic AI architectures and responsibilities in a realistic cloud scenario. It enables researchers and developers to:

- Prototype and benchmark multi-agent systems for cloud management and troubleshooting
- Experiment with agent roles, workflows, and tool integrations (e.g. resource, network, knowledge, helper agents)
- Observe agent behavior and interactions in a controlled Azure environment
- Validate agentic approaches for knowledge management, infrastructure automation, and security operations

The included scenario (North River organization) provides a concrete context, but the architecture is modular and can be adapted for other domains or agentic experiments.

---

## Running Your Own Environment

To run your own agentic AI sandbox:

1. **Clone the repository**
   ```sh
   git clone <repo-url>
   cd agentic-ai-observation-experiment
   ```
2. **Install Python dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Provision Azure resources with Terraform**
   ```sh
   cd infra
   terraform init
   terraform plan
   terraform apply
   ```
4. **Configure environment variables**
   Create a `.env` file in the root with your Azure credentials and storage info:

   ```env
   AZURE_STORAGE_ACCOUNT_NAME=northriverknowledgebase
   AZURE_STORAGE_ACCOUNT_KEY=<your_access_key>
   AZURE_STORAGE_ACCOUNT_URL=https://northriverknowledgebase.blob.core.windows.net
   # Add other secrets as needed
   ```

   **Important:** Never commit your `.env` or secrets to Git.

5. **Run agents and tests**
   - Use the provided Python scripts to interact with agents
   - Run unit tests with:
     ```sh
     python -m unittest discover tests
     ```

You can extend the scenario, add new agents, or modify workflows to suit your research or validation needs.

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
   git clone https://github.com/kaikuzai/agentic-ai-observation-experiment
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

--

## Scenario

This project is designed for observation research in an Azure environment. The North River organization has multiple VMs (FinancieleAdministratie, Klantregistratie, Orderverwerking, Rapportage, Authenticatie) and a knowledge base. Agents assist with troubleshooting, knowledge management, and resource management.

---

## Contact & Support

For questions or support: contact me using dylan.okyere@gmail.com

---

## License

MIT License
