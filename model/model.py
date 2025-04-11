import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
import sqlalchemy
import re
from langchain_community.chat_message_histories import SQLChatMessageHistory


# Загрузка переменных окружения
load_dotenv()


# Класс для управления чат-ботом D&D
class DNDChatbot:
    def __init__(self):
        # Получение API ключа
        self.api_key = os.getenv("MISTRAL_API_KEY")

        # Инициализация языковой модели
        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            temperature=0.7,  # Немного повышенная температура для креативности
        )

        self.system_prompt = (
            "Ты Narramancer — ведущий и рассказчик в ролевой игре, вдохновлённой Dungeons & Dragons.\n\n"
            "Твоя задача — создать живой, богатый, непредсказуемый мир для игрока, где он сам принимает решения, "
            "действует, разговаривает и бросает кубики. Ты — не герой истории. Ты — её создатель и ведущий.\n\n"
            "🎭 Взаимодействие с игроком:\n"
            "- Не говори за игрока. Никогда. Игрок говорит и действует сам. Ты не описываешь, что он думает, говорит или делает.\n"
            "- Не предлагай действия и броски одновременно. Если нужен бросок кубика — приостанови ход истории и дай только метку [roll:XdY]. "
            "Только после броска продолжай историю и предложи варианты или жди ответа игрока.\n"
            "- При каждом выборе обязательно добавляй: 'Ты можешь выбрать один из вариантов или предложить свой.'\n\n"
            "🧑‍🎤 Персонаж:\n"
            "- В начале игрок описывает своего персонажа: кто он, откуда, чего ищет.\n"
            "- После этого ты сам создаёшь и показываешь:\n"
            "  • Имя\n"
            "  • Расу\n"
            "  • Класс (например, воин, маг, плут и т.п.)\n"
            "  • Характеристики (от 1 до 20):\n"
            "      - Сила — физическая мощь и выносливость\n"
            "      - Ловкость — гибкость и скорость реакции\n"
            "      - Телосложение — здоровье, выносливость, сопротивляемость\n"
            "      - Интеллект — ум, логика, учёность\n"
            "      - Мудрость — интуиция, внимательность, внутренняя чуйка\n"
            "      - Харизма — обаяние, влияние, харизма\n"
            "  • Характеристики должны быть сбалансированы: сумма всех значений должна быть примерно 75–90\n"
            "  • Также ты должен указать уровень HP (жизни) по формуле:\n"
            "        HP = 10 + Телосложение×3 + Сила×1.5 + Ловкость×1.2 + Интеллект×0.5 + Мудрость×0.5 + Харизма×0.5\n"
            "  • Укажи текущий HP игрока, например: 'HP: HP / HP'\n"
            "  • Укажи базовую экипировку, внешний вид, краткую предысторию, имеющиеся предметы и магию\n"
            "  • Определи количество монет — от 0 до 1000, в зависимости от описания персонажа. Не давай много монет без причины.\n"
            "  • Монеты — важный игровой ресурс. Их можно тратить в тавернах, лавках, или они могут быть украдены. Отслеживай баланс.\n\n"
            "🎲 Кубики:\n"
            "- Используй метку вида [roll:1d20]. Не подставляй результат — игрок бросает сам.\n"
            "- Один бросок — одна ситуация. Игрок не может бросать несколько кубиков за раз.\n"
            "- Используй модификаторы: результат броска + (связанная характеристика - 10) / 2\n"
            "- Результат с учетом модификатора больше 10 - успех, но цифра имеет значение, даже если результат положительный - то есть 19 лучше 11 (атака интенсивнее, например).\n"
            "- Не предлагай бросок просто для случайности. Броски только для проверок, боя, инициативы, магии и лечения.\n"
            "- Для врагов броски не нужны — решай сам, как действуют NPC.\n\n"
            "⚔️ Бой и здоровье:\n"
            "- HP уменьшается при получении урона. Если HP падает ниже 0, персонаж погибает — игра заканчивается или начинается новая.\n"
            "- Лечение возможно зельями, магией, отдыхом — но не всегда доступно. Иногда бывают побочные эффекты (можешь предложить бросок кубика).\n"
            "- После боя обязательно сообщи обновлённый уровень HP игрока.\n\n"
            "🌍 Сюжет:\n"
            "- Создавай глубокий мир, полон тайн, моральных дилемм и неожиданных поворотов.\n"
            "- Не все персонажи должны быть добрыми — пусть будут грубые, хитрые, непредсказуемые.\n"
            "- Делай каждый сюжет уникальным. Без шаблонов.\n"
            "- Будь справедливым, но не слишком снисходительным. Пусть игрока иногда ждут неудачи\n\n"
            "📏 Максимум — 4000 символов в одном сообщении.\n\n"
            "Ты можешь использовать эмодзи, чтобы оживить повествование"
            "Ты — Narramancer. Веди игру!"
        )

        # Словарь для хранения истории чатов
        self.chat_histories = {}

        # Создаем директорию для базы данных, если она не существует
        os.makedirs("chat_histories", exist_ok=True)

        # Создание цепочки обработки
        self.chain = self.create_chain()

    def start_new_game(self, session_id: str):
        """Метод для начала новой игры с очисткой истории"""
        # Получаем текущую историю
        history = self.get_session_history(session_id)

        # Очищаем историю
        history.clear()

    def create_chain(self):
        """Создание цепочки обработки с историей сообщений"""
        # Создание шаблона чата
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{player_input}"),
            ]
        )

        # Основная цепочка с добавлением переменной roll
        from langchain_core.runnables import RunnablePassthrough

        base_chain = (
            RunnablePassthrough.assign(roll=lambda x: x.get("roll", ""))
            | prompt
            | self.llm
            | StrOutputParser()
        )

        # Создание цепочки с историей
        return RunnableWithMessageHistory(
            base_chain,
            self.get_session_history,
            input_messages_key="player_input",
            history_messages_key="chat_history",
            additional_variables=[
                "roll"
            ],  # Добавляем roll как дополнительную переменную
        )

    # Изменим взаимодействие с кубиками в методе interact

    def interact(
        self, player_input: str, session_id: str = "default_session", roll: str = None
    ):
        """Взаимодействие с чат-ботом с обработкой бросков кубика"""
        try:
            # Проверка наличия формата броска кубика
            roll_match = re.search(r"\[roll:(\d+)d(\d+)\]", player_input)

            if roll_match:
                # Извлечение параметров броска
                num_dice = int(roll_match.group(1))
                dice_sides = int(roll_match.group(2))

                # Если результат броска не передан, генерируем приглашение
                if roll is None:
                    return f"🎲 Тебе нужно бросить {num_dice}d{dice_sides}. Нажми на кнопку броска!"

                # Если результат броска передан, подставляем его
                roll_result = int(roll)

                # Оставляем метку как есть
                modified_input = player_input  # Не заменяем метку

                # Выполнение запроса с сохранением истории
                response = self.chain.invoke(
                    {"player_input": modified_input, "roll": str(roll_result)},
                    {"configurable": {"session_id": session_id}},
                )

                return response

            else:
                # Обычный режим без броска
                response = self.chain.invoke(
                    {"player_input": player_input, "roll": ""},
                    {"configurable": {"session_id": session_id}},
                )
                return response

        except Exception as e:
            return f"Произошла ошибка: {e}"

    def get_session_history(self, session_id: str):
        """Получение истории сообщений с использованием SQLite"""
        engine = sqlalchemy.create_engine("sqlite:///database/chat_history.db")
        return SQLChatMessageHistory(session_id=session_id, connection=engine)
