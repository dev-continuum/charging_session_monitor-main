from config import Settings

settings = Settings()


class DbCommunicator:
    def __init__(self):
        self.db_api = settings.DB_API

    def get_current_session_data(self):
        return ""