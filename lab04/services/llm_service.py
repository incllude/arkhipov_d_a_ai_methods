from config.config import HF_API_TOKEN, LLAMA_URL, GPT_URL, START_PHRASE, MID_PHRASE, END_PHRASE
from typing import List
import aiohttp


class HuggingFaceService:
    
    def __init__(self):
        '''
        Сервис для взаимодействия с API Hugging Face
        '''
        self.headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        
    async def process(self, model_type: str, text: str, context: List[str]) -> str:
        '''
        Отправка запроса к API модели и получение результата
        
        Принимает на вход:
            model_type: тип модели (llama или gpt)
            text: текст для обработки
            context: список контекстных сообщений
        Возвращает:
            Сгенерированный моделью текст
        '''
        prompt = self.create_prompt(text, context)
        print(prompt)
        async with aiohttp.ClientSession() as session:
            # Выбор URL в зависимости от типа модели
            async with session.post(
                LLAMA_URL if model_type == "llama" else GPT_URL,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 200  # Ограничение длины генерации
                    }
                }
            ) as response:
                result = await response.json()
                # Возвращаем только новый сгенерированный текст, обрезая исходный промпт
                return result[0]["generated_text"][len(prompt):]
            
    def create_prompt(self, text: str, context: List[str]) -> str:
        '''
        Формирование промпта для модели
        
        Принимает на вход:
            text: основной текст
            context: список контекстных сообщений
        Возвращает:
            Готовый промпт для отправки модели
        '''
        # Замена переносов строк на пробелы
        context = [text.replace("\n", " ") for text in context]
        text = text.replace("\n", " ")
        
        # Сборка промпта из трех частей: начальная фраза, контекст и завершающая фраза
        prompt = START_PHRASE + '"' + text + '"\n\n'
        timeline = [f'    {i+1}. "{text}"' for i, text in enumerate(context)]
        prompt += MID_PHRASE + "\n" + " \n".join(timeline) + "\n\n"
        prompt += END_PHRASE

        return prompt
