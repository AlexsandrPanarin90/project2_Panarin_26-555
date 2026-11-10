import time
from functools import wraps


def handle_db_errors(func):
    @wraps(func)    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
            return args[0] if args else None  # <--- возвращаем то, что было
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            return args[0] if args else None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return args[0] if args else None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return args[0] if args else None
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @wraps(func)        
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.lower() != "y":
                print("Операция отменена.")
                return  
            return func(*args, **kwargs)
        return wrapper
    return decorator


# замер времени выполнения функции
def log_time(func):
    @wraps(func)    
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        
        print(
            f"Функция {func.__name__} выполнилась "
            f"за {end_time - start_time:.3f} секунд."
        )
        return result
    return wrapper


def create_cacher():
  
    cache = {}
    def cache_result(key, value_func):
        if key in cache:
            print(f"[cache] HIT: {key}")
            return cache[key]
        print(f"[cache] MISS: {key}")
        result = value_func()
        cache[key] = result
        return result

    def clear_cache():
        cache.clear()

    return cache_result, clear_cache