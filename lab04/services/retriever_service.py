from config.config import YACLOUD_FOLDER_KEY, YACLOUD_API_KEY
from yandex_cloud_ml_sdk import AsyncYCloudML
from scipy.spatial.distance import cdist
import pandas as pd
import numpy as np


class RetrieverService:

    def __init__(
        self,
        path_to_df: str,
        path_to_embeddings: str,
        k: int
    ) -> None:
        '''
        Сервис для поиска релевантных новостей по запросу
        
        Принимает на вход:
            path_to_df: путь к CSV файлу с новостями
            path_to_embeddings: путь к файлу с векторными представлениями
            k: количество возвращаемых документов
        '''
        # Загрузка и предобработка датафрейма с новостями
        self.news = pd.read_csv(path_to_df)
        self.news.publish_date = pd.to_datetime(self.news.publish_date, dayfirst=True).dt.date
        self.news = self.news.drop_duplicates(subset=["uid"])
        self.news.content = self.news.apply(self.filter_from_trash, axis=1)

        # Загрузка векторных представлений
        self.doc_embeddings = np.load(path_to_embeddings)
        self.doc_embeddings /= np.linalg.norm(self.doc_embeddings, axis=-1).reshape(-1, 1)

        # Проверка соответствия размерностей
        assert len(self.news) == len(self.doc_embeddings)

        # Инициализация модели для векторизации запросов
        sdk = AsyncYCloudML(
            folder_id=YACLOUD_FOLDER_KEY,
            auth=YACLOUD_API_KEY
        )
        self.query_model = sdk.models.text_embeddings("query")
        self.k = k

    @staticmethod
    def filter_end(string: str) -> str:
        '''
        Удаление технической информации в конце строки

        Принимает на вход:
            string: строка с новостью
        Возвращает:
            Очищенная строка
        '''
        if string[-5:] == "Вчера":
            return string[:-5]
    
        string_ = " ".join(string.split(" ")[:-1])
        
        try:
            while string_[-1].isnumeric():
                string_ = string_[:-1]
        except:
            return None
        
        return string_.strip()
    
    @staticmethod
    def filter_from_trash(row: pd.Series) -> str:
        '''
        Очистка текста новости от мусора и технической информации

        Принимает на вход:
            row: строка с новостью
        Возвращает:
            Очищенный текст новости
        '''
        string = row.content
        t = string.replace("\xad", "").replace("\xa0", "").replace("˗", "-").replace(":", "").strip()
        stop_list = ["", " ", "Поделиться", "Повторить", "1.7%Нет", "Сибирь", "Гости", "ИнфографикаСмотреть", "27 маая", "Культура"]
        t = list(filter(lambda x: x not in stop_list, t.split("\n")))
        x = t[0].split(".")
        if len(x) > 1 and not (len(x) == 2 and x[-1] == ""):
            t[0] = ".".join(x[1:])
        else:
            t[0] = ".".join(x)
        t = list(map(lambda x: x.strip(), t))
        t = list(map(lambda x: x[:-1] if x[-1] == "." else x, t))
    
        for i in range(len(t)):
            try:
                if t[i][-4:].isnumeric():
                    t[i] = t[i][:-6]
            except:
                t[i] = " "
    
        t = list(map(RetrieverService.filter_end, t))
        t = list(filter(lambda x: x is not None, t))
        if len(t) >= 2 and t[-1] == "Такого Telegram-канала, как у нас, нет ни у кого. Он для тех, кто хочет делать выводы":
            t = t[:-1]
        return ". ".join(t)
    
    async def process(self, query: str) -> pd.DataFrame:
        '''
        Поиск релевантных новостей по запросу

        Принимает на вход:
            query: запрос пользователя
        Возвращает:
            pd.DataFrame с релевантными новостями
        '''
        # Получение векторного представления запроса
        query_embedding = await self.query_model.run(query)
        query_embedding = np.array(query_embedding)
        query_embedding /= np.linalg.norm(query_embedding)
        
        # Расчет косинусного расстояния между запросом и документами
        dist = cdist([query_embedding], self.doc_embeddings, metric="cosine").reshape(-1)
        dist[np.isnan(dist)] = 10

        # Возврат k наиболее релевантных новостей
        news = self.news.iloc[np.argsort(dist)[:self.k]].sort_values("publish_date", ascending=True).content.tolist()
        # Обрезка текстов до 200 символов для корректной работы GPT
        news = list(map(lambda x: x[:200], news))
        return news
