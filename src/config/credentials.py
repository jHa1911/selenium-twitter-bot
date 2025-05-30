from .settings import Settings

class CredentialsManager:
    def __init__(self, settings: Settings):
        self.settings = settings

    def get_twitter_credentials(self):
        return {
            'username': self.settings.twitter_username,
            'password': self.settings.twitter_password,
            'email': self.settings.twitter_email
        }
