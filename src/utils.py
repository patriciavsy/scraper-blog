import unicodedata
from datetime import datetime


routes_dicc = {
    "xepelin": "noticias",
    "pymes": "pymes",
    "corporativos": "corporativos",
    "educacion financiera": "educacion-financiera",
    "emprendedores": "emprendedores",
    "casos de exito": "empresarios-exitosos"
}


def normalize_category(category: str) -> str:
    text = category.lower()
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    if text in routes_dicc:
        return routes_dicc[text]
    else:
        raise ValueError(f"Categoría no válida: {category}. Debe ser una de las siguientes: {', '.join(routes_dicc.keys())}")


def sheets_name_generator(category: str):
    now = datetime.now()
    date_time_str = now.strftime("%Y%m%d_%H%M%S")
    return f"{category}_{date_time_str}"

