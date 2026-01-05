# Observatie Onderzoek - Azure Infrastructure

Dit project bevat de Terraform configuratie voor het opzetten van een Azure sandbox omgeving voor het observatie-onderzoek naar de interactie tussen MCAT-teamleden en een agentic AI-prototype.

## 📋 Overzicht

De infrastructuur bestaat uit:

### Virtuele Machines

| VM Naam                    | Functie                               | NSG                  |
| -------------------------- | ------------------------------------- | -------------------- |
| VM-FinancieleAdministratie | Facturatie, betalingen, boekhouding   | NSG-Financieel       |
| VM-Klantregistratie        | Klantdata, accounts, onboarding       | NSG-Klantregistratie |
| VM-Orderverwerking         | Verwerken en afhandelen van orders    | NSG-Orderverwerking  |
| VM-Rapportage              | Managementinformatie en dashboards    | NSG-Rapportage       |
| VM-Authenticatie           | Inloggen, autorisatie, toegangsbeheer | NSG-Authenticatie    |

### Network Security Groups

Elke VM heeft een eigen NSG met regels voor beheertoegang (SSH/RDP) vanaf toegestane IP-adressen.

> ⚠️ **Let op**: `NSG-Authenticatie` heeft **geen** SSH/RDP regels geconfigureerd. Dit is het probleem dat deelnemers moeten oplossen.

### Storage

- **northriverstorageaccount** - Storage account voor Nord River
- **north-river-knowledge-base** - Container met interne kennisdocumenten
- **Beleid/IP-adressen.txt** - Beleidsdocument met toegestane IP-adressen

## 🚀 Deployment

### Vereisten

- [Terraform](https://www.terraform.io/downloads) >= 1.0.0
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- Azure subscription met voldoende rechten

### Stappen

1. **Login bij Azure**

   ```bash
   az login
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   ```

2. **Configureer variabelen**

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Bewerk terraform.tfvars met je waarden
   ```

3. **Genereer SSH key** (indien nodig)

   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/observatie_key -N ""
   ```

4. **Initialiseer Terraform**

   ```bash
   terraform init
   ```

5. **Plan de deployment**

   ```bash
   terraform plan -out=tfplan
   ```

6. **Apply de configuratie**
   ```bash
   terraform apply tfplan
   ```

## 🔧 Scenario Probleem

Het scenario simuleert een situatie waarbij beheertoegang tot `VM-Authenticatie` niet werkt. De oorzaak is dat `NSG-Authenticatie` geen inbound regels heeft voor SSH (poort 22) of RDP (poort 3389).

### Oplossing

De deelnemer moet met behulp van het agentic AI-prototype:

1. Het probleem diagnosticeren
2. De ontbrekende NSG regels identificeren
3. De juiste regels toevoegen aan `NSG-Authenticatie`

## 📁 Bestanden

```
infra/
├── main.tf                    # Hoofd configuratie
├── variables.tf               # Variabele definities
├── outputs.tf                 # Output waarden
├── terraform.tfvars.example   # Voorbeeld variabelen
├── .gitignore                 # Git ignore regels
└── README.md                  # Deze documentatie
```

## 🧹 Opruimen

Om alle resources te verwijderen:

```bash
terraform destroy
```

## 📞 Contact

Multi Client Azure Team (MCAT)  
E-mail: mcat@nordriver.nl
