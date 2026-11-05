def create_table(metadata, tb_name, columns):
    
    if tb_name in metadata: # проверяем есть ли уже создаваемая таблица
        print(
            f"Ошибка: таблица с именем '{tb_name}' уже существует. "
            "Попробуйте другое имя"
        )
        return metadata

    
    type_col_pars = []
    for col in columns:  
        if ":" not in col: # проверяем как переданы колонки - должно быть <столбец1:тип>
            print(
                "Нарушен формат передачи! Формат колонок должен соответствовать "
                "шаблону: <столбец1:тип>. Повторите снова."
            )
            return metadata  

        
        name, col_type = col.split(":") 
        # проверяем типы
        if col_type != "int" and col_type != "str" and col_type != "bool":  
            print(f'Ошибка: недопустимый тип данных "{col_type}".')
            return metadata

        type_col_pars.append(f"{name}:{col_type}")


    type_col_pars.insert(0, "ID:int") 
    metadata[tb_name] = type_col_pars

    print(f'Таблица "{tb_name}" создана со столбцами: {", ".join(type_col_pars)}')
    
    return metadata


def drop_table(metadata, tb_name):

    if tb_name in metadata: # проверяем есть ли уже создаваемая таблица
        del metadata[tb_name]
        print(f"Успешно! Таблица с именем '{tb_name}' удалена")
    else:        
        print(
            f"Ошибка: таблица с именем '{tb_name}' не существует. "
            "Удалите другую таблицу"
        )
    return metadata 