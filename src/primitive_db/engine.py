# Добавил импортировал shlex для парсинга строк и функции из наших модулей
import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

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
            
            # Создаем таблицу
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

        # доабвил обработку команды вывода списка таблиц
        elif command == "list_tables":
            if not metadata:
                print("Таблиц нет.")
            else:
                for table in metadata:
                    print(f"- {table}")

        else:
            print(f"Функции {command} нет. Попробуйте снова.")