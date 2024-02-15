## Описание
Учебный проект шаблонизатор документов.

### О проекте
Проект, представляет собой инструмент, который позволяет автоматизировать процесс
генерации документов в формате docx или pdf на основе предварительно подготовленных шаблонов.

## Основная логика
Пользователь может выбрать шаблон (из имеющихся в базе), выполнить заполнение полей, после чего на сервере осуществляется генерация готового документа в формате docx или pdf и сгенерированного документа пользователю.
В шаблонах имеются возможности дополнительных обработок вводимых пользователем данных (склонение по падежам, приведение в нужную форму числительных и др.). Для авторизованных пользователей предусмотрена возможность добавления шаблонов в избранное и хранения истории подготовленных документов и черновиков (не полностью заполненных документов).

Неавторизованный пользователь имеет возможность:
  - получить список всех доступных шаблонов базы /api/v1/template/
  - скачать черновик документа в формате docx /api/v1/template/{id}/download_draft/
  - скачать черновик документа в формате pdf /api/v1/template/{id}/download_draft/?pdf=true
  - сгенерировать и скачать превью документа в формате docx /api/v1/template/{id}/download_preview/
  - сгенерировать и скачать превью документа в формате pdf /api/v1/template/{id}/download_preview/?pdf=true
  
Авторизованный пользователь имеет возможность:
  - добавить/удалить шаблон в/из избранное /api/v1/template/favorite
  - формировать/редактировать документы на основании выбранного шаблона и пользовательски данных и сохранять документы на сервере /api/v1/document/{id}/
  - скачивать сохраненные документы в формате docx /api/document/{id}/download/
  - доступ к документам и данным отдельных документов имеет только автор документа

Администратор имеет возможность (в дополнение к авторизованному пользователю):
  - загрузить информацию о новом шаблоне (наименование, описание полей), удалить шаблон /api/v1/template/
  - обновить docx файл шаблона /api/v1/template/{id}/upload_template/
  - сгенерировать миниатюру шаблона /api/v1/template/{id}/generate_thumbnail/

В дополнение к api разработаны эскизы html страниц для взаимодействия с api:
  - просмотр шаблонов /view/template/
  - просмотр документов /view/document/
  - работа с шаблоном /view/template/{id}
  - работа с документом /view/document/{id}

### Технологии
- **Python - 3.10**
- **FastAPI**
- **SQLAlchemy - 2.0**
- **Pydantic - 2.5**
- **PostgreSQL - 13.10**
- **Redis**
- **Celery**
- **jinja**
- **Docker**
- **nginx**

## Подготовка и запуск проекта:

Клонируйте репозиторий:

```bash
    git clone  git@github.com:ASTimch/documents-templates-fastapi.git
```

## Сборка и запуск docker-контейнеров проекта:

### Сформировать файл настроек окружения:
Файл .env-prod подготовить в соответствии с шаблоном .env-prod.example

### Сборка и запуск оркестра контейнеров:
```
    docker compose up --build
```

### Просмотр документации по api:
```
    localhost/api/v1/docs
    localhost/api/v1/redoc
```

## Инициализация базы начальными данными:

#### Регистрация нового пользователя:
POST запрос по адресу /api/v1/auth/register

#### Задать типы полей:
POST запрос по адресу /api/v1/template_field_type/list
Пример тела запроса в файле /data/field_types.json

#### Загрузить описание полей шаблона:
POST запрос по адресу /api/v1/template/
Пример тела запроса в файле /data/otpusk_tpl.json

#### Загрузить файл шаблона:
PATCH запрос по адресу /api/v1/template/{id}/upload_template
с содержимым файлом /data/otpusk_tpl.docx

#### Доступ к визуальному интерфейсу:

    localhost:9000/view/



## Разворачивание проекта без использования docker-образов:

### Создать виртуальное окружение:
```
    python -m venv venv
```
#### активировать виртуальное окружение, Если у вас Linux/macOS
```
    source venv/bin/activate
```
#### Активировать виртуальное окружение, Если у вас windows
```
    source venv/scripts/activate
```

### Установить зависимости из файла requirements.txt:
```
    cd backend
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```
### Сформировать файл настроек окружения:
Файл .env подготовить в соответствии с шаблоном .env.example

### Выполнить миграции:
```
    alembic upgrade head
```

### Запустить проект:
```
    uvicorn app.main:app --reload
```

### Просмотр документации по api:
```
    localhost:8000/api/v1/docs
    localhost:8000/api/v1/redoc
```
