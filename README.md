# Rosstat Parser API

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.142-009688)
![Playwright](https://img.shields.io/badge/Playwright-1.63-2EAD33)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Асинхронный API-сервис для получения данных о формах отчетности с официального сайта Росстата по ИНН организации. 
Сервис автоматизирует поиск, обходит защиту от ботов, парсит HTML-таблицу и сохраняет результат в Excel-файл.

## 🚀 Возможности

- Получение перечня форм отчетности по ИНН (10 или 12 цифр).
- Автоматическая навигация по сайту Росстата (hover, клики, ввод).
- Парсинг динамической HTML-таблицы с защитой от пустых строк.
- Сохранение данных в Excel-файл (`.xlsx`) с автошириной колонок.
- Обход базовой антибот-защиты (настройка User-Agent, отключение флагов автоматизации).
- Полное покрытие тестами (pytest + unittest.mock).

## 🛠 Технологии

- **Python 3.12+**
- **FastAPI** — веб-фреймворк для API
- **Playwright** — автоматизация браузера (async API)
- **OpenPyXL** — запись в Excel
- **Poetry** — управление зависимостями
- **Docker** / **Docker Compose** — контейнеризация
- **Pytest** — тестирование
- **Ruff** — линтинг и форматирование

## 📋 Требования

- Установленный [Python 3.12](https://www.python.org/downloads/) или выше.
- Установленный [Poetry](https://python-poetry.org/docs/#installation).
- (Опционально) [Docker](https://www.docker.com/products/docker-desktop/) для запуска в контейнере.

## ⚙️ Установка и запуск (локально)

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/ВашНик/rosstat-parser.git
   cd rosstat-parser
   
2. **Установите зависимости:**
   ```bash
   poetry install 

3. **Установите браузеры для работы Playwright:**
   ```bash
   poetry run playwright install chromium
   
4. **Запустите сервер (для Windows):**
   ```bash
   poetry rin uvicorn src.main:app --reload --loop asyncio

5. **Откройте Swagger UI:**
   Перейдите по адресу http://localhost:8000/docs

## 🐳 Запуск через Docker

1. **Соберите и запустите контейнеры:**
   ```bash
   docker compose up --build

2. **API будет доступно по адресу:**
   http://localhost:8000/docs

3. **Остановить контейнеры:**
   docker compose down

## 📡 Использование API
Эндпоинт POST /forms/{inn}

Параметры:
- inn - ИНН Организации. Строка 10 или 12 цифр.

Пример запроса:
- curl -X 'POST' \
  'http://localhost:8000/forms/505021556592' \
  -H 'accept: application/json'

Пример успешного ответа (200 OK):
- {
  "status": "success",
  "file_path": "505021556592.xlsx"
}
- 
Возможные ошибки:

- 404 Not Found — данных по указанному ИНН не найдено.

- 422 Unprocessable Entity — неверный формат ИНН.

- 409 Conflict — файл открыт в другой программе (Excel).

- 503 Service Unavailable — сайт Росстата недоступен или требует капчу.

## 🧪 Тестирование

1. **Запуск всех тестов (быстрые тесты с моками):**
   ```bash 
   poetry run pytest

2. **Запуск с отчетом о покрытии:**
   ```bash
   poetry run pytest --cov=src
   
## ⚠️ Примечание
Скрипт использует реальный браузер (Playwright) для обхода защиты сайта.
При частых запросах сайт Росстата может временно блокировать IP-адрес.
Используйте с уважением к ресурсам сайта.

