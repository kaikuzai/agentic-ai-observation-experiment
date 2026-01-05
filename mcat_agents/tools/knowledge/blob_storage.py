import asyncio
import os
from typing import Annotated, Any, Dict, List

from agent_framework import ai_function
from azure.core.credentials import AzureNamedKeyCredential
from azure.storage.blob import BlobClient, BlobServiceClient, ContentSettings
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "northriverknowledgebase")
account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
storage_account_url = f"https://{account_name}.blob.core.windows.net"
container_name = "north-river-knowledge-base"

# Create credential object
credential = AzureNamedKeyCredential(account_name, account_key) if account_key else None


@ai_function(
    name="read_blob_file",
    description="Lees de inhoud van een bestand uit Blob Storage via de blob URL. Gebruik dit om documenten te lezen uit de knowledge base.",
    approval_mode="never_require"
)
async def read_blob_file(
    blob_url: Annotated[
        str,
        Field(description="De volledige blob URL (https://<account>.blob.core.windows.net/<container>/<path>)")
    ]
) -> Dict[str, Any]:
    """Lees de inhoud van een blob uit Blob Storage."""
    try:
        blob_client = BlobClient.from_blob_url(blob_url=blob_url, credential=credential)

        # Download blob content
        blob_data = blob_client.download_blob(max_concurrency=1)
        content = blob_data.readall().decode("utf-8")

        # Haal properties op
        props = blob_client.get_blob_properties()

        return {
            "blob_url": blob_url,
            "content": content,
            "size": props.size,
            "last_modified": props.last_modified.isoformat() if props.last_modified else None,
            "content_type": props.content_settings.content_type if props.content_settings else None,
        }
    except Exception as e:
        return {"error": f"Fout bij lezen van blob {blob_url}: {e}"}


@ai_function(
    name="replace_blob_file_content",
    description="Vervang de volledige inhoud van een bestand in Blob Storage. Gebruik dit voor het updaten van knowledge base bestanden.",
    approval_mode="never_require"
)
async def replace_blob_file_content(
    blob_url: Annotated[
        str,
        Field(description="De volledige blob URL (https://<account>.blob.core.windows.net/<container>/<path>)")
    ],
    new_content: Annotated[
        str,
        Field(description="De nieuwe tekstinhoud voor het blob bestand")
    ],
    content_type: Annotated[
        str,
        Field(description="MIME type voor het blob bestand", default="text/plain")
    ] = "text/plain"
) -> Dict[str, Any]:
    """Vervang de inhoud van een blob bestand."""
    try:
        blob_client = BlobClient.from_blob_url(blob_url=blob_url, credential=credential)

        # Haal oude grootte op
        try:
            existing_bytes = blob_client.download_blob(max_concurrency=1).readall()
            previous_size = len(existing_bytes)
        except Exception:
            previous_size = None

        # Upload nieuwe content
        settings = ContentSettings(content_type=content_type, content_encoding="utf-8")
        blob_client.upload_blob(
            new_content.encode("utf-8"),
            overwrite=True,
            content_settings=settings
        )

        # Haal nieuwe properties op
        props = blob_client.get_blob_properties()

        return {
            "blob_url": blob_url,
            "status": "updated",
            "etag": props.etag,
            "last_modified": props.last_modified.isoformat() if props.last_modified else None,
            "size": props.size,
            "previous_size": previous_size,
            "content_type": props.content_settings.content_type if props.content_settings else content_type,
        }
    except Exception as e:
        return {"error": f"Fout bij vervangen van blob inhoud {blob_url}: {e}"}


@ai_function(
    name="append_to_blob_file",
    description="Voeg tekst toe aan het einde van een bestaand bestand in Blob Storage. Gebruik dit om informatie toe te voegen aan documenten zonder de bestaande inhoud te verwijderen.",
    approval_mode="never_require"
)
async def append_to_blob_file(
    blob_url: Annotated[
        str,
        Field(description="De volledige blob URL (https://<account>.blob.core.windows.net/<container>/<path>)")
    ],
    text_to_append: Annotated[
        str,
        Field(description="De tekst die toegevoegd moet worden aan het einde van het bestand")
    ]
) -> Dict[str, Any]:
    """Voeg tekst toe aan een bestaand blob bestand."""
    try:
        blob_client = BlobClient.from_blob_url(blob_url=blob_url, credential=credential)

        # Lees huidige content
        existing_blob = blob_client.download_blob(max_concurrency=1)
        existing_content = existing_blob.readall().decode("utf-8")
        previous_size = len(existing_content.encode("utf-8"))

        # Voeg nieuwe content toe
        new_content = existing_content + text_to_append

        # Upload updated content
        props_before = blob_client.get_blob_properties()
        content_type = props_before.content_settings.content_type if props_before.content_settings else "text/plain"
        settings = ContentSettings(content_type=content_type, content_encoding="utf-8")

        blob_client.upload_blob(
            new_content.encode("utf-8"),
            overwrite=True,
            content_settings=settings
        )

        # Haal nieuwe properties op
        props = blob_client.get_blob_properties()

        return {
            "blob_url": blob_url,
            "status": "appended",
            "etag": props.etag,
            "last_modified": props.last_modified.isoformat() if props.last_modified else None,
            "size": props.size,
            "previous_size": previous_size,
            "added_bytes": props.size - previous_size,
        }
    except Exception as e:
        return {"error": f"Fout bij toevoegen aan blob {blob_url}: {e}"}


@ai_function(
    name="create_blob_file",
    description="Maak een nieuw bestand aan in Blob Storage. Gebruik dit om nieuwe documenten toe te voegen aan de knowledge base.",
    approval_mode="never_require"
)
async def create_blob_file(
    blob_path: Annotated[
        str,
        Field(description="Het pad binnen de container (bijv. 'Beleid/nieuw-document.txt')")
    ],
    content: Annotated[
        str,
        Field(description="De tekstinhoud voor het nieuwe bestand")
    ],
    content_type: Annotated[
        str,
        Field(description="MIME type voor het bestand", default="text/plain")
    ] = "text/plain"
) -> Dict[str, Any]:
    """Maak een nieuw blob bestand aan."""
    try:
        blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=credential
        )
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)

        # Check of blob al bestaat
        if blob_client.exists():
            return {
                "error": f"Bestand {blob_path} bestaat al. Gebruik replace_blob_file_content om het te overschrijven."
            }

        # Upload nieuwe blob
        settings = ContentSettings(content_type=content_type, content_encoding="utf-8")
        blob_client.upload_blob(
            content.encode("utf-8"),
            content_settings=settings
        )

        # Haal properties op
        props = blob_client.get_blob_properties()

        return {
            "blob_url": blob_client.url,
            "blob_path": blob_path,
            "status": "created",
            "etag": props.etag,
            "last_modified": props.last_modified.isoformat() if props.last_modified else None,
            "size": props.size,
            "content_type": content_type,
        }
    except Exception as e:
        return {"error": f"Fout bij aanmaken van blob {blob_path}: {e}"}


@ai_function(
    name="list_blobs_in_container",
    description="Lijst alle bestanden op in de north-river-knowledge-base container. Gebruik dit om te zien welke documenten beschikbaar zijn.",
    approval_mode="never_require"
)
async def list_blobs_in_container(
    prefix: Annotated[
        str,
        Field(description="Optioneel: filter op pad prefix (bijv. 'Beleid/' voor alleen beleidsdocumenten)", default="")
    ] = ""
) -> List[Dict[str, Any]]:
    """Lijst alle blobs op in de knowledge base container."""
    try:
        blob_service_client = BlobServiceClient(
            account_url=storage_account_url,
            credential=credential
        )
        container_client = blob_service_client.get_container_client(container_name)

        blobs = container_client.list_blobs(name_starts_with=prefix if prefix else None)

        blob_list = []
        for blob in blobs:
            blob_list.append({
                "name": blob.name,
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                "content_type": blob.content_settings.content_type if blob.content_settings else None,
                "url": f"{storage_account_url}/{container_name}/{blob.name}",
            })

        return blob_list if blob_list else [{"message": "Geen blobs gevonden"}]

    except Exception as e:
        return [{"error": f"Fout bij ophalen blob lijst: {e}"}]


@ai_function(
    name="delete_blob_file",
    description="Verwijder een bestand uit Blob Storage. Gebruik dit ALLEEN na expliciete bevestiging.",
    approval_mode="never_require"
)
async def delete_blob_file(
    blob_url: Annotated[
        str,
        Field(description="De volledige blob URL van het bestand dat verwijderd moet worden")
    ]
) -> Dict[str, Any]:
    """Verwijder een blob bestand."""
    try:
        blob_client = BlobClient.from_blob_url(blob_url=blob_url, credential=credential)

        # Check of blob bestaat
        if not blob_client.exists():
            return {"error": f"Blob {blob_url} bestaat niet"}

        # Verwijder blob
        blob_client.delete_blob()

        return {
            "blob_url": blob_url,
            "status": "deleted",
        }
    except Exception as e:
        return {"error": f"Fout bij verwijderen van blob {blob_url}: {e}"}


if __name__ == "__main__":
    # Test functie
    asyncio.run(list_blobs_in_container())
