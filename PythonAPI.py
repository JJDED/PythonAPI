from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import pandas as pd

app = FastAPI()

filepath = 'ww2_dataset.csv'

# Load dataset into a Pandas DataFrame
df = pd.read_csv(filepath)

# Helper function to reload data for persistence
def load_data():
    global df
    df = pd.read_csv(filepath)


df = df.replace({np.nan:None})

# Helper function to save data for persistence
def save_data():
    df.to_csv(filepath, index=False)

data = df.to_dict(orient="records")

# Model to define input data
class DataItem(BaseModel):
    # Define the fields you want to allow in POST request
    # Example: name: str, age: int, city: str, etc.
    pass

### 1. Vis data - Returnér datasættet i JSON-format
@app.get("/data")
def get_data():
    return data

### 2. Sortering - Sortér data efter flere kolonner
@app.get("/data/sort")
def sort_data(column: List[str] = Query(...), ascending: bool = True):
    try:
        sorted_df = df.sort_values(by=column, ascending=ascending)
        return sorted_df.to_dict(orient="records")
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid column name(s) for sorting")

### 3. Filtrering - Filtrér datasættet på flere felter
@app.get("/data/filter")
def filter_data(**filters: str):
    filtered_df = df.copy()
    for column, value in filters.items():
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' does not exist in data")
        filtered_df = filtered_df[filtered_df[column] == value]
    return filtered_df.to_dict(orient="records")

### 4. Tilføj data - Tilføj én eller flere poster ad gangen
@app.post("/data/add")
def add_data(items: List[DataItem]):
    global df
    new_df = pd.DataFrame([item.dict() for item in items])
    df = pd.concat([df, new_df], ignore_index=True)
    save_data()  # Gemmer til CSV
    return {"message": "Data added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
