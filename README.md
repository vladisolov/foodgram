# Описание проекта

Проект «Фудграм» — сайт, на котором зарегистрированные пользователи могут 
публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться 
на публикации других авторов.  
Зарегистрированным пользователям также доступен сервис «Список покупок». Он 
позволяет создавать список продуктов, которые нужно купить для приготовления 
выбранных блюд. Список покупок можно скачать в формате .pdf.  
[Ссылка на проект](https://foodgram.ddns.net/)

### Содержание

- [Запуск проекта в Docker контейнерах](#запуск-проекта-в-Docker-контейнерах)
- [Документация API](#документация-api)
- [Технологический стек](#технологический-стек)
- [Авторы](#авторы)

### Запуск проекта в Docker контейнерах:

Клонировать репозиторий и перейти в директорию infra/ в командной строке:

```
git clone git@github.com:vladisolov/foodgram.git
cd foodgram/infra/
```

Запустить контейнеры в фоновом режиме:

```
docker compose up -d
```

Выполнить миграции:

```
docker compose exec backend python manage.py migrate
```

Собрать статику backend и копировать ее на volume static:

```
docker compose exec backend python manage.py collectstatic
```

```
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```

Загрузить тестовые данные в БД из csv-файлов:

```
docker compose exec backend python manage.py load_data
```

При необходимости создать админа Django:

```
docker compose exec backend python manage.py createsuperuser
```

### Документация API

Полная спецификация и примеры запросов доступны по адресу:

- [ReDoc](https://foodgram.ddns.net/api/docs/)

### Технологический стек

- **Язык:** Python 3.12
- **Фреймворк:** Django 6.0
- **API:** djangorestframework 3.16.1
- **Аутентификация:** djoser 2.3.3
- **База данных:** postgres 14
- **Фильтрация:** django-filter 25.2
- **Переменные окружения:** python-dotenv 1.2.1
- **Документация API:** redoc 2.1.4
- **Обработка изображений:** pillow 12.0.0
- **Обработка PDF-файлов:** reportlab 4.4.6
- **Линтинг:** flake8 7.3.0, flake8-isort 7.0.0

### Авторы

Проект разработал: [Влад Соловьёв](https://github.com/vladisolov)
