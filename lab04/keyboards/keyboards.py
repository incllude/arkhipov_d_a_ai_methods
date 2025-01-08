from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def start_keyboard() -> ReplyKeyboardMarkup:
    '''
    Создает и возвращает стартовую клавиатуру для выбора модели
    
    Возвращает:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопкой "Выбрать модель"
    '''
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Выбрать модель")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def model_keyboard() -> ReplyKeyboardMarkup:
    '''
    Создает и возвращает клавиатуру для выбора одной из двух моделей
    
    Возвращает:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками выбора моделей
    '''
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Llama 3 8B"),
                KeyboardButton(text="GPT-Neo 2.7B")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard
