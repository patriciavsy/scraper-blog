from scraper import get_info_to_gsheet
import asyncio


if __name__ == "__main__":
    asyncio.run(get_info_to_gsheet("pymes"))
