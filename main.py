from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

app = FastAPI()

app.mount("/images", StaticFiles(directory="./downloaded_images"), name="images")

templates = Jinja2Templates(directory="./templates")

data = pd.read_csv("./bib_numbers.csv")

@app.get("/")
def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "images": []})

@app.post("/search")
def search_bib(request: Request, bib_number: str = Form(...)):
    cleaned_data = data.dropna(subset=["bib_numbers"]).copy()

    def match_bib(cell):
        bibs = [b.strip() for b in cell.split("|")]
        return bib_number in bibs

    filtered = cleaned_data[cleaned_data["bib_numbers"].apply(match_bib)]

    image_paths = [f"/images/{filename}" for filename in filtered['image_name'].tolist()]
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "images": image_paths, "bib_number": bib_number}
    )