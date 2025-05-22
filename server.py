from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Настройки почты
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('EMAIL_USER')  # Ваш email
SENDER_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Ваш пароль приложения

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        data = request.form
        recipient_email = data.get('email')
        
        if not recipient_email:
            return jsonify({'success': False, 'error': 'Email не указан'}), 400

        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = 'Спасибо за покупку Windows!'

        # Текст письма
        body = """
        Здравствуйте!

        Спасибо за покупку Windows! Мы рады, что вы выбрали наш продукт.

        В ближайшее время мы свяжемся с вами для подтверждения заказа и предоставления дальнейших инструкций.

        С уважением,
        Команда Windows Store
        """
        
        msg.attach(MIMEText(body, 'plain'))

        # Подключаемся к серверу и отправляем письмо
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        return jsonify({'success': True})

    except Exception as e:
        print(f"Ошибка при отправке письма: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 