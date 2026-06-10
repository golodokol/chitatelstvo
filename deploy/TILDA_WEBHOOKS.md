# Webhook Tilda для chitatelstvo.ru

## Регистрация

| Параметр | Значение |
|----------|----------|
| URL | `https://api.chitatelstvo.ru/webhook/register` |
| Метод | POST |
| Заголовок | `X-Webhook-Secret: ваш_WEBHOOK_SECRET` |

## Ручная отметка (только творчество / встреча)

| Параметр | Значение |
|----------|----------|
| URL | `https://api.chitatelstvo.ru/webhook/event` |
| event_type | `creative_task` или `live_meeting` |

Видео и квизы — **только через плеер**, не через Tilda.

## Ссылки для родителей

| Страница | Откуда |
|----------|--------|
| Сайт | `https://chitatelstvo.ru` |
| Прогресс | приходит после регистрации (`progress_url`) |
| Урок | кнопка сказки на странице прогресса |
