# Добавил импортировал shlex для парсинга строк и функции из наших модулей
import shlex

import prompt

from primitive_db.core import (
    create_table, 
    drop_table, 
    insert, 
    select, 
    update, 
    delete,  
    info

)
from primitive_db.utils import (
    load_metadata, 
    save_metadata, 
    load_table_data, 
    save_table_data
)# перенес чтобы не ругался ruff

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

# Добавил переменную с именем файла базы данных
DB_FILE = "db_meta.json"


# (Раньше это было просто кучей print внутри цикла 
# - переделал на функцию добавил команыд)
def print_help():
    print("***")
    print("\n***База данных***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. "
          "- создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nCRUD-операции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    
    print("\nКоманды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


# Переименовал welcome в run, так как по заданию
def run():
    print_help()

  
    while True:
         # переделал инпут на вводу данных, так более праивльно, 
         # а уже первый агрумент буду счиатть командой после дробления стркои
        user_input = prompt.string("Введите команду: ") 
        args = shlex.split(user_input)

        # Проверка если пользователь ввел Enter 
        if not args:
            continue

        # Первое слово это всегда команда
        command = args[0]

        # Загружаем актуальные данные из JSON-файла перед каждой командой
        metadata = load_metadata(DB_FILE)

        if command == "exit":
            print("Выход из программы...")
            break

        elif command == "help":
            print_help()

        # Добавил обработка команды создания таблицы
        elif command == "create_table":
            # Провекра, что ввели хотя бы имя таблицы и одну колонку
            if len(args) < 3:
                print("Некорректное значение: не хватает аргументов. Попробуйте снова.")
                continue
            table_name = args[1]      # Второе слово имя таблицы
            columns = args[2:]        # Всё остальное список колонок
            
            # создаем таблицу
            metadata = create_table(metadata, table_name, columns)
            save_metadata(DB_FILE, metadata)

        # Добавил обработку команды удаления таблицы
        elif command == "drop_table":
            if len(args) < 2:
                print("Некорректное значение: нет имени таблицы. Попробуйте снова.")
                continue
            table_name = args[1]
            
            # Удаляем таблицу
            metadata = drop_table(metadata, table_name)
            save_metadata(DB_FILE, metadata)

        elif command == "insert":
                    # Проверяем, что команда состоит хотя бы из 5 частей
                    if len(args) < 5 or args[1] != "into" or args[3] != "values":
                        print("Некорректное значение: неверный синтаксис команды insert.")
                        continue

                    table_name = args[2]
                    
                    # склеиваем всё что идет после values
                    values_raw = " ".join(args[4:])
                    values_raw = values_raw.strip("()")
                    
                    # разбиваем по разделителю "," чтобы получить список значений
                    values = [v.strip() for v in values_raw.split(",")]

                    # загружаем данные таблицы
                    table_data = load_table_data(table_name)
                    table_data = insert(metadata, table_name, table_data, values)
                    save_table_data(table_name, table_data)            

        elif command == "select":
            if len(args)<3 or args[1] != "from":
                print("Некорректное значение: неверный синтаксис команды select.")
                continue

            table_name = args[2]
            
            # вызываем пасрер чтобы получить солварь или none
            where_clause = parse_where(args)
            table_data = load_table_data(table_name)

            # вызываем функцию select из core и отдаем в нее where_clause
            select(table_data, where_clause)

        elif command == "update":
            if len(args) < 6 or "set" not in args or "where" not in args:
                print("Некорректное значение: неверный синтаксис команды update.")
                continue
                
            table_name = args[1]
            set_clause = parse_set(args)
            where_clause = parse_where(args)
            
            # заргужаем даные и вызываем функцию update
            table_data = load_table_data(table_name)
            table_data = update(table_data, set_clause, where_clause)
            save_table_data(table_name, table_data)

        elif command == "delete":
            # Проверяем синтаксис: delete from users where ...
            if len(args) < 5 or args[1] != "from" or "where" not in args:
                print("Некорректное значение: неверный синтаксис команды delete.")
                continue
                
            table_name = args[2]
            
            where_clause = parse_where(args)
            
            # Загружаем данные, удаляем и сохраняем
            table_data = load_table_data(table_name)
            table_data = delete(table_data, table_name, where_clause) 
            save_table_data(table_name, table_data)

        elif command == "info":
            if len(args) < 2:
                print("Некорректное значение: не хватает имени таблицы. Попробуйте снова.")
                continue
                
            table_name = args[1]
            
            table_data = load_table_data(table_name)
            
            info(metadata, table_data, table_name)


        # доабвил обработку команды вывода списка таблиц
        elif command == "list_tables":
            if not metadata:
                print("Таблиц нет.")
            else:
                for table in metadata:
                    print(f"- {table}")

        else:
            print(f"Функции {command} нет. Попробуйте снова.")