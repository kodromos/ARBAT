# utils/http_helpers.py
import aiohttp
from typing import Any, Dict, Optional

async def fetch_json(url: str, params: Optional[Dict[str, Any]] = None, session: Optional[aiohttp.ClientSession] = None) -> Optional[Dict]:
    """Fetches JSON data from a given URL with optional parameters."""
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None
    except Exception as e:
        print(f"Error during HTTP request to {url}: {e}")
        return None

