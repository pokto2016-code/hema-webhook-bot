from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

class TradingViewWebhook:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.telegram_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
    def send_telegram(self, message):
        """Отправка сообщения в Telegram"""
        try:
            response = requests.post(
                self.telegram_url,
                json={
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Telegram error: {e}")
            return False
    
    def format_signal_message(self, data):
        """Форматирование сообщения о сигнале"""
        symbol = data.get('ticker', 'Unknown')
        signal_type = data.get('signal_type', 'Signal')
        direction = data.get('direction', '')
        price = data.get('price', 0)
        strength = data.get('strength', 0)
        
        # Эмодзи для сигналов
        emoji_map = {
            "STRONG": "🚀", "WEAK": "⚠️", 
            "REVERSAL": "🔄", "DIVERGENCE_STRONG": "📈"
        }
        
        direction_emoji = "🟢" if direction == "LONG" else "🔴"
        signal_emoji = emoji_map.get(signal_type, "📊")
        
        message = f"""
{signal_emoji} <b>HEMA PRO SIGNAL</b> {signal_emoji}
══════════════════════
{direction_emoji} <b>Symbol:</b> {symbol}
📊 <b>Signal:</b> {signal_type} {direction}
💰 <b>Price:</b> ${float(price):.4f}
💪 <b>Strength:</b> {strength}/100
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
📍 <b>Server:</b> Render.com
══════════════════════
"""
        return message

# Создаем обработчик
webhook_handler = TradingViewWebhook()

@app.route('/webhook/hema', methods=['POST'])
def hema_webhook():
    """Основной webhook для HEMA сигналов"""
    try:
        data = request.get_json()
        logging.info(f"Received webhook: {data}")
        
        if not data:
            return jsonify({"status": "error", "message": "No data"}), 400
        
        # Форматируем и отправляем сообщение
        message = webhook_handler.format_signal_message(data)
        success = webhook_handler.send_telegram(message)
        
        if success:
            logging.info("Signal sent to Telegram successfully")
            return jsonify({"status": "success"}), 200
        else:
            logging.error("Failed to send to Telegram")
            return jsonify({"status": "error", "message": "Telegram failed"}), 500
            
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({
        "status": "healthy",
        "service": "HEMA Webhook Bot",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    })

@app.route('/')
def home():
    """Главная страница"""
    return """
    <h1>🤖 HEMA Pro Webhook Bot</h1>
    <p>Сервер работает и готов принимать сигналы!</p>
    <p>Webhook URL: <code>/webhook/hema</code></p>
    <p><a href="/health">Проверить статус</a></p>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)