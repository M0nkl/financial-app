import flet as ft
import sqlite3 
from datetime import datetime
import requests

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Финансы"
    today = datetime.today().strftime("%d_%m_%Y")
    #общие кнопки
    homepage = ft.IconButton(ft.Icons.BACKSPACE, on_click=lambda _: page.go("/"))

    #Ввод курсов
    cvd = ft.TextField(label="Введите дату")
    cvuk = ft.TextField(label="Введите usd-kzt")
    cvur = ft.TextField(label="Введите usd-rub")
    cvrk = ft.TextField(label="Введите rub-kzt")
    curtext = ft.Text("RUB")

    #Ввод кошельков
    actype = ft.TextField(label="Введите тип")
    acname = ft.TextField(label="Введите название")
    accurrency = ft.TextField(label="Введите валюту")
    acbalance = ft.TextField(label="Введите баланс")

    #Ввод транзакций
    tranval = ft.TextField(label="Сумма")
    trancard = ft.Text("Т-банк")
    trancat = ft.Text("Прочее")

    def rub_rates():
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        # USD: {"Nominal":1, "Value":82.3456}
        rates = {
            code: val["Value"] / val["Nominal"]
            for code, val in data["Valute"].items()
        }
        rates["RUB"] = 1.0
        return rates
    
    rates = rub_rates()

    usd_kzt = ft.Text("USD-KZT - " + format(rates["USD"] / rates["KZT"], ".2f"))
    usd_rub = ft.Text("USD-RUB - " + format(rates["USD"], ".2f"))
    rub_kzt = ft.Text("RUB-KZT - " + format(1/rates["KZT"], '.2f'))

    def card_rub_info(e): # Скорее всего юзлес
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c = db.cursor()
        c.execute("SELECT (balance, currency) FROM accounts")
        row = c.fetchall()
        card_rub.value = row
        db.close()
        page.update()

    def change_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.DARK
        page.update()

    def currency_in(e): #Упразнено
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c = db.cursor()
        c.execute("INSERT INTO currency (date, usd_kzt, usd_rub, rub_kzt) VALUES (?, ?, ?, ?)", (today, cvuk.value, cvur.value, cvrk.value))
        db.commit()
        db.close()

    def accounts_in(e):
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c = db.cursor()
        c.execute("INSERT INTO accounts (type, name, currency, balance) VALUES (?, ?, ?, ?)", (actype.value, acname.value, accurrency.value, acbalance.value))
        db.commit()
        db.close()

    def currency_change(e):
        cur = e.control.value
        rr = rub_rates()
        if cur == "USD":
            total_rub.value = format(total_balance_in_rub() / rr["USD"], '.2f') 
        if cur == "KZT":
            total_rub.value = format(total_balance_in_rub() / rr["KZT"], '.2f')
        if cur == "RUB":
            total_rub.value = format(total_balance_in_rub(), '.2f')
        page.update()

    curinfo = ft.Dropdown(
        editable=True,
        label="currency",
        value="RUB",
        on_change = currency_change,
        options = [
            ft.DropdownOption(key="RUB"),
            ft.DropdownOption(key="USD"),
            ft.DropdownOption(key="KZT"),
        ],
    )

    def dropdown_card(e):
        trancard.value = e.control.value
        page.update()

    card_list = ft.Dropdown(
        editable = True, 
        options = [
            ft.DropdownOption(key="Наличка"),
            ft.DropdownOption(key="Т-банк"),
            ft.DropdownOption(key="Каспи"),
            ft.DropdownOption(key="СберБанк"),
            ft.DropdownOption(key="BuyBit"),
            ft.DropdownOption(key="OKX"),
            ft.DropdownOption(key="Binance"),
        ], label = "wallet", 
        value = "Т-банк",
        on_change = dropdown_card,
        )
    
    def option_category(e):
        trancat.value = e.control.value
        page.update()

    category_list = ft.Dropdown(
        editable=True, 
        options = [
        ft.DropdownOption(key="Продукты"),
        ft.DropdownOption(key="Интернет покупки"),
        ft.DropdownOption(key="Транспорт"),
        ft.DropdownOption(key="Перевод"),
        ft.DropdownOption(key="Прочее"),
    ], label = "category",
    value = "Прочее",
    on_change = option_category,
    )

    def transaction_in(e):
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c = db.cursor()
        c.execute("INSERT INTO transactions (date, account, category, amount) VALUES (?, ?, ?, ?)", (today, trancard.value, trancat.value, tranval.value))
        c.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (tranval.value, trancard.value))
        db.commit()
        db.close()

    def total_balance_in_rub():
        rates = rub_rates()
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c = db.cursor()
        c.execute("SELECT balance, currency FROM accounts")
        accounts = c.fetchall()  # [(28000.0,"RUB"), (6000.0,"RUB"), (270000.0,"KZT"), ...]
        db.close()
        total = 0.0
        for balance, cur_code in accounts:
            rate = rates.get(cur_code)
            if rate is None:
                continue
            total += balance * rate

        return total
    
    total_rub = ft.Text(format(total_balance_in_rub(), '.2f'))
    
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Text(today),
                    ft.IconButton(ft.Icons.LIGHT_MODE, on_click=change_theme),
                    ft.IconButton(ft.Icons.PERSON, on_click=lambda _: page.go("/accounts")),
                    ft.IconButton(ft.Icons.MONEY_ROUNDED, on_click=lambda _: page.go("/transaction")),
                    curinfo,
                    ft.TextButton(text="Шма"),
                    ft.TextButton(text="Шма2"),
                    usd_kzt,
                    usd_rub,
                    rub_kzt,
                    total_rub,
                ],
            ),
        )
        if page.route == "/accounts":
            page.views.append(
                ft.View(
                    "/accounts",
                    [
                        homepage,
                        actype,
                        acname,
                        accurrency,
                        acbalance,
                        ft.ElevatedButton(text="Жмак", on_click=accounts_in),
                    ]
                )
            )
        if page.route == "/transaction":
            page.views.append(
                ft.View(
                    "/transaction",
                    [
                        homepage,
                        card_list,
                        category_list,
                        tranval,
                        ft.ElevatedButton(text="Шпак", on_click=transaction_in),
                        trancard,
                        trancat,
                    ]
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_views = page.views[-1]
        page.go(top_views.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(main)