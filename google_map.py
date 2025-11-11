import os
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("google_map")
load_dotenv()

GOOGLE_MAP_URL = "https://places.googleapis.com/v1/places:searchText"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


async def make_google_map_request(search_text: str):
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set. Check .env or env vars.")
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount"
    }
    body = {"textQuery": search_text, "pageSize": 5}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GOOGLE_MAP_URL, headers=headers, json=body)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print("HTTP error occurred:", e)
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            print("An error occurred:", e)
            return {"error": str(e)}


@mcp.tool()
async def get_places(search_text: str) -> str:
    """
    Search Google Maps for places using free-text query.
    """
    response = await make_google_map_request(search_text)
    if response.get("error", ""):
        return f"Error: {response['error']}"
    print(response)
    places = response.get("places", [])
    if not places:
        return "No results found."

    results = []
    for p in places:
        name = p.get("displayName", {}).get("text", "N/A")
        address = p.get("formattedAddress", "N/A")
        rating = p.get("rating", "N/A")
        results.append(f"{name} — {address} (⭐ {rating})")

    return "\n".join(results)


def main():
    # Initialize and run the server
    mcp.run(transport='stdio')
    # import asyncio
    # print(asyncio.run(get_places("cafes near San Francisco")))


if __name__ == "__main__":
    main()
