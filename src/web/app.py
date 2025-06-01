from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import subprocess
import signal
from .config_manager import ConfigManager

app = Flask(__name__)
CORS(app)

config_manager = ConfigManager()
bot_process = None

@app.route('/')
def index():
    config = config_manager.get_config()
    return render_template('index.html', config=config)

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(config_manager.get_config())

@app.route('/api/config', methods=['POST'])
def update_config():
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        if data is None:
            return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400

        bot_settings = data.get('bot_settings', {})
        if not bot_settings:
            return jsonify({'status': 'error', 'message': 'No bot_settings found in request'}), 400

        # Validate numeric values
        numeric_fields = ['MAX_REPLIES_PER_DAY', 'MAX_REPLIES_PER_HOUR', 'MIN_DELAY_SECONDS',
                        'MAX_DELAY_SECONDS', 'MAX_FOLLOWS_PER_DAY', 'MAX_LIKES_PER_DAY', 'MAX_LIKES_PER_HOUR']

        for field in numeric_fields:
            if field in bot_settings:
                try:
                    bot_settings[field] = int(bot_settings[field])
                except (ValueError, TypeError):
                    return jsonify({'status': 'error', 'message': f'Invalid value for {field}'}), 400

        # Validate boolean values
        boolean_fields = ['ENABLE_AUTO_FOLLOW_BACK', 'ENABLE_AUTO_LIKE_FOLLOWING']
        for field in boolean_fields:
            if field in bot_settings:
                if isinstance(bot_settings[field], str):
                    bot_settings[field] = bot_settings[field].lower() in ['true', '1', 'yes', 'on']
                else:
                    bot_settings[field] = bool(bot_settings[field])

        # Update configuration
        success = config_manager.update_config({'bot_settings': bot_settings})
        if not success:
            return jsonify({'status': 'error', 'message': 'Failed to save configuration'}), 500

        return jsonify({'status': 'success', 'message': 'Configuration updated successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    global bot_process
    try:
        if bot_process and bot_process.poll() is None:
            return jsonify({'status': 'error', 'message': 'Bot is already running'})

        # Start the bot process
        bot_process = subprocess.Popen([sys.executable, 'main.py'],
                    cwd=os.path.join(os.path.dirname(__file__), '../..'))

        config_manager.update_config({'bot_status': 'running'})
        return jsonify({'status': 'success', 'message': 'Bot started successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    global bot_process
    try:
        if bot_process and bot_process.poll() is None:
            bot_process.terminate()
            bot_process.wait(timeout=10)

        config_manager.update_config({'bot_status': 'stopped'})
        return jsonify({'status': 'success', 'message': 'Bot stopped successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    global bot_process
    is_running = bot_process and bot_process.poll() is None
    status = 'running' if is_running else 'stopped'

    config_manager.update_config({'bot_status': status})
    return jsonify({'status': status, 'is_running': is_running})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
