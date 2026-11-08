from prettytable import PrettyTable

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


def insert(metadata, tb_name, table_data, values):

    if tb_name not in metadata:
        print(f'Ошибка: Таблица "{tb_name}" не существует.')
        return table_data

    structure = metadata[tb_name]
    val_columns = structure[1:]  # берем всё кроме ID
    
    if len(values) != len(val_columns):
        print(f"Ошибка: Неверное количество значений. Ожидалось {len(val_columns)}.")
        return table_data

    if len(table_data) == 0:
        new_id = 1
    else:
        new_id = max(row["ID"] for row in table_data) + 1

    new_record = {"ID": new_id}   

    # Проходимся по колонкам и значениям
    for col, val in zip(val_columns, values):
        col_name, col_type = col.split(":")
        
        if col_type == "int":
            try:
                new_record[col_name] = int(val)
            except ValueError:
                print(f'Ошибка: Значение "{val}" не является целым числом (int).')
                return table_data
                
        elif col_type == "bool":
            val_clean = str(val).lower().strip('"').strip("'")
            if val_clean in ["true", "1", "yes"]:
                new_record[col_name] = True
            elif val_clean in ["false", "0", "no"]:
                new_record[col_name] = False
            else:
                print(f'Ошибка: Значение "{val}" не является логическим (bool).')
                return table_data
                
        else:  # str
            new_record[col_name] = str(val).strip('"').strip("'")

    table_data.append(new_record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{tb_name}".')
    return table_data


def select(table_data, where_clause=None):
    if len(table_data) ==0:
        print(f'Таблица пустая')
        return

    # проверяем если  if where_clause = true тогда фильтруем по where_clause
    if where_clause:
        filtered_data = []
        for row in table_data:
            # Проверяем, совпадают ли ВСЕ ключи и значения из where_clause с этой строкой
            match = True
            for key, value in where_clause.items():
                # Приводим к строке для надежного сравнения (вдруг там числа)
                if str(row.get(key)) != str(value):
                    match = False
                    break
            if match:
                filtered_data.append(row)
        
        table_data = filtered_data

    if not table_data:
        print("Записей по заданному условию не найдено.")
        return

    # выводим таблицу  
    table = PrettyTable()
    table.field_names = table_data[0].keys()
    for row in table_data:
        table.add_row(row.values())
    print(table)


#обновляет записи, подходящие под where_clause.
def update(table_data, set_clause, where_clause):
    if not table_data:
        print("Таблица пуста.")
        return table_data

    updated_count = 0
    for row in table_data:
        # проверяем подходет ли строка под условие where
        match = True
        for key, value in where_clause.items():
            if str(row.get(key)) != str(value):
                match = False
                break
                
        # если да обновляем поля из set_clause
        if match:
            for key, value in set_clause.items():
                if key == "ID" or key == "age":
                    row[key] = int(value)
                else:
                    row[key] = value
            updated_count += 1

    if updated_count > 0:
        print(f"Успешно обновлено записей: {updated_count}.")
    else:
        print("Записей по заданному условию не найдено.")
        
    return table_data


#Удаляет записи подходящие под where_clause
def delete(table_data, tb_name, where_clause):
    # если таблица пустая тогда нечего удалять 
    if not table_data:
        print("Таблица пуста.")
        return table_data

    data_n = []
    deleted_ids = []  # надо записывать id удаленных записей для сообщения - вывода
    
    for row in table_data:
        # проверяем удовлетворяет ли строка условию удаления
        match = True
        for key, value in where_clause.items():
            # чтобы можно было сравнить числа и строки надо привести к строкам
            if str(row.get(key)) != str(value):
                match = False
                break
                
        # здесь хитрое условие, мы не перебираем 
        # и не удаляем записи из-за смещенйя индекса, а просто формируем новый список. 
        # Принцип в новый список попадают все кто не подходит под удаление      
        if match:
            # Если подходит записвыаем id для вывода и не добавляем в data_n
            deleted_ids.append(row.get("ID", "?")) 
        else:
            # не подходит оставляем запись
            data_n.append(row)

    # Выводим результат
    if deleted_ids:
        if len(deleted_ids) == 1:
            print(f'Запись с ID={deleted_ids[0]} успешно удалена из таблицы "{tb_name}".')
        else:
            print(f"Успешно удалено записей: {len(deleted_ids)}.")
    else:
        print("Записей по заданному условию не найдено.")
        
    return data_n

#Выводит информацию о таблице
def info(metadata, table_data, tb_name):

    if tb_name not in metadata:
        print(f'Ошибка: Таблица "{tb_name}" не существует.')
        return

    columns = metadata[tb_name]

    print(f"Таблица: {tb_name}")
    print(f"Столбцы: {', '.join(columns)}")
    print(f"Количество записей: {len(table_data)}")