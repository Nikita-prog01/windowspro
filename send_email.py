from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import traceback
from yookassa import Payment
import uuid
from yookassa import Configuration

load_dotenv()

app = Flask(__name__)
# Настраиваем CORS для разрешения всех источников
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Конфигурация email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('EMAIL_USER')
SENDER_PASSWORD = os.getenv('EMAIL_PASSWORD')

# ЮKassa config (лучше вынести в .env)
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')

# Проверяем загруженные переменные окружения
print("Проверка конфигурации:")
print(f"EMAIL_USER: {SENDER_EMAIL}")
print(f"EMAIL_PASSWORD: {'*' * len(SENDER_PASSWORD) if SENDER_PASSWORD else 'Не установлен'}")

# Проверка конфигурации ЮKassa
print(f"YOOKASSA_SHOP_ID: {YOOKASSA_SHOP_ID}")
print(f"YOOKASSA_SECRET_KEY: {'*' * len(YOOKASSA_SECRET_KEY) if YOOKASSA_SECRET_KEY else 'Не установлен'}")

from yookassa import Configuration
Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

def send_simple_email(recipient_email):
    try:
        print(f"Попытка отправки письма на {recipient_email}")
        
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = "Спасибо за покупку Windows 11"

        # Текст письма
        body = """
        Спасибо за покупку Windows 11!

        Мы рады, что вы выбрали наш магазин. В ближайшее время с вами свяжется наш менеджер для подтверждения заказа.

        С уважением,
        Команда Windows Store
        """

        msg.attach(MIMEText(body, 'plain'))

        print("Подключение к SMTP серверу...")
        # Подключаемся к серверу и отправляем письмо
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        print("Включение TLS...")
        server.starttls()
        print("Авторизация...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("Отправка письма...")
        server.send_message(msg)
        print("Закрытие соединения...")
        server.quit()
        print("Письмо успешно отправлено!")

        return True
    except Exception as e:
        print("\nОШИБКА ПРИ ОТПРАВКЕ EMAIL:")
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение ошибки: {str(e)}")
        print("\nПолный стек ошибки:")
        print(traceback.format_exc())
        return False

@app.route('/send_email', methods=['POST', 'OPTIONS'])
def handle_email():
    if request.method == 'OPTIONS':
        # Обработка preflight запроса
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        print("\nПолучен новый запрос на отправку email")
        data = request.form
        email = data.get('email')
        print(f"Получен email: {email}")

        if not email:
            print("Ошибка: Email не указан")
            return jsonify({'success': False, 'error': 'Email не указан'}), 400

        if send_simple_email(email):
            response = jsonify({'success': True})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            response = jsonify({'success': False, 'error': 'Ошибка при отправке email'}), 500
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

    except Exception as e:
        print("\nОШИБКА В ОБРАБОТЧИКЕ:")
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение ошибки: {str(e)}")
        print("\nПолный стек ошибки:")
        print(traceback.format_exc())
        response = jsonify({'success': False, 'error': str(e)}), 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/create_payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json() or request.form
        email = data.get('email')
        name = data.get('name')
        product = data.get('product')
        price = data.get('price')  # в рублях, строкой или числом
        if not (email and product and price):
            return jsonify({'success': False, 'error': 'Необходимы email, product, price'}), 400
        # Генерируем уникальный идентификатор платежа
        payment_id = str(uuid.uuid4())
        # Создаем платеж
        payment = Payment.create({
            "amount": {
                "value": str(price),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://windowspro.store/"  # после оплаты
            },
            "capture": True,
            "description": f"Покупка {product} для {email}",
            "metadata": {
                "email": email,
                "name": name,
                "product": product,
                "payment_id": payment_id
            }
        })
        confirmation_url = payment.confirmation.confirmation_url
        return jsonify({'success': True, 'confirmation_url': confirmation_url})
    except Exception as e:
        print("\nОШИБКА ПРИ СОЗДАНИИ ПЛАТЕЖА:", str(e))
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/yookassa_webhook', methods=['POST'])
def yookassa_webhook():
    try:
        event = request.get_json()
        if event and event.get('event') == 'payment.succeeded':
            payment_obj = event['object']
            metadata = payment_obj.get('metadata', {})
            email = metadata.get('email')
            name = metadata.get('name')
            product = metadata.get('product')
            # Здесь можно отправить письмо с ключом активации
            send_simple_email(email)  # или send_license_email(email, name, product)
            print(f"Платеж успешен для {email}, продукт: {product}")
        return jsonify({'status': 'ok'})
    except Exception as e:
        print("\nОШИБКА В WEBHOOK:", str(e))
        print(traceback.format_exc())
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    print("\nЗапуск сервера для отправки email...")
    app.run(port=5000, debug=True)
 