from bs4 import BeautifulSoup as _bs4
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager


import time

from urllib.parse import quote
import httpx

from src.utils import normalize_category

from dotenv import load_dotenv
import os



load_dotenv()


options = Options()
options.add_argument("--headless")  # no abre ventana
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)




async def get_posts_count(category: str):

    url = f"https://4n68r2aa.apicdn.sanity.io/v2023-08-21/data/query/production?query=count(*%5B_type%20%3D%3D%20%22blogArticle%22%20%26%26%20blogCategory-%3Eslug.current%20%3D%3D%20%22{category}%22%5D)"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    total = data.get("result", 0)
    return {"total": total}



async def get_posts(category: str):
    
    posts = []

    total = await get_posts_count(category)
    print("Total de posts buscando:", total["total"])
    step = 10

    for start in range(0, total["total"], step):
        end = start + step
        
        url = f"https://4n68r2aa.apicdn.sanity.io/v2023-08-21/data/query/production?query=*%0A%09++%09%5B%0A%09%09%09%09%28_type+%3D%3D+%22blogArticle%22%29%0A++++++++%0A++++++++%26%26+%28%0A%09%09%09%09%09blogCategory-%3Eslug.current+%3D%3D+%22{category}%22%0A%09%09%09%09%29%0A%09%09++%5D+%0A%09%09%09%7C+order%28date+desc%2C+_createdAt+desc%29%0A%09%09%09%7B%0A++++++_type%2C%0A++++++_id%2C%0A++++++slug%2C%0A++++++title%2C%0A%09%09%09excerpt%2C%0A++++++featuredImage%2C%0A++++++_createdAt%2C%0A++++++_updatedAt%2C%0A++++++date%2C%0A++++++author-%3E%2C%0A++++++blogCategory-%3E%2C%0A++++++resourceCategory-%3E%2C%0A++++%7D%5B{start}...{end}%5D&returnQuery=false&perspective=published"

        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json()

        for post in data.get("result", []):       
            link_post = f"{os.environ.get("URL_XEPELIN")}/{category}/{post.get('slug', {}).get('current')}"

            async with httpx.AsyncClient() as client:
                response = await client.get(link_post, headers=headers)

                # se que llega un HTML
                soup_data = _bs4(response.text, "html.parser")
                post_wrapper = soup_data.find("div", attrs={"class": "ArticleSingle_wrapper__I9R7j"})
                lecture_time_div = post_wrapper.select_one("div:nth-of-type(1) > div:nth-of-type(2) > div > div")
                lecture_time = lecture_time_div.text if lecture_time_div else "No Lecture Time"

            post_data = [
                post.get("title"),
                post.get("blogCategory", {}).get("title"),
                post.get("author", {}).get("name"),
                post.get("date"),
                lecture_time    
            ]
            posts.append(post_data)

    print("Se revisaron todos los posts!")

    return posts


async def get_info_to_gsheet(category: str):

    posts = await get_posts(category)    
    return posts
