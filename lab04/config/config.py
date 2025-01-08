from dotenv import load_dotenv
from pathlib import Path
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токенов для HF и TG
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
LLAMA_URL = os.getenv("LLAMA_URL")
GPT_URL = os.getenv("GPT_URL")

# Ключи для Yandex Cloud
YACLOUD_FOLDER_KEY = os.getenv("YACLOUD_FOLDER_KEY")
YACLOUD_API_KEY = os.getenv("YACLOUD_API_KEY")
TOP_K = 2

# Путь к директории с данными
PATH_TO_DATA = Path(__file__).parent.parent / "data"

# Промпты для формирования запроса
START_PHRASE = "Пользователь сделал запрос со следующим содержанием: "
MID_PHRASE = "Далее в хронологическом порядке перечислены новости о теме, указанной пользователем:"
END_PHRASE = "ДАЛЕЕ ОТВЕЧАЙ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ. Краткое изложение только тех событий, которые подходят под запрос пользователя:\n"
