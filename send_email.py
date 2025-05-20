from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

app = Flask(__name__)
# Настраиваем CORS для разрешения всех источников
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Конфигурация email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('EMAIL_USER')
SENDER_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Проверяем загруженные переменные окружения
print("Проверка конфигурации:")
print(f"EMAIL_USER: {SENDER_EMAIL}")
print(f"EMAIL_PASSWORD: {'*' * len(SENDER_PASSWORD) if SENDER_PASSWORD else 'Не установлен'}")

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

if __name__ == '__main__':
    print("\nЗапуск сервера для отправки email...")
    app.run(port=5000, debug=True)
