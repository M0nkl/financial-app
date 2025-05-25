import flet as ft
import sqlite3 
from datetime import datetime
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import base64

CBR_JSON = "https://www.cbr-xml-daily.ru/daily_json.js"

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

    chart = ft.Image()

    def update_chart(target_cur: str):
        dist   = compute_distribution(target_cur)
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        img_b64 = make_pie_image(dist, target_cur, dark=is_dark)
        chart.src_base64 = img_b64
        rr = rub_rates()
        if target_cur == "USD":
            total_rub.value = ("Ваш общий баланс в выбранной валюте: " +  format(total_balance_in_rub() / rr["USD"], '.2f'))
        if target_cur == "KZT":
            total_rub.value = ("Ваш общий баланс в выбранной валюте: " +  format(total_balance_in_rub() / rr["KZT"], '.2f'))
        if target_cur == "RUB":
            total_rub.value = ("Ваш общий баланс в выбранной валюте: " +  format(total_balance_in_rub(), '.2f'))
        page.update()


    def fetch_wallets():
        db = sqlite3.connect("UserData.db", check_same_thread=False)
        c  = db.cursor()
        c.execute("SELECT name, balance, currency FROM accounts")
        rows = c.fetchall()
        db.close()
        return rows

    def change_theme(e):
        # переключаем тему
        page.theme_mode = (
            ft.ThemeMode.LIGHT
            if page.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        # перезапускаем отрисовку текущего экрана
        route_change(page)

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
            total_rub.value = ("Ваш общий баланс в выбранной валюте: " +  format(total_balance_in_rub() / rr["USD"], '.2f'))
        if cur == "KZT":
            total_rub.value = ("Ваш общий баланс в выбранной валюте: " +  format(total_balance_in_rub() / rr["KZT"], '.2f'))
        if cur == "RUB":
            total_rub.value = ("Ваш общий баланс в выбранной валюте: " +  format(total_balance_in_rub(), '.2f'))
        page.update()

    curinfo = ft.Dropdown(
        editable=True,
        label="currency",
        value="RUB",
        on_change=lambda e: update_chart(e.control.value),
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
    
    def fetch_rates():
        resp = requests.get(CBR_JSON)
        resp.raise_for_status()
        data = resp.json()["Valute"]
        rates = {"RUB": 1.0}
        for code, info in data.items():
            nominal   = info["Nominal"]
            value_rub = info["Value"]
            rates[code] = value_rub / nominal
        return rates
    
    def compute_distribution(target_currency: str) -> dict:
        rates   = fetch_rates()
        wallets = fetch_wallets()
        dist = {}
        for name, bal, cur in wallets:
            # если в API нет курса — пропускаем
            if cur not in rates or target_currency not in rates:
                continue
            # баланс → в рубли → в целевую валюту
            rub       = bal * rates[cur]
            converted = rub / rates[target_currency]
            dist[name] = converted
        return dist
    
    def make_pie_image(dist: dict, target_currency: str, dark: bool) -> str:
        text_color = "white" if dark else "black"

        # 1) Сортируем пары (label, size) по size убыванию
        items = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)
        labels, sizes = zip(*items)

        total = sum(sizes)
        percents = [100 * s / total for s in sizes]

        # 2) Формируем подписи легенды в том же порядке
        legend_labels = [
            f"{label}: {value:,.2f} {target_currency} ({percent:.1f}%)"
            for label, value, percent in zip(labels, sizes, percents)
        ]

        # 3) Рисуем прозрачное полотно
        fig, ax = plt.subplots(figsize=(6,6), facecolor="none")
        ax.set_facecolor("none")

        # 4) Круг без встроенных меток
        wedges, _ = ax.pie(
            sizes,
            startangle=90,
            radius=0.7,
            center=(0.3, 0.5),
            labels=None
        )
        ax.axis("equal")

        # 5) Легенда справа, с уже отсортированными записями
        legend = ax.legend(
            wedges,
            legend_labels,
            title="Кошельки",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            frameon=False,
            prop={"size": 10}
        )
        for txt in legend.get_texts():
            txt.set_color(text_color)
        legend.get_title().set_color(text_color)

        # 6) Сохраняем картинку как прозрачный PNG → Base64
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()
            
    total_rub = ft.Text("Ваш общий баланс в выбранной валюте: " + format(total_balance_in_rub(), '.2f'))
    
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
                    chart,
                ],
            ),
        )
        update_chart(curinfo.value)
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