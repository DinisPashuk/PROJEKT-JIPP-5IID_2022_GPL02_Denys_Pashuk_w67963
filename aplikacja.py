import json
import hashlib
import os
from datetime import datetime

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {"users": []}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"users": []}

def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register():
    users = load_users()
    username = input("Wprowadź login: ")
    if any(user["username"] == username for user in users["users"]):
        print("Użytkownik już istnieje!")
        return None
    password = input("Wprowadź hasło: ")
    hashed_password = hash_password(password)
    data_file = f"data_{username}.json"
    users["users"].append({"username": username, "password": hashed_password, "data_file": data_file})
    save_users(users)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump({"balance": 0, "income": [], "expenses": []}, f, indent=4)
    print("Konto zostało pomyślnie utworzone! Teraz zaloguj się na swoje konto.")

def login():
    users = load_users()
    while True:
        username = input("Wprowadź login: ")
        password = input("Wprowadź hasło: ")
        hashed_password = hash_password(password)
        for user in users["users"]:
            if user["username"] == username and user["password"] == hashed_password:
                print("Zalogowano pomyślnie!")
                return user["data_file"]
        print("Nieprawidłowy login lub hasło. Spróbuj ponownie.")

def load_data(file):
    if not os.path.exists(file):
        return {"balance": 0, "income": [], "expenses": []}
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def show_balance(file):
    data = load_data(file)
    print(f"\nTwój aktualny balans: {data['balance']} PLN")

def add_transaction(file, transaction_type):
    data = load_data(file)
    amount_input = input("Wprowadź kwotę (lub 'anuluj' aby wyjść): ")
    if amount_input.lower() == "anuluj":
        return
    try:
        amount = float(amount_input)
    except ValueError:
        print("Błąd! Wprowadź poprawną liczbę.")
        return
    category = input("Kategoria: ")
    date = input("Data (YYYY-MM-DD), lub naciśnij Enter dla dzisiaj: ") or datetime.today().strftime('%Y-%m-%d')
    data[transaction_type].append({"id": len(data[transaction_type]) + 1, "amount": amount, "category": category, "date": date})
    data["balance"] += amount if transaction_type == "income" else -amount
    save_data(file, data)
    print("✅ Operacja dodana pomyślnie!")
    show_balance(file)

def edit_transaction(file, transaction_type):
    data = load_data(file)
    transactions = data[transaction_type]
    if not transactions:
        print("Brak zapisów do edytowania.")
        return
    for t in transactions:
        print(f"{t['id']}. {t['category']} - {t['amount']} ({t['date']})")
    trans_id = input("Wprowadź ID zapisu do edytowania (lub 'anuluj' aby wyjść): ")
    if trans_id.lower() == "anuluj":
        return
    try:
        trans_id = int(trans_id)
    except ValueError:
        print("Niepoprawne wejście! Wprowadź liczbę lub 'anuluj'.")
        return
    for t in transactions:
        if t['id'] == trans_id:
            data["balance"] -= t['amount'] if transaction_type == "income" else -t['amount']
            t['amount'] = float(input("Nowa kwota: "))
            t['category'] = input("Nowa kategoria: ")
            t['date'] = input("Nowa data (YYYY-MM-DD): ") or t['date']
            data["balance"] += t['amount'] if transaction_type == "income" else -t['amount']
            save_data(file, data)
            print("✅ Zapis zaktualizowany!")
            return
    print("Nie znaleziono zapisu!")

def delete_transaction(file, transaction_type):
    data = load_data(file)
    transactions = data[transaction_type]
    if not transactions:
        print("Brak zapisów do usunięcia.")
        return
    for t in transactions:
        print(f"{t['id']}. {t['category']} - {t['amount']} ({t['date']})")
    trans_id = input("Wprowadź ID zapisu do usunięcia (lub 'anuluj' aby wyjść): ")
    if trans_id.lower() == "anuluj":
        return
    try:
        trans_id = int(trans_id)
    except ValueError:
        print("Niepoprawne wejście! Wprowadź liczbę lub 'anuluj'.")
        return
    data["balance"] -= next((t['amount'] for t in transactions if t['id'] == trans_id), 0) if transaction_type == "income" else -next((t['amount'] for t in transactions if t['id'] == trans_id), 0)
    data[transaction_type] = [t for t in transactions if t['id'] != trans_id]
    save_data(file, data)
    print("✅ Zapis usunięty!")

def generate_report(file):
    data = load_data(file)
    print("\n=== Raport dochodów i wydatków ===")
    print("Dochody:")
    for inc in data["income"]:
        print(f"- {inc['date']}: {inc['category']} +{inc['amount']} PLN")
    print("\nWydatki:")
    for exp in data["expenses"]:
        print(f"- {exp['date']}: {exp['category']} -{exp['amount']} PLN")
    total_income = sum(inc['amount'] for inc in data["income"])
    total_expense = sum(exp['amount'] for exp in data["expenses"])
    print("\n=== Podsumowanie ===")
    print(f"Łączne dochody: {total_income} PLN")
    print(f"Łączne wydatki: {total_expense} PLN")
    print(f"Końcowy balans: {data['balance']} PLN")

def filter_transactions(file):
    data = load_data(file)
    print("\nFiltracja transakcji")
    print("1. Wyszukiwanie według kategorii")
    print("2. Wyszukiwanie według daty")
    print("3. Wyświetlanie wydatków za określony okres")
    print("4. Wyjście")
    choice = input("Wybierz opcję: ")

    if choice == "1":
        category = input("Wprowadź kategorię: ")
        filtered = [t for t in data["income"] + data["expenses"] if t["category"].lower() == category.lower()]
    elif choice == "2":
        date = input("Wprowadź datę (YYYY-MM-DD): ")
        filtered = [t for t in data["income"] + data["expenses"] if t["date"] == date]
    elif choice == "3":
        start_date = input("Wprowadź datę początkową (YYYY-MM-DD): ")
        end_date = input("Wprowadź datę końcową (YYYY-MM-DD): ")
        filtered = [t for t in data["income"] + data["expenses"] if start_date <= t["date"] <= end_date]
    elif choice == "4":
        return
    else:
        print("Niepoprawny wybór, spróbuj ponownie.")
        return

    if not filtered:
        print("Nic nie znaleziono.")
    else:
        for t in filtered:
            sign = "-" if t in data["expenses"] else "+"
            print(f"{t['date']} | {t['category']} | {sign}{t['amount']} PLN")


def budget_menu(file):
    data = load_data(file)
    while True:
        print(" === Menu budżetu === ")
        print("1. Ustaw budżet")
        print("2. Edytuj budżet")
        print("3. Usuń budżet")
        print("4. Wyjdź")
        choice = input("Wybierz opcję: ")

        if choice == "1":
            try:
                budget = float(input("Ustaw miesięczny budżet (lub '0' aby anulować): "))
                if budget == 0:
                    print("Budżet nie został ustawiony.")
                    continue
                data["budget"] = budget
                save_data(file, data)
                print(f"✅ Budżet ustawiony: {budget} PLN")
            except ValueError:
                print("Błąd! Wprowadź poprawną liczbę.")

        elif choice == "2":
            if "budget" not in data:
                print("❌ Budżet jeszcze nie został ustawiony!")
                continue
            try:
                budget = float(input("Wprowadź nowy rozmiar budżetu: "))
                data["budget"] = budget
                save_data(file, data)
                print(f"✅ Budżet zaktualizowany: {budget} PLN")
            except ValueError:
                print("Błąd! Wprowadź poprawną liczbę.")

        elif choice == "3":
            if "budget" not in data:
                print("❌ Budżet jeszcze nie został ustawiony!")
                continue
            del data["budget"]
            save_data(file, data)
            print("✅ Budżet usunięty!")

        elif choice == "4":
            return
        else:
            print("Niepoprawny wybór, spróbuj ponownie.")

def check_budget_warning(file):
    data = load_data(file)
    budget = data.get("budget", None)
    if budget is None:
        return
    total_expense = sum(exp["amount"] for exp in data["expenses"])
    if total_expense >= budget * 0.9:
        print(f"⚠️ Uwaga! Wydano już {total_expense}/{budget} PLN z budżetu! Przekroczenie jest bliskie!")

def clear_all_transactions(file):
    data = load_data(file)
    data["income"] = []
    data["expenses"] = []
    data["balance"] = 0
    data["budget"] = None
    save_data(file, data)
    print("✅ Wszystkie transakcje i budżet zostały wyczyszczone!")


def main_menu(file):
    while True:
        print("\n=== Główne menu ===")
        print("1. Pokaż balans")
        print("2. Dodaj dochód")
        print("3. Dodaj wydatek")
        print("4. Edytuj dochód")
        print("5. Edytuj wydatek")
        print("6. Usuń dochód")
        print("7. Usuń wydatek")
        print("8. Pokaż raport")
        print("9. Filtruj i wyszukaj transakcje")
        print("10. Budżet")
        print("11. Wyczyść wszystkie transakcje i budżet")
        print("12. Wyjdź do głównego menu")
        check_budget_warning(file)
        choice = input("Wybierz opcję: ")
        if choice == "1":
            show_balance(file)
        elif choice == "2":
            add_transaction(file, "income")
        elif choice == "3":
            add_transaction(file, "expenses")
        elif choice == "4":
            edit_transaction(file, "income")
        elif choice == "5":
            edit_transaction(file, "expenses")
        elif choice == "6":
            delete_transaction(file, "income")
        elif choice == "7":
            delete_transaction(file, "expenses")
        elif choice == "8":
            generate_report(file)
        elif choice == "9":
            filter_transactions(file)
        elif choice == "10":
            budget_menu(file)
        elif choice == "11":
            clear_all_transactions(file)
        elif choice == "12":
            print("Wychodzenie do głównego menu...")
            return
        else:
            print("Niepoprawny wybór, spróbuj ponownie.")

def main():
    while True:
        print("\n=== Witaj w programie do śledzenia wydatków ===")
        print("1. Rejestracja")
        print("2. Logowanie")
        print("3. Wyjście")
        choice = input("Wybierz opcję: ")
        if choice == "1":
            register()
        elif choice == "2":
            user_data_file = login()
            if user_data_file:
                main_menu(user_data_file)
        elif choice == "3":
            print("Do zobaczenia!")
            break
        else:
            print("Niepoprawny wybór, spróbuj ponownie.")

if __name__ == "__main__":
    main()
