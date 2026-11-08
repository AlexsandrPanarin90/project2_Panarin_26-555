import json
import os


def load_metadata(filepath):
    try:
        with open(filepath,"r", encoding="utf-8") as f:
            data = json.load(f)
        return data            
    except FileNotFoundError:
        return {} 


def save_metadata(filepath, data):
    with open(filepath,"w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)          


def load_table_data(table_name):
    try:
        with open(f'data/{table_name}.json',"r", encoding="utf-8") as f:
            data = json.load(f)
        return data            
    except FileNotFoundError:
        return [] 


def save_table_data(table_name, data):
    os.makedirs("data", exist_ok=True)
    with open(f'data/{table_name}.json',"w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)  