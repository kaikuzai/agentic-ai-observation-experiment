import asyncio
import os
from typing import Annotated, Any, Dict, List

from agent_framework import ai_function
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

credential = DefaultAzureCredential()
subscription_id = "0818ef22-4784-4365-8a35-1f03e8c5e27d"
default_resource_group = "north-river-resource-group"


@ai_function(
    name="list_resource_groups",
    description="Gebruik deze functie om alle resource groups in de subscription op te lijsten.",
    approval_mode="never_require"
)
async def list_resource_groups(
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID voor de gevraagde resource groups",
            default=subscription_id
        ) 
    ] = subscription_id
) -> List[Dict[str, Any]]:
    """Lijst alle resource groups in een subscription."""
    try:
        resource_group_list = []
        resource_client = ResourceManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        for resource_group in resource_client.resource_groups.list():
            resource_group_list.append({
                "name": resource_group.name,
                "location": resource_group.location,
                "id": resource_group.id,
            })

        return resource_group_list
    except Exception as e:
        return [{"error": f"Fout bij ophalen resource groups in {subscription_id}: {e}"}]


@ai_function(
    name="get_resources_in_resource_group",
    description="Lijst alle resources in de north-river-resource-group. Kan geen gedetailleerde informatie over individuele resources geven.",
    approval_mode="never_require"
)
async def get_resources_in_resource_group(
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID voor de gevraagde resource group",
            default=subscription_id
        )
    ] = subscription_id
) -> List[Dict[str, Any]]:
    """Geef alle resources in een specifieke resource group terug."""
    try:
        resource_group = "north-river-resource-group"
        resource_client = ResourceManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        resources = resource_client.resources.list_by_resource_group(
            resource_group_name=resource_group
        )

        resource_list = []
        for resource in resources:
            resource_list.append({
                "name": resource.name,
                "type": resource.type,
                "kind": resource.kind,
                "id": resource.id,
                "location": resource.location,
            })

        return resource_list
    except Exception as e:
        return [{"error": f"Fout bij ophalen resources in {resource_group}: {e}"}]


@ai_function(
    name="list_vms_in_resource_group",
    description="Lijst alle VMs in de north-river-resource-group met hun basisinformatie.",
    approval_mode="never_require"
)
async def list_vms_in_resource_group(
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID",
            default=subscription_id
        )
    ] = subscription_id
) -> List[Dict[str, Any]]:
    """Lijst alle VMs in een resource group."""
    try:
        resource_group = "north-river-resource-group"
        compute_client = ComputeManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        vms = compute_client.virtual_machines.list(resource_group_name=resource_group)

        vm_list = []
        for vm in vms:
            vm_list.append({
                "name": vm.name,
                "id": vm.id,
                "location": vm.location,
                "vm_size": vm.hardware_profile.vm_size if vm.hardware_profile else None,
                "os_type": vm.storage_profile.os_disk.os_type if vm.storage_profile and vm.storage_profile.os_disk else None,
            })

        return vm_list
    except Exception as e:
        return [{"error": f"Fout bij ophalen VMs in {resource_group}: {e}"}]


@ai_function(
    name="get_vm_status",
    description="Haal de huidige status (running, stopped, deallocated) van een specifieke VM op in north-river-resource-group.",
    approval_mode="never_require"
)
async def get_vm_status(
    vm_name: Annotated[
        str,
        Field(description="De naam van de VM waarvan je de status wilt weten")
    ],
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID",
            default=subscription_id
        )
    ] = subscription_id
) -> Dict[str, Any]:
    """Geef de status van een specifieke VM terug."""
    try:
        resource_group = "north-river-resource-group"
        compute_client = ComputeManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        instance_view = compute_client.virtual_machines.instance_view(
            resource_group_name=resource_group,
            vm_name=vm_name
        )

        statuses = []
        if instance_view.statuses:
            for status in instance_view.statuses:
                statuses.append({
                    "code": status.code,
                    "display_status": status.display_status,
                    "message": status.message,
                })

        return {
            "vm_name": vm_name,
            "statuses": statuses,
        }
    except Exception as e:
        return {"error": f"Fout bij ophalen status van VM {vm_name}: {e}"}


@ai_function(
    name="get_vm_network_info",
    description="Haal netwerkinformatie op van een VM in north-river-resource-group, inclusief NIC, private IP, public IP en gekoppelde NSG.",
    approval_mode="never_require"
)
async def get_vm_network_info(
    vm_name: Annotated[
        str,
        Field(description="De naam van de VM waarvan je netwerkinformatie wilt")
    ],
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID",
            default=subscription_id
        )
    ] = subscription_id
) -> Dict[str, Any]:
    """Geef netwerkinformatie van een VM terug."""
    try:
        resource_group = "north-river-resource-group"
        compute_client = ComputeManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )
        network_client = NetworkManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        # Haal VM op
        vm = compute_client.virtual_machines.get(
            resource_group_name=resource_group,
            vm_name=vm_name
        )

        network_interfaces = []
        if vm.network_profile and vm.network_profile.network_interfaces:
            for nic_reference in vm.network_profile.network_interfaces:
                nic_id = nic_reference.id
                nic_name = nic_id.split('/')[-1]

                # Haal NIC details op
                nic = network_client.network_interfaces.get(
                    resource_group_name=resource_group,
                    network_interface_name=nic_name
                )

                ip_configurations = []
                for ip_config in nic.ip_configurations:
                    config_info = {
                        "name": ip_config.name,
                        "private_ip": ip_config.private_ip_address,
                        "private_ip_allocation": ip_config.private_ip_allocation_method,
                    }

                    # Haal public IP op indien aanwezig
                    if ip_config.public_ip_address:
                        public_ip_id = ip_config.public_ip_address.id
                        public_ip_name = public_ip_id.split('/')[-1]
                        public_ip = network_client.public_ip_addresses.get(
                            resource_group_name=resource_group,
                            public_ip_address_name=public_ip_name
                        )
                        config_info["public_ip"] = public_ip.ip_address

                    ip_configurations.append(config_info)

                nsg_info = None
                if nic.network_security_group:
                    nsg_info = {
                        "id": nic.network_security_group.id,
                        "name": nic.network_security_group.id.split('/')[-1],
                    }

                network_interfaces.append({
                    "nic_name": nic_name,
                    "nic_id": nic_id,
                    "ip_configurations": ip_configurations,
                    "network_security_group": nsg_info,
                })

        return {
            "vm_name": vm_name,
            "network_interfaces": network_interfaces,
        }
    except Exception as e:
        return {"error": f"Fout bij ophalen netwerkinformatie van VM {vm_name}: {e}"}


@ai_function(
    name="get_nsg_info",
    description="Haal informatie op over een Network Security Group (NSG), inclusief alle inbound en outbound security rules.",
    approval_mode="never_require"
)
async def get_nsg_info(
    nsg_name: Annotated[
        str,
        Field(description="De naam van de Network Security Group waarvan je informatie wilt")
    ],
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID",
            default=subscription_id
        )
    ] = subscription_id
) -> Dict[str, Any]:
    """Geef gedetailleerde informatie over een NSG terug."""
    try:
        resource_group = "north-river-resource-group"
        network_client = NetworkManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        nsg = network_client.network_security_groups.get(
            resource_group_name=resource_group,
            network_security_group_name=nsg_name
        )

        security_rules = []
        if nsg.security_rules:
            for rule in nsg.security_rules:
                security_rules.append({
                    "name": rule.name,
                    "priority": rule.priority,
                    "direction": rule.direction,
                    "access": rule.access,
                    "protocol": rule.protocol,
                    "source_port_range": rule.source_port_range,
                    "destination_port_range": rule.destination_port_range,
                    "source_address_prefix": rule.source_address_prefix,
                    "destination_address_prefix": rule.destination_address_prefix,
                    "description": rule.description,
                })

        default_security_rules = []
        if nsg.default_security_rules:
            for rule in nsg.default_security_rules:
                default_security_rules.append({
                    "name": rule.name,
                    "priority": rule.priority,
                    "direction": rule.direction,
                    "access": rule.access,
                    "protocol": rule.protocol,
                    "source_port_range": rule.source_port_range,
                    "destination_port_range": rule.destination_port_range,
                    "source_address_prefix": rule.source_address_prefix,
                    "destination_address_prefix": rule.destination_address_prefix,
                })

        return {
            "nsg_name": nsg.name,
            "id": nsg.id,
            "location": nsg.location,
            "provisioning_state": nsg.provisioning_state,
            "security_rules": security_rules,
            "default_security_rules": default_security_rules,
        }
    except Exception as e:
        return {"error": f"Fout bij ophalen NSG informatie voor {nsg_name}: {e}"}


@ai_function(
    name="list_nsgs",
    description="Lijst alle Network Security Groups (NSGs) in north-river-resource-group op.",
    approval_mode="never_require"
)
async def list_nsgs(
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID",
            default=subscription_id
        )
    ] = subscription_id
) -> List[Dict[str, Any]]:
    """Lijst alle NSGs in een resource group."""
    try:
        resource_group = "north-river-resource-group"
        network_client = NetworkManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        nsgs = network_client.network_security_groups.list(resource_group_name=resource_group)

        nsg_list = []
        for nsg in nsgs:
            nsg_list.append({
                "name": nsg.name,
                "id": nsg.id,
                "location": nsg.location,
                "provisioning_state": nsg.provisioning_state,
            })

        return nsg_list
    except Exception as e:
        return [{"error": f"Fout bij ophalen NSGs in {resource_group}: {e}"}]


@ai_function(
    name="start_vm",
    description="Start een VM in north-river-resource-group die momenteel gestopt of deallocated is.",
    approval_mode="always_require"
)
async def start_vm(
    vm_name: Annotated[
        str,
        Field(description="De naam van de VM die gestart moet worden")
    ],
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID",
            default=subscription_id
        )
    ] = subscription_id
) -> Dict[str, Any]:
    """Start een VM."""
    try:
        resource_group = "north-river-resource-group"
        compute_client = ComputeManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        async_vm_start = compute_client.virtual_machines.begin_start(
            resource_group_name=resource_group,
            vm_name=vm_name
        )
        async_vm_start.wait()

        return {
            "success": True,
            "message": f"VM {vm_name} is succesvol gestart",
        }
    except Exception as e:
        return {"error": f"Fout bij starten van VM {vm_name}: {e}"}


@ai_function(
    name="stop_vm",
    description="Stop een VM (deallocate) in north-river-resource-group om kosten te besparen.",
    approval_mode="always_require"
)
async def stop_vm(
    vm_name: Annotated[
        str,
        Field(description="De naam van de VM die gestopt moet worden")
    ],
    subscription_id: Annotated[
        str,
        Field(
            description="De subscription ID",
            default=subscription_id
        )
    ] = subscription_id
) -> Dict[str, Any]:
    """Stop (deallocate) een VM."""
    try:
        resource_group = "north-river-resource-group"
        compute_client = ComputeManagementClient(
            credential=credential,
            subscription_id=subscription_id
        )

        async_vm_stop = compute_client.virtual_machines.begin_deallocate(
            resource_group_name=resource_group,
            vm_name=vm_name
        )
        async_vm_stop.wait()

        return {
            "success": True,
            "message": f"VM {vm_name} is succesvol gestopt",
        }
    except Exception as e:
        return {"error": f"Fout bij stoppen van VM {vm_name}: {e}"}


if __name__ == '__main__':
    # Test functie
    asyncio.run(list_resource_groups())
