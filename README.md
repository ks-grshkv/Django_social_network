## Social Network project / Учебный проект - социальная сеть

[EN] A social network similar to LiveJournal. Here you can:
- share your latest news and thoughts,
- add images to your posts,
- follow your friends,
- follow a certain category of posts (e.g. "Jokes" or "Quotes from great thinkers"),
- create new posts categories,
- comment other users' posts,
- edit your posts,
- signup/login/logout.

[RU] Проект социальной сети, похожей на LiveJournal.
Что в ней можно делать:
- делиться своими новостями и мыслями,
- добавлять изображения к своим сообщениям,
- подписываться на другого пользователя,
- подписываться на категорию постов (например, «Шутки» или «Цитаты великих мыслителей»),
- создавать новые категории постов,
- комментировать сообщения других пользователей,
- редактировать свои сообщения,
- создать профиль/войти в профиль/выйти из профиля.


### Launching project / Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/ks-grshkv/api_yamdb.git
```

```
cd yatube_api
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```