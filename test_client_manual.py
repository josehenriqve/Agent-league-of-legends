import asyncio
from lol_fandom_mcp.client import LolFandomClient

async def main():
    client = LolFandomClient()
    try:
        print("Searching for 'Ahri'...")
        results = await client.search_pages("Ahri")
        print(f"Results: {results}")

        if results:
            first_title = results[0]['title']
            print(f"\nReading page: {first_title}")
            content = await client.get_page_content(first_title)
            print(f"Content length: {len(content)}")
            print(f"Content preview: {content[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
