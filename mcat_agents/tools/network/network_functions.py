import asyncio
import os
from typing import Annotated, Any, Dict, List, Optional

from agent_framework import ai_function
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import SecurityRule
from dotenv import load_dotenv
from ipaddress import ip_address, ip_network
from pydantic import Field

load_dotenv()

credential = DefaultAzureCredential()
subscription_id = "0818ef22-4784-4365-8a35-1f03e8c5e27d"
default_resource_group = "north-river-resource-group"


def _parse_name_from_id(resource_id: str, type_segment: str) -> Optional[str]:
    """Parse resource name from Azure resource ID."""
    try:
        parts = resource_id.strip('/').split('/')
        for i, p in enumerate(parts):
            if p.lower() == type_segment.lower():
                return parts[i + 1]
    except Exception:
        return None
    return None


def _rule_ports(rule: Any) -> List[int]:
    """Extract port numbers from NSG rule."""
    ports: List[int] = []
    single = getattr(rule, "destination_port_range", None)
    multiple = getattr(rule, "destination_port_ranges", None)
    if single and single != "*":
        try:
            ports.append(int(single))
        except Exception:
            pass
    if multiple:
        for p in multiple:
            try:
                ports.append(int(p))
            except Exception:
                pass
    return ports


def _source_prefixes(rule: Any) -> List[str]:
    """Extract source address prefixes from NSG rule."""
    prefixes: List[str] = []
    single = getattr(rule, "source_address_prefix", None)
    multiple = getattr(rule, "source_address_prefixes", None)
    if single:
        prefixes.append(single)
    if multiple:
        prefixes.extend(multiple)
    return prefixes


def _dest_prefixes(rule: Any) -> List[str]:
    """Extract destination address prefixes from NSG rule."""
    prefixes: List[str] = []
    single = getattr(rule, "destination_address_prefix", None)
    multiple = getattr(rule, "destination_address_prefixes", None)
    if single:
        prefixes.append(single)
    if multiple:
        prefixes.extend(multiple)
    return prefixes


def _prefix_allows_ip(prefix: str, ip: str) -> bool:
    """Check if an IP address is allowed by a CIDR prefix."""
    try:
        if prefix in ("*", "0.0.0.0/0"):
            return True
        if prefix in ("VirtualNetwork", "Internet", "AzureLoadBalancer"):
            return True
        return ip_address(ip) in ip_network(prefix, strict=False)
    except Exception:
        return False


@ai_function(
    name="list_nsgs_in_resource_group",
    description="Lijst alle Network Security Groups (NSGs) in north-river-resource-group.",
    approval_mode="never_require"
)
async def list_nsgs_in_resource_group() -> List[Dict[str, Any]]:
    """Lijst alle NSGs in de resource group."""
    try:
        network = NetworkManagementClient(credential, subscription_id)
        nsgs = network.network_security_groups.list(default_resource_group)
        results: List[Dict[str, Any]] = []
        for nsg in nsgs:
            results.append({
                "name": nsg.name,
                "id": nsg.id,
                "location": nsg.location,
                "tags": nsg.tags,
            })
        return results if results else [{"message": "Geen NSGs gevonden"}]
    except Exception as e:
        return [{"error": f"Fout bij ophalen NSGs: {e}"}]


@ai_function(
    name="get_nsg_rules",
    description="Haal alle inbound en outbound security rules op voor een specifieke NSG in north-river-resource-group.",
    approval_mode="never_require"
)
async def get_nsg_rules(
    nsg_name: Annotated[
        str,
        Field(description="Naam van de Network Security Group")
    ]
) -> Dict[str, Any]:
    """Haal NSG rules op."""
    try:
        network = NetworkManagementClient(credential, subscription_id)
        nsg = network.network_security_groups.get(default_resource_group, nsg_name)
        rules = getattr(nsg, "security_rules", [])
        inbound: List[Dict[str, Any]] = []
        outbound: List[Dict[str, Any]] = []

        for r in rules:
            item = {
                "name": r.name,
                "priority": r.priority,
                "direction": r.direction,
                "access": r.access,
                "protocol": r.protocol,
                "source_prefixes": _source_prefixes(r),
                "destination_prefixes": _dest_prefixes(r),
                "ports": _rule_ports(r),
                "description": r.description,
            }
            if r.direction == "Inbound":
                inbound.append(item)
            else:
                outbound.append(item)

        return {
            "nsg_name": nsg_name,
            "inbound_rules": inbound,
            "outbound_rules": outbound,
            "total_rules": len(inbound) + len(outbound),
        }
    except Exception as e:
        return {"error": f"Fout bij ophalen NSG rules voor {nsg_name}: {e}"}


@ai_function(
    name="list_vm_nsg_associations",
    description="Lijst welke NSG gekoppeld is aan elke NIC van een VM in north-river-resource-group.",
    approval_mode="never_require"
)
async def list_vm_nsg_associations(
    vm_name: Annotated[
        str,
        Field(description="Naam van de Virtual Machine")
    ]
) -> Dict[str, Any]:
    """Lijst NSG associaties voor een VM."""
    try:
        compute = ComputeManagementClient(credential, subscription_id)
        network = NetworkManagementClient(credential, subscription_id)
        vm = compute.virtual_machines.get(default_resource_group, vm_name)
        nic_refs = getattr(getattr(vm, "network_profile", None), "network_interfaces", [])

        associations: List[Dict[str, Any]] = []
        for nic_ref in nic_refs:
            nic_id = nic_ref.id
            nic_name = _parse_name_from_id(nic_id, "networkInterfaces") or nic_id
            nic = network.network_interfaces.get(default_resource_group, nic_name)
            nsg_id = getattr(getattr(nic, "network_security_group", None), "id", None)
            nsg_name = _parse_name_from_id(nsg_id, "networkSecurityGroups") if nsg_id else None
            associations.append({
                "nic_name": nic_name,
                "nsg_name": nsg_name or "Geen NSG gekoppeld"
            })

        return {
            "vm_name": vm_name,
            "nic_nsg_associations": associations,
        }
    except Exception as e:
        return {"error": f"Fout bij ophalen VM NSG associaties: {e}"}


@ai_function(
    name="check_nsg_port_allow",
    description="Controleer of een NSG inbound verkeer toestaat op een specifieke poort vanaf een bron IP-adres.",
    approval_mode="never_require"
)
async def check_nsg_port_allow(
    nsg_name: Annotated[
        str,
        Field(description="Naam van de Network Security Group")
    ],
    port: Annotated[
        int,
        Field(description="Poort nummer om te controleren (bijv. 22 voor SSH)")
    ],
    source_ip: Annotated[
        str,
        Field(description="Bron IP-adres om te testen (bijv. 203.0.113.10)")
    ]
) -> Dict[str, Any]:
    """Controleer of een poort toegankelijk is vanaf een bron IP."""
    try:
        network = NetworkManagementClient(credential, subscription_id)
        nsg = network.network_security_groups.get(default_resource_group, nsg_name)
        rules = getattr(nsg, "security_rules", [])

        matching_rules: List[Dict[str, Any]] = []
        allowed = False

        for r in rules:
            if r.direction != "Inbound":
                continue
            if r.access != "Allow":
                continue

            ports = _rule_ports(r)
            ports_match = (not ports) or (port in ports)
            if not ports_match:
                continue

            src_prefixes = _source_prefixes(r)
            sources_match = (not src_prefixes) or any(_prefix_allows_ip(p, source_ip) for p in src_prefixes)
            if not sources_match:
                continue

            matching_rules.append({
                "name": r.name,
                "priority": r.priority,
                "protocol": r.protocol,
                "source_prefixes": src_prefixes,
                "ports": ports or ["*"],
            })
            allowed = True

        return {
            "nsg_name": nsg_name,
            "port": port,
            "source_ip": source_ip,
            "allowed": allowed,
            "matching_rules": matching_rules,
        }
    except Exception as e:
        return {"error": f"Fout bij controleren NSG poort toegang: {e}"}


@ai_function(
    name="check_vm_port_access",
    description="Controleer of een VM inbound verkeer toestaat op een poort vanaf een bron IP, door alle NICs en hun NSGs te controleren.",
    approval_mode="never_require"
)
async def check_vm_port_access(
    vm_name: Annotated[
        str,
        Field(description="Naam van de Virtual Machine")
    ],
    port: Annotated[
        int,
        Field(description="Poort nummer om te controleren (bijv. 22 voor SSH)")
    ],
    source_ip: Annotated[
        str,
        Field(description="Bron IP-adres om te testen (bijv. 203.0.113.10)")
    ]
) -> Dict[str, Any]:
    """Controleer of een VM toegankelijk is op een poort vanaf een bron IP."""
    try:
        compute = ComputeManagementClient(credential, subscription_id)
        network = NetworkManagementClient(credential, subscription_id)
        vm = compute.virtual_machines.get(default_resource_group, vm_name)
        nic_refs = getattr(getattr(vm, "network_profile", None), "network_interfaces", [])

        details: List[Dict[str, Any]] = []
        overall_allowed = False

        for nic_ref in nic_refs:
            nic_id = nic_ref.id
            nic_name = _parse_name_from_id(nic_id, "networkInterfaces") or nic_id
            nic = network.network_interfaces.get(default_resource_group, nic_name)
            nsg_id = getattr(getattr(nic, "network_security_group", None), "id", None)
            nsg_name = _parse_name_from_id(nsg_id, "networkSecurityGroups") if nsg_id else None

            if not nsg_name:
                details.append({
                    "nic_name": nic_name,
                    "nsg_name": None,
                    "allowed": False,
                    "reason": "Geen NSG gekoppeld"
                })
                continue

            result = await check_nsg_port_allow(nsg_name, port, source_ip)
            allowed = bool(result.get("allowed"))
            overall_allowed = overall_allowed or allowed
            details.append({
                "nic_name": nic_name,
                "nsg_name": nsg_name,
                "allowed": allowed,
                "matching_rules": result.get("matching_rules", []),
            })

        return {
            "vm_name": vm_name,
            "port": port,
            "source_ip": source_ip,
            "allowed": overall_allowed,
            "nic_details": details,
        }
    except Exception as e:
        return {"error": f"Fout bij controleren VM poort toegang: {e}"}


@ai_function(
    name="add_nsg_rule",
    description="Voeg een nieuwe security rule toe aan een NSG of update een bestaande rule. Gebruik dit om poorten te openen of regels aan te passen.",
    approval_mode="never_require"
)
async def add_nsg_rule(
    nsg_name: Annotated[
        str,
        Field(description="Naam van de Network Security Group")
    ],
    rule_name: Annotated[
        str,
        Field(description="Naam voor de security rule")
    ],
    priority: Annotated[
        int,
        Field(description="Priority van de rule (100-4096, lagere nummers = hogere priority)")
    ],
    direction: Annotated[
        str,
        Field(description="Richting: 'Inbound' of 'Outbound'")
    ],
    access: Annotated[
        str,
        Field(description="Toegang: 'Allow' of 'Deny'")
    ],
    protocol: Annotated[
        str,
        Field(description="Protocol: 'Tcp', 'Udp', 'Icmp', of '*' voor alle")
    ],
    destination_ports: Annotated[
        List[int],
        Field(description="Lijst van destination poorten (bijv. [22, 80]). Leeg = alle poorten")
    ] = [],
    source_prefixes: Annotated[
        Optional[List[str]],
        Field(description="Bron IP CIDR prefixes (bijv. ['203.0.113.0/24']). None = alle bronnen (*)")
    ] = None,
    destination_prefixes: Annotated[
        Optional[List[str]],
        Field(description="Doel IP CIDR prefixes. None = alle bestemmingen (*)")
    ] = None,
    description: Annotated[
        Optional[str],
        Field(description="Optionele beschrijving van de rule")
    ] = None
) -> Dict[str, Any]:
    """Voeg een NSG security rule toe of update deze."""
    try:
        network = NetworkManagementClient(credential, subscription_id)

        # Ports handling
        dest_port_range = "*"
        dest_port_ranges = None
        if destination_ports:
            if len(destination_ports) == 1:
                dest_port_range = str(destination_ports[0])
            else:
                dest_port_range = None
                dest_port_ranges = [str(p) for p in destination_ports]

        # Source prefixes
        src_prefix_single = "*"
        src_prefixes_list = None
        if source_prefixes:
            if len(source_prefixes) == 1:
                src_prefix_single = source_prefixes[0]
            else:
                src_prefix_single = None
                src_prefixes_list = source_prefixes

        # Destination prefixes
        dst_prefix_single = "*"
        dst_prefixes_list = None
        if destination_prefixes:
            if len(destination_prefixes) == 1:
                dst_prefix_single = destination_prefixes[0]
            else:
                dst_prefix_single = None
                dst_prefixes_list = destination_prefixes

        rule = SecurityRule(
            protocol=protocol,
            source_port_range="*",
            destination_port_range=dest_port_range,
            destination_port_ranges=dest_port_ranges,
            source_address_prefix=src_prefix_single,
            source_address_prefixes=src_prefixes_list,
            destination_address_prefix=dst_prefix_single,
            destination_address_prefixes=dst_prefixes_list,
            access=access,
            priority=priority,
            direction=direction,
            description=description,
        )

        poller = network.security_rules.begin_create_or_update(
            default_resource_group,
            nsg_name,
            rule_name,
            rule
        )
        poller.result()

        return {
            "nsg_name": nsg_name,
            "rule_name": rule_name,
            "priority": priority,
            "direction": direction,
            "access": access,
            "protocol": protocol,
            "destination_ports": destination_ports or ["*"],
            "source_prefixes": source_prefixes or ["*"],
            "destination_prefixes": destination_prefixes or ["*"],
            "status": "updated",
        }
    except Exception as e:
        return {"error": f"Fout bij toevoegen/updaten NSG rule: {e}"}


@ai_function(
    name="remove_nsg_rule",
    description="Verwijder een security rule uit een NSG. Gebruik dit ALLEEN na expliciete bevestiging.",
    approval_mode="never_require"
)
async def remove_nsg_rule(
    nsg_name: Annotated[
        str,
        Field(description="Naam van de Network Security Group")
    ],
    rule_name: Annotated[
        str,
        Field(description="Naam van de security rule die verwijderd moet worden")
    ]
) -> Dict[str, Any]:
    """Verwijder een NSG security rule."""
    try:
        network = NetworkManagementClient(credential, subscription_id)
        poller = network.security_rules.begin_delete(
            default_resource_group,
            nsg_name,
            rule_name
        )
        poller.result()

        return {
            "nsg_name": nsg_name,
            "rule_name": rule_name,
            "status": "deleted",
        }
    except Exception as e:
        return {"error": f"Fout bij verwijderen NSG rule: {e}"}


if __name__ == '__main__':
    # Test functie
    asyncio.run(list_nsgs_in_resource_group())
