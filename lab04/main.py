import asyncio
from aiogram import Bot, Dispatcher
from config.config import BOT_TOKEN
from handlers.message_handlers import router
import logging


async def main():
    '''
    Основная функция для запуска бота
    '''
    # Настройка базового логирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Инциализация бота
    bot = Bot(token=BOT_TOKEN)
    # Создание диспетчер для обработки обновлений
    dp = Dispatcher()
    
    # Подключение роутер с обработчиками сообщений
    dp.include_router(router)
    
    # Запуск бота и начинаем получать обновления только через сообщения
    await dp.start_polling(bot, allowed_updates=["message"])


if __name__ == "__main__":
    asyncio.run(main())
