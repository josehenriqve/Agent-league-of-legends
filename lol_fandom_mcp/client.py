import httpx
from typing import Optional, Dict, Any, List

BASE_URL = "https://lol.fandom.com"

class LolFandomClient:
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.client = httpx.AsyncClient(base_url=BASE_URL, headers=headers)

    async def query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic method to perform a GET request to the API.
        """
        # Ensure format is json
        if "format" not in params:
            params["format"] = "json"
        
        try:
            response = await self.client.get("/api.php", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP Error: {e}")
            raise

    async def search_pages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for pages by title.
        API: ?action=query&list=search&srsearch=QUERY&srlimit=LIMIT
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit
        }
        data = await self.query(params)
        return data.get("query", {}).get("search", [])


    async def get_page_content(self, title: str) -> str:
        """
        Get the raw content (wikitext) of a page.
        API: ?action=query&prop=revisions&titles=TITLE&rvprop=content&rvslots=main
        """
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "rvprop": "content",
            "rvslots": "main"
        }
        data = await self.query(params)
        pages = data.get("query", {}).get("pages", {})
        
        # pages is a dict with page_id as keys. We iterate to find the first one.
        for page_id, page_data in pages.items():
            if page_id == "-1": # Page not found
                return f"Page '{title}' not found."
            
            revisions = page_data.get("revisions", [])
            if revisions:
                slot_main = revisions[0].get("slots", {}).get("main", {})
                return slot_main.get("*", "No content found.")
        
        return "Page not found or no content."

    async def cargo_query(self, tables: str, fields: str, where: str, limit: Optional[int] = 50) -> List[Dict[str, Any]]:
        """
        Perform a Cargo query.
        """
        params = {
            "action": "cargoquery",
            "tables": tables,
            "fields": fields,
            "where": where,
            # "limit": limit # User request wanted EXACT matching URL, so we shouldn't send limit if not requested,
            # but usually APIs have defaults. The user's URL didn't show limit.
            # I will omit limit from params if it's None.
        }
        if limit is not None:
             params["limit"] = limit

        # The user provided a very specific URL.
        # We need to make sure httpx encoding matches it.
        # Httpx usually does standard encoding.
        
        data = await self.query(params)
        return data.get("cargoquery", [])


    async def close(self):
        await self.client.aclose()
