# 🎲🧙‍♂️ **Narramancer** — твой AI-мастер подземелий

> **Telegram-бот**, использующий LLM для создания приключений и ведения ролевых игр, вдохновленная **Dungeons & Dragons**.
>
> https://t.me/narramancer_bot

---

## 🧠 **Основная идея**

**Narramancer** — это AI-гейммастер, созданный для того, чтобы проводить игроков через увлекательные приключения. Бот выполняет роль ведущего и рассказчика, моделируя ситуацию, генерируя сюжет и предлагая броски кубиков с учётом характеристик персонажа.

### 🎯 **Целевая аудитория**

- **Новички** в настольных ролевых играх, которым не нужно углубляться в сложные правила.
- **Любители** хороших историй, которые хотят активно участвовать в создании сюжета.
- **Игроки** в одиночку, которым не нужно взаимодействие с реальным мастером.
- **Игроки DnD** и TTRPG, которым не хватает гейм-мастера.
- **Создатели контента**, ищущие источник вдохновения для историй.

---

## ✨ **Уникальные особенности**

- **Ручной контроль бросков кубиков**: игрок сам инициирует бросок кубика.
- **Автоматическое применение модификаторов** характеристик при вычислении результата.
- **Персонализированный сторителлинг**: бот создаёт уникальные приключения на основе решений игрока.
- **Поддержка многосессионных игр**: история игры сохраняется и используется для последующих сессий.
- **Минималистичный интерфейс через Telegram**: никаких приложений и входов в аккаунты.

---

## 🛠️ **Необходимые библиотеки и ресурсы**

- **LLM API**: [`mistralai`](https://github.com/mistralai/mistral-src)
- **Telegram Bot**: [`aiogram`](https://github.com/aiogram/aiogram) 3.x
- **LangChain** для создания цепочек обработки запросов и управления историей чатов.
- **SQLAlchemy** — для работы с базой данных.
- **SQLite** — для хранения истории чатов и игровых данных.
- **dotenv** — для загрузки переменных окружения.

---

## 🧩 **Особенности реализации**

### 💡 **Работа с данными**

- **Сохранение истории**: Все чаты сохраняются в базе данных SQLite, что позволяет поддерживать контекст между сессиями.
- **Механизм истории**: Используется цепочка обработки с помощью `LangChain`, которая учитывает как запросы игрока, так и историю предыдущих взаимодействий.
- **Векторизация**: Для генерации эмбеддингов используется Mistral API, который адаптирует ответы под контекст игры.

### 🎲 **Техника промптинга и обработки кубиков**

- Используется формат метки броска кубика: `[roll:XdY]`, где X — количество бросков, Y — количество граней у кубика.
- При получении запроса с меткой броска кубика бот ожидает от игрока результат, который затем подставляется в игру.
- Важный элемент: **модификаторы характеристик**. Например, если результат броска на 20-гранном кубике с учётом модификатора характеристики больше 10, это считается успешным действием.

### ⚔️ **Бой и здоровье**

- HP персонажа уменьшается при получении урона. Если HP падает ниже 0 — персонаж погибает.
- Лечение доступно через зелья, магию или отдых. Также, после каждого боя, бот обновляет информацию о текущем состоянии здоровья игрока.

---

## 🚀 **Деплой и взаимодействие с пользователем**

- **Место развертывания**: Бот развернут на сервере с использованием Railway для обеспечения доступности и масштабируемости.
- **Взаимодействие с пользователем**: Игра происходит через Telegram. Пользователь отправляет команды и получает историю с возможностью самостоятельно бросать кубики и делать выбор.

Проект можно развернуть на сервере с установленным Python, например, на **Render** или **Heroku**. Взаимодействие происходит через Telegram-бота, для чего используется библиотека `aiogram`. Вы можете легко запустить проект на своем сервере или хостинге:

1. ```bash
   $ git clone https://github.com/yourusername/narramancer-llm
   $ cd  narramancer-llm
   $ python -m venv venv
   $ source venv/bin/activate   # Для Windows: venv\Scripts\activate
   $ pip install -r requirements.txt
   $ python bot.py
   ```

---

## 🎯 Идея для улучшения

1. Добавление данных из базы по монстрам, магии и предметам из DnD конкретные характеристики и реализовать показ картинок этих вещей с помощью DnD api https://www.dnd5eapi.co
2. Добавление кубика с шестью гранями для боев
3. Добавление нейронной сети для генерации картинок, чтобы создавать изображения локаций
4. Добавление повышения уровня персонажа и увеличение его характеристик
5. Улучшение партийности (пока кофортнее всего играть одному)
