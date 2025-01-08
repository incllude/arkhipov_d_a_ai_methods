from keyboards.keyboards import start_keyboard, model_keyboard
from services.retriever_service import RetrieverService
from services.llm_service import HuggingFaceService
from config.config import PATH_TO_DATA, TOP_K
from aiogram.filters import Command
from aiogram import Router, types

# Инициализация роутера для обработки сообщений
router = Router()

# Инициализация сервиса для работы с языковыми моделями
hf_service = HuggingFaceService()
# Инициализация сервиса для поиска релевантных новостей
retriever_service = RetrieverService(
    path_to_df=PATH_TO_DATA / "news.csv",
    path_to_embeddings=PATH_TO_DATA / "embeddings.npy",
    k=TOP_K
)

# Словарь для хранения выбранной модели для каждого пользователя
user_models = {}
# Отображение названий моделей на их идентификаторы
model_mapping = {
    "Llama 3 8B": "llama",
    "GPT-Neo 2.7B": "gpt"
}


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    '''
    Обработчик команды /start
    '''
    await message.answer(
        "Привет! Я бот для аггрегации новостей с РИА.\n"
        "Выберите модель для работы",
        reply_markup=start_keyboard()
    )


@router.message(lambda message: message.text in ["/model", "Выбрать модель"])
async def choose_model(message: types.Message):
    '''
    Обработчик команды выбора модели
    '''
    await message.answer(
        "Пожалуйста, выберите модель:",
        reply_markup=model_keyboard()
    )


@router.message(lambda message: message.text in ["Llama 3 8B", "GPT-Neo 2.7B"])
async def handle_model_selection(message: types.Message):
    '''
    Обработчик выбора конкретной модели пользователем
    '''
    # Сохранение выбранной модели для конкретного пользователя
    user_models[message.from_user.id] = model_mapping[message.text]
    await message.answer(
        f"Выбрана модель: {message.text}\n",
        "Напишите запрос"
    )


async def next_move_selection(message: types.Message):
    '''
    Обработчик отображения сообщения о следующем действии
    '''
    await message.answer(
        f"Запрос обрабатывается\nВведите следующий запрос или выберите другую модель",
        reply_markup=start_keyboard()
    )


@router.message()
async def handle_message(message: types.Message):
    '''
    Основной обработчик текстовых сообщений
    '''
    user_text = message.text
    user_id = message.from_user.id

    # Получение типа модели для пользователя
    model_type = user_models.get(user_id, None)
    if model_type is None:
        await message.answer(
            "Пожалуйста, сначала выберите модель",
            reply_markup=start_keyboard()
        )
        return
    await next_move_selection(message)
    
    # Поиск релевантных новостей по запросу пользователя
    appropriate_news = await retriever_service.process(user_text)
    try:
        # Суммаризация запроса выбранной языковой моделью
        response = await hf_service.process(
            model_type=model_type,
            text=user_text,
            context=appropriate_news
        )
        await message.answer(response, reply_markup=start_keyboard())
    except Exception as e:
        # Обработка ошибок
        await message.answer(
            "Извините, произошла ошибка при обработке запроса.",
            reply_markup=start_keyboard()
        )
