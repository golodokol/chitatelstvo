# Читательство — мобильное приложение (Expo)

React Native приложение для родителей и детей: вход по email + OTP, комната приключений, уроки в WebView.

**Полный план и статус:** [`docs/MOBILE_APP.md`](../docs/MOBILE_APP.md)

## Требования

- Node.js 20+
- [Expo Go](https://expo.dev/go) на телефоне **или** Android Studio / Xcode для эмулятора

## Запуск

```bash
cd mobile
npm install
npx expo start
```

Отсканируйте QR-код в Expo Go (Android) или Camera (iOS).

API по умолчанию: `https://api.chitatelstvo.ru` (см. `app.json` → `extra.apiBaseUrl`).

## Экраны

1. **Вход** — email из формы записи на сайте
2. **Код** — 6 цифр из письма
3. **Выбор ребёнка** — если в семье несколько детей
4. **Комната** — уровень, Словики, треки курсов (в т.ч. «Буквы оживают» / «Первые истории»), сундук, «Продолжить приключение», вкладка «Родителям»
5. **Урок** — WebView на подписанную ссылку с сервера (сказки и квесты)

## Поддерживаемые курсы

Приложение показывает всё, что есть у ребёнка в enrollment:

- 1–4 класс, внеклассное 6–8 / 9–11 — формат «сказка» (видео + квизы)
- **Буквы оживают**, **Первые истории** — интерактивные квесты (станции, искорки, сундук)
- Смешанный кабинет — несколько треков на одном экране

Запись и оплата — только на [chitatelstvo.ru](https://chitatelstvo.ru).

## Локальная разработка против prod

Поменять API в `mobile/app.json`:

```json
"extra": {
  "apiBaseUrl": "http://YOUR_IP:8000"
}
```

На Android-эмуляторе для localhost используйте `http://10.0.2.2:8000`.

## API (кратко)

| Метод | Путь |
|-------|------|
| POST | `/api/v1/auth/otp/request` |
| POST | `/api/v1/auth/otp/verify` |
| GET | `/api/v1/cabinet?child_id=…` |
| GET | `/api/v1/lessons/{slug}?child_id=…` |
| POST | `/api/v1/chest/claim` |

Подробнее: `docs/WEBHOOK_AND_NOTIFICATIONS.md`.

## Сборка в Store (следующий шаг)

```bash
npm install -g eas-cli
cd mobile
eas login
eas init          # один раз — привязка проекта Expo
eas build --profile preview --platform android   # APK для проверки
eas build --profile production --platform all    # перед Store
```

Иконка и splash уже в `mobile/assets/` (Словик). Пересобрать:

```bash
python scripts/generate_mobile_assets.py
```

### Smoke-тест API (prod)

```bash
# Публичные проверки (health, auth 401, OTP)
python scripts/smoke_mobile_app.py

# Полный прогон: кабинет + урок + сундук
# Сначала получите JWT: scripts/test_auth_otp.py
set AUTH_TEST_TOKEN=eyJ...
set AUTH_TEST_CHILD_ID=uuid-ребёнка
python scripts/smoke_mobile_app.py
```

Понадобятся аккаунты Apple Developer / Google Play. См. чеклист в `docs/MOBILE_APP.md`.

## Структура

```
mobile/
  app/           # expo-router экраны
  lib/           # API + auth (SecureStore)
  components/    # UI (LevelPath, BadgeGrid, …)
  constants/     # тема, тексты родительской вкладки
```
