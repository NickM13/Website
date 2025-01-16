import dotenv
import os

dotenv.load_dotenv()

class Config():
    minecraft_logs = os.getenv("MINECRAFT_LOGS")
