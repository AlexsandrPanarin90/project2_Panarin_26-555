import os

from prettytable import PrettyTable

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data

_cache_result, clear_select_cache = create_cacher()

@handle_db_errors
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


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, tb_name):

    if tb_name in metadata:
        del metadata[tb_name]
        
        # Внес корретировки так как создавался мусор - 
        # приходилось каждый раз чистить создаваемые таблицы
        # Это мешает работать
        filepath = f"data/{tb_name}.json"
        if os.path.exists(filepath):
            os.remove(filepath)
            
        print(f"Успешно! Таблица с именем '{tb_name}' удалена")
        clear_select_cache()
    else:        
        print(
            f"Ошибка: таблица с именем '{tb_name}' не существует. "
            "Удалите другую таблицу"
        )
    return metadata 


@log_time
@handle_db_errors
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
            new_record[col_name] = int(val)
                
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
    clear_select_cache()
    return table_data

@log_time
@handle_db_errors
def select(tb_name, where_clause=None):
        
    # ключ кэша (имя таблицы + условие)
    where_key = tuple(sorted(where_clause.items())) if where_clause else None
    cache_key = (tb_name, where_key)

    # загружаем и фильтруем данные
    def _fetch():
        table_data = load_table_data(tb_name)
        
        if not table_data:
            return None

        # проверяем если if where_clause = true тогда фильтруем по where_clause
        if where_clause:
            filtered_data = []
            for row in table_data:
                # Проверяем, совпадают ли ВСЕ ключи и 
                # значения из where_clause с этой строкой
                match = True
                for key, value in where_clause.items():
                    # Приводим к строке для надежного сравнения (вдруг там числа)
                    if str(row.get(key)) != str(value):
                        match = False
                        break
                if match:
                    filtered_data.append(row)
            
            return filtered_data
        
        return table_data

    # Вызываем кэшер. Если данные уже есть в кэше - он их вернет, 
    # если нет - вызовет _fetch() и сохранит результат.
    table_data = _cache_result(cache_key, _fetch)

    if not table_data:
        print("Записей по заданному условию не найдено.")
        return

    # выводим таблицу  
    table = PrettyTable()
    table.field_names = table_data[0].keys()
    for row in table_data:
        table.add_row(row.values())
    print(table)


# обновляет записи, подходящие под where_clause.
# внес корректировки, делал под  пример из задания
#правильно не привязываться к примеру а делать универсально
@handle_db_errors
def update(table_data, set_clause, where_clause):
    if not table_data:
        print("Таблица пуста.")
        return table_data

    updated_count = 0
    for row in table_data:
        # проверяем подходит ли строка под условие where
        match = True
        for key, value in where_clause.items():
            if str(row.get(key)) != str(value):
                match = False
                break
                
        # если да, обновляем поля из set_clause
        if match:
            for key, value in set_clause.items():
                # здесь внес корретировки, что если значение 
                # состоит из цифр (или начинается с минуса), тодга 
                # это число, и его надо сохранить как int
                if value.lstrip("-").isdigit():
                    row[key] = int(value)
                else:
                    row[key] = value
            updated_count += 1

    if updated_count > 0:
        print(f"Успешно обновлено записей: {updated_count}.")
        clear_select_cache() 
    else:
        print("Записей по заданному условию не найдено.")
        
    return table_data


#Удаляет записи подходящие под where_clause
@handle_db_errors
@confirm_action("удаление записи")
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
            print(
                f'Запись с ID={deleted_ids[0]} '
                f'успешно удалена из таблицы "{tb_name}".'
            )
        else:
            print(f"Успешно удалено записей: {len(deleted_ids)}.")
        clear_select_cache()    
    else:
        print("Записей по заданному условию не найдено.")
        
    return data_n

#Выводит информацию о таблице
@handle_db_errors
def info(metadata, table_data, tb_name):

    if tb_name not in metadata:
        print(f'Ошибка: Таблица "{tb_name}" не существует.')
        return

    columns = metadata[tb_name]

    print(f"Таблица: {tb_name}")
    print(f"Столбцы: {', '.join(columns)}")
    print(f"Количество записей: {len(table_data)}")


