import json


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





