import asyncio
import base64
import os
from typing import Annotated, Any, Dict, List

from agent_framework import ai_function
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv()

# AI Search configuratie
endpoint = os.getenv("AI_SEARCH_PROJECT_CONNECTION_ID")
index_name = os.getenv("AI_SEARCH_INDEX_NAME")
api_key = os.getenv("AI_SEARCH_API_KEY")


@ai_function(
    name="search_knowledge_base",
    description="Zoek naar documenten in de knowledge base op basis van een zoekterm. Gebruik dit voor het vinden van beleidsdocumenten, IP-adressen, configuratie-informatie, etc.",
    approval_mode="never_require"
)
async def search_knowledge_base(
    keyword: Annotated[
        str,
        Field(description="De zoekterm om documenten te vinden in de knowledge base. Kan een enkel woord zijn of een specifieke term zoals 'IP-adressen', 'beleid', 'configuratie'")
    ]
) -> List[Dict[str, Any]]:
    """Zoek naar documenten in de AI Search knowledge base."""
    try:
        search_client = SearchClient(
            endpoint,
            index_name,
            credential=AzureKeyCredential(api_key)
        )

        results = search_client.search(search_text=keyword, top=10)

        found_documents = []
        for result in results:
            document_info = {
                "title": result.get("title", "Geen titel"),
                "content": result.get("content", ""),
                "score": result.get("@search.score", 0),
            }

            # Decode file URL indien beschikbaar
            if "id" in result:
                try:
                    padding = "=" * (-len(result['id']) % 4)
                    file_url = base64.b64decode(result['id'] + padding).decode("utf-8")
                    document_info['file_url'] = file_url
                except Exception:
                    document_info['file_url'] = "Niet beschikbaar"

            found_documents.append(document_info)

        return found_documents if found_documents else [{"message": "Geen documenten gevonden voor deze zoekterm"}]

    except Exception as e:
        return [{"error": f"Fout bij zoeken in knowledge base: {e}"}]


@ai_function(
    name="search_knowledge_base_detailed",
    description="Voer een gedetailleerde zoekactie uit in de knowledge base met filters en sortering. Gebruik dit wanneer je specifieke informatie nodig hebt met meer controle over de resultaten.",
    approval_mode="never_require"
)
async def search_knowledge_base_detailed(
    keyword: Annotated[
        str,
        Field(description="De zoekterm voor gedetailleerde zoekactie")
    ],
    top: Annotated[
        int,
        Field(description="Aantal resultaten om terug te geven (standaard 5)", default=5)
    ] = 5
) -> List[Dict[str, Any]]:
    """Voer een gedetailleerde zoekactie uit in de knowledge base."""
    try:
        search_client = SearchClient(
            endpoint,
            index_name,
            credential=AzureKeyCredential(api_key)
        )

        results = search_client.search(
            search_text=keyword,
            top=top,
            include_total_count=True
        )

        found_documents = []
        for result in results:
            document_info = {
                "title": result.get("title", "Geen titel"),
                "content": result.get("content", ""),
                "score": result.get("@search.score", 0),
                "highlights": result.get("@search.highlights", {}),
            }

            # Decode file URL indien beschikbaar
            if "id" in result:
                try:
                    padding = "=" * (-len(result['id']) % 4)
                    file_url = base64.b64decode(result['id'] + padding).decode("utf-8")
                    document_info['file_url'] = file_url
                except Exception:
                    document_info['file_url'] = "Niet beschikbaar"

            found_documents.append(document_info)

        if not found_documents:
            return [{"message": f"Geen documenten gevonden voor '{keyword}'"}]

        return found_documents

    except Exception as e:
        return [{"error": f"Fout bij gedetailleerd zoeken: {e}"}]


@ai_function(
    name="get_document_by_title",
    description="Haal een specifiek document op uit de knowledge base op basis van de exacte titel.",
    approval_mode="never_require"
)
async def get_document_by_title(
    title: Annotated[
        str,
        Field(description="De exacte titel van het document dat je wilt ophalen")
    ]
) -> Dict[str, Any]:
    """Haal een specifiek document op op basis van titel."""
    try:
        search_client = SearchClient(
            endpoint,
            index_name,
            credential=AzureKeyCredential(api_key)
        )

        # Zoek naar exacte match op titel
        results = search_client.search(
            search_text=f'"{title}"',
            search_fields=["title"],
            top=1
        )

        for result in results:
            document_info = {
                "title": result.get("title", "Geen titel"),
                "content": result.get("content", ""),
                "score": result.get("@search.score", 0),
            }

            # Decode file URL indien beschikbaar
            if "id" in result:
                try:
                    padding = "=" * (-len(result['id']) % 4)
                    file_url = base64.b64decode(result['id'] + padding).decode("utf-8")
                    document_info['file_url'] = file_url
                except Exception:
                    document_info['file_url'] = "Niet beschikbaar"

            return document_info

        return {"message": f"Geen document gevonden met titel '{title}'"}

    except Exception as e:
        return {"error": f"Fout bij ophalen document: {e}"}


if __name__ == '__main__':
    # Test functie
    asyncio.run(search_knowledge_base(6))
