import flet as ft
import sqlite3 

from datetime import datetime

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Финансы"

    #общие кнопки
    homepage = ft.IconButton(ft.Icons.BACKSPACE, on_click=lambda _: page.go("/"))

    #Ввод курсов
    cvd = ft.TextField(label="Введите дату")
    cvuk = ft.TextField(label="Введите usd-kzt")
    cvur = ft.TextField(label="Введите usd-rub")
    cvrk = ft.TextField(label="Введите rub-kzt")

    #Ввод кошельков
    actype = ft.TextField(label="Введите тип")
    acname = ft.TextField(label="Введите название")
    accurrency = ft.TextField(label="Введите валюту")
    acbalance = ft.TextField(label="Введите баланс")

    #Ввод транзакций
    tranval = ft.TextField(label="Сумма")
    trancard = ft.Text("Т-банк")

    def get_info():
        pass

    def inform():
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c = db.cursor()
        c.execute("SELECT * FROM transactions")
        c.fetchall()
        db.close()

    def change_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.DARK
        page.update()

    def currency_in(e):
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c = db.cursor()
        c.execute("INSERT INTO currency (date, usd_kzt, usd_rub, rub_kzt) VALUES (?, ?, ?, ?)", (cvd.value, cvuk.value, cvur.value, cvrk.value))
        db.commit()
        db.close()

    def accounts_in(e):
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c = db.cursor()
        c.execute("INSERT INTO accounts (type, name, currency, balance) VALUES (?, ?, ?, ?)", (actype.value, acname.value, accurrency.value, acbalance.value))
        db.commit()
        db.close()

    def dropdown_card(e):
        trancard.value = e.control.value
        page.update()

    card_list = ft.Dropdown(editable = True, options = [
            ft.DropdownOption(key="Наличка"),
            ft.DropdownOption(key="Т-банк"),
            ft.DropdownOption(key="Каспи"),
            ft.DropdownOption(key="Сбербанк"),
            ft.DropdownOption(key="BuyBit"),
            ft.DropdownOption(key="OKX"),
            ft.DropdownOption(key="Binance"),
        ], 
        label = "wallet", 
        value = "Т-банк",
        on_change=dropdown_card)
    
    def option_currency():
        return [
            ft.DropdownOption(
                key="RUB",
            ),
            ft.DropdownOption(
                key="USD",
            ),
            ft.DropdownOption(
                key="KZT",
            ),
        ]
    
    def dropdown_currency(e):
        pass

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.IconButton(ft.Icons.LIGHT_MODE, on_click=change_theme),
                    ft.IconButton(ft.Icons.MONEY, on_click=lambda _: page.go("/currency")),
                    ft.IconButton(ft.Icons.PERSON, on_click=lambda _: page.go("/accounts")),
                    ft.IconButton(ft.Icons.MONEY_ROUNDED, on_click=lambda _: page.go("/transaction")),
                    ft.Dropdown(
                        editable=True,
                        label="currency",
                        value="RUB",
                        options=option_currency(),
                    ),
                ],
            ),
        )
        if page.route == "/currency":
            page.views.append(
                ft.View(
                    "/currency",
                    [
                        homepage,
                        cvd,
                        cvuk,
                        cvur,
                        cvrk,
                        ft.ElevatedButton(text="Жмак", on_click=currency_in),
                    ],
                )
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
                        trancard,
                        tranval,

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