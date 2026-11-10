#Превращает список аргументов после 'where' в словарь.
def parse_where(args):
    if "where" not in args:
        return None
        
    where_index = args.index("where")
    
    condition_str = " ".join(args[where_index + 1:])
    
    if "=" not in condition_str:
        return None
    parts = condition_str.split("=")
    
    col_name = parts[0].strip()
    
    col_value = parts[1].strip().strip('"').strip("'")
    
    return {col_name: col_value}

# делаем список аргументов после set в словарь
def parse_set(args):
    
    if "set" not in args:
        return None
        
    set_index = args.index("set")
    where_index = args.index("where") if "where" in args else len(args)
    
    condition_str = " ".join(args[set_index + 1 : where_index])
    
    if "=" not in condition_str:
        return None
        
    parts = condition_str.split("=")
    col_name = parts[0].strip()
    col_value = parts[1].strip().strip('"').strip("'")
    
    return {col_name: col_value}