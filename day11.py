import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "https://api.frankfurter.dev/v2/rates")
BASE_DEFAULT = os.getenv("BASE_CURRENCY", "USD")
QUOTE_DEFAULT = os.getenv("QUOTE_CURRENCY", "EUR")


def read_settings():
    print("Введите код валюты: USD, RUB или EUR")
    base = input(f"Исходная валюта: ").strip().upper() or BASE_DEFAULT
    quote = input(f"Целевая валюта: ").strip().upper() or QUOTE_DEFAULT
    amount_str = input("Сумма: ").strip().replace(" ", "")

    if not base or not quote:
        raise ValueError("Код валюты не может быть пустыми")
    if len(base) != 3 or len(quote) != 3:
        raise ValueError("Код валюты должен состоять из 3 букв")
    try:
        amount = float(amount_str)
    except ValueError:
        raise ValueError("Сумма должна быть числом")
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    return base, quote, amount

def get_rate(base, quote):
    response = requests.get(API_URL, params={"base": base, "quotes": quote}, timeout=5)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise ValueError("неожиданный формат ответа сервера")

    for row in data:
        if row.get("base") == base and row.get("quote") == quote:
            return row["rate"], row["date"]

    raise ValueError(f"курс {base} -> {quote} не найден в ответе сервера")
    
  

def print_result(base, quote, amount, rate, date):
    result = amount * rate
    print(f"Дата курса: {date}")
    print(f"Курс: 1 {base} = {rate:.4f} {quote}")
    print(f"Результат: {amount:.2f} {base} = {result:.2f} {quote}")

def main():
    try:
        base, quote, amount = read_settings()
    except ValueError as e:
        print(f"Ошибка: {e}")
        return

    if base == quote:
        print(f"Валюты совпадают: {amount:.2f} {base} = {amount:.2f} {quote}")
        return
    try:
        rate, date = get_rate(base, quote)
    except requests.ConnectionError:
        print("Ошибка: нет соединения с интернетом.")
        return
    except requests.Timeout:
        print(f"Ошибка: сервер не ответил, превышен таймаут.")
        return
    except requests.HTTPError as e:
        print(f"Ошибка HTTP: {e.response.status_code}")
        return
    except (ValueError, KeyError):
        print("Ошибка: не удалось прочитать ответ сервера.")
        return
    
    print_result(base, quote, amount, rate, date)


if __name__ == "__main__":
    main()