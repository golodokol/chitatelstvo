# Читательство — мобильное приложение (Expo)

React Native приложение для родителей и детей: вход по email + OTP, комната приключений, уроки в WebView.

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

1. **Вход** — email из формы записи  
2. **Код** — 6 цифр из письма  
3. **Выбор ребёнка** — если в семье несколько детей  
4. **Комната** — уровень, Словики, «Продолжить приключение», вкладка «Родителям»  
5. **Урок** — WebView на подписанную ссылку с сервера  

## Локальная разработка против prod

Поменять API в `mobile/app.json`:

```json
"extra": {
  "apiBaseUrl": "http://YOUR_IP:8000"
}
```

На Android-эмуляторе для localhost используйте `http://10.0.2.2:8000`.

## Сборка в Store (позже)

```bash
npm install -g eas-cli
eas build --platform all
```

Понадобятся иконка, splash и аккаунты Apple Developer / Google Play.

## Структура

```
mobile/
  app/           # expo-router экраны
  lib/           # API + auth (SecureStore)
  components/    # UI
  constants/     # тема
```
