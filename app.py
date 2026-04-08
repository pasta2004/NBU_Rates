from flask import Flask, render_template, request
from db import get_connection
from fetch_rates import fetch_rates_from_api
from datetime import datetime

app = Flask(__name__)

def data_exists(date_str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM currencies WHERE date=%s", (date_str,))
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count > 0


def save_rates(data):
    conn = get_connection()
    cursor = conn.cursor()

    for item in data:
        numeric_code = item['r030']
        code = item['cc']
        name = item['txt']
        rate = item['rate']
        date_obj = datetime.strptime(item['exchangedate'], '%d.%m.%Y').date()

        cursor.execute("""
            INSERT INTO currencies (numeric_code, currency_code, currency_name, rate, date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE rate=%s
        """, (numeric_code, code, name, rate, date_obj, rate))

    conn.commit()
    cursor.close()
    conn.close()



def fetch_rates(date_str=None):
    if date_str:
        date_obj = date_str
    else:
        date_obj = datetime.now().strftime('%Y-%m-%d')

    if data_exists(date_obj):
        return

    data = fetch_rates_from_api(date_str)

    if data:
        save_rates(data)


# 🔹 отримання з БД
def get_rates(date_str=None, search=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if not date_str:
        cursor.execute("""
            SELECT * FROM currencies 
            WHERE date = (SELECT MAX(date) FROM currencies)
        """)
    else:
        if search:
            cursor.execute("""
                SELECT * FROM currencies 
                WHERE date=%s AND currency_code LIKE %s
            """, (date_str, f"%{search.upper()}%"))
        else:
            cursor.execute("SELECT * FROM currencies WHERE date=%s", (date_str,))

    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return data


@app.route('/', methods=['GET', 'POST'])
def index():
    selected_date = None
    search = ""
    message = None

    if request.method == 'POST':
        selected_date = request.form.get('date')
        search = request.form.get('search')

        if selected_date:
            fetch_rates(selected_date)
            rates = get_rates(selected_date, search)

            if not rates:
                message = f"На {selected_date} курс ще не доступний ❌"
        else:
            fetch_rates()
            rates = get_rates(search=search)
    else:
        fetch_rates()
        rates = get_rates()

    return render_template(
        'index.html',
        rates=rates,
        selected_date=selected_date,
        search=search,
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)