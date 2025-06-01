class TwitterBotController {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.checkBotStatus();
        setInterval(() => this.checkBotStatus(), 5000);
    }

    initializeElements() {
        this.startBtn = document.getElementById('start-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.saveBtn = document.getElementById('save-config');
        this.resetBtn = document.getElementById('reset-config');
        this.statusIndicator = document.getElementById('status-indicator');
        this.configForm = document.getElementById('config-form');
        this.notification = document.getElementById('notification');
    }

    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startBot());
        this.stopBtn.addEventListener('click', () => this.stopBot());
        this.saveBtn.addEventListener('click', () => this.saveConfig());
        this.resetBtn.addEventListener('click', () => this.resetConfig());
    }

    async checkBotStatus() {
        try {
            const response = await fetch('/api/bot/status');
            const data = await response.json();
            this.updateBotStatus(data.is_running);
        } catch (error) {
            console.error('Error checking bot status:', error);
        }
    }

    updateBotStatus(isRunning) {
        if (isRunning) {
            this.statusIndicator.className = 'status-badge running';
            this.statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Running';
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
        } else {
            this.statusIndicator.className = 'status-badge stopped';
            this.statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Stopped';
            this.startBtn.disabled = false;
            this.stopBtn.disabled = true;
        }
    }

    async startBot() {
        try {
            const response = await fetch('/api/bot/start', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                this.showNotification('Bot started successfully!', 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error starting bot', 'error');
        }
    }

    async stopBot() {
        try {
            const response = await fetch('/api/bot/stop', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                this.showNotification('Bot stopped successfully!', 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error stopping bot', 'error');
        }
    }

    async saveConfig() {
    try {
        // Get all form inputs
        const inputs = this.configForm.querySelectorAll('input');
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');

        const config = {};

        // Get regular inputs
        inputs.forEach(input => {
            if (input.type !== 'checkbox') {
                config[input.name] = input.value;
            }
        });

        // Get checkbox inputs
        checkboxes.forEach(checkbox => {
            config[checkbox.name] = checkbox.checked;
        });

        console.log('Sending config:', config); // Debug log

        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ bot_settings: config })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            this.showNotification('Configuration saved successfully!', 'success');
        } else {
            this.showNotification(data.message || 'Unknown error', 'error');
        }
    } catch (error) {
        console.error('Save config error:', error);
        this.showNotification(`Error saving configuration: ${error.message}`, 'error');
    }
}

    resetConfig() {
        if (confirm('Are you sure you want to reset to default settings?')) {
            location.reload();
        }
    }

    showNotification(message, type) {
        this.notification.textContent = message;
        this.notification.className = `notification ${type} show`;

        setTimeout(() => {
            this.notification.classList.remove('show');
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TwitterBotController();
});
