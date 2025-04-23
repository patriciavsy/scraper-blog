from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.scraper import get_info_to_gsheet
from src.gsheetmaker import create_sheet, update_sheet
from src.utils import routes_dicc, normalize_category

import httpx

from dotenv import load_dotenv
import os



load_dotenv()

app = FastAPI()




class Query(BaseModel):
    category: str
    webhook: str
    email: str



@app.get("/")
def read_root():
    return {"mensaje": "Iniciando FastAPI"}


@app.post("/posts-blog")
async def posts_by_category(query: Query):
    try:
        category_1 = query.category
        webhook = query.webhook
        email = query.email

        category = normalize_category(category_1)

        scraped_info = await get_info_to_gsheet(category)
        scraped_info.insert(0, ['Título', 'Categoría', 'Autor', 'Fecha de publicación', 'Tiempo de lectura'])
    
        new_sheet_id = create_sheet(category)
        update_sheet(category, new_sheet_id, scraped_info)
        
        link_sheet = f"https://docs.google.com/spreadsheets/d/{new_sheet_id}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        print(webhook)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=webhook, 
                headers=headers, 
                json={
                    "email": email,
                    "link": link_sheet,
                }
            )
            data = response.json()
            print("Respuesta del webhook:", data)

        return {
            "status": "Web Scraping realizado exitosamente"
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/all-posts-blog")
async def all_posts_by_category():
    try:
        categories = routes_dicc.values()
        all_info = []
        for category in categories:
            print(category);
            scraped_info = await get_info_to_gsheet(category)
            all_info += scraped_info

        all_info.insert(0, ['Título', 'Categoría', 'Autor', 'Fecha de publicación', 'Tiempo de lectura'])
        new_sheet_id = create_sheet("todas-categorias")
        update_sheet(category, new_sheet_id, all_info)
        
        link_sheet = f"https://docs.google.com/spreadsheets/d/{new_sheet_id}"

        return {
            "status": "Web Scraping realizado exitosamente",
            "link": link_sheet
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))