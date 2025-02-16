
# Описание

Данный проект представляет собой реализацию API для работы с мессенджером. В рамках проекта были реализованы следующие методы:

- [x] - login - аутентификация пользователя
- [x] - sign_up - регистрация нового пользователя
- [ ] - read_messages - получение сообщений
- [ ] - send_message - отправка сообщения

Архитектура gRPC сервиса была максимально упрощена. Мы отказались от сложной архитектуры с очередями, синхронизирующими потоки, которые использовались для работы с сессиями в фоне. Вместо этого, было принято решение использовать полностью синхронное однопоточное устройство. Мы пришли к выводу, что нет особого смысла держать сессии открытыми между HTTP запросами от пользователя.

К сожалению, на текущий момент сервис работает нестабильно, и требуется дополнительная отладка для улучшения его производительности и надежности.

# Основные команды:
```
docker compose ubuild
docker compose up 
 ✔ Container test_task-mysql   Created                 0.0s # контейнер с БД для tinode
 ✔ Container test_task-tinode  Created                 0.0s # контейнер с tinode - доступен по адресу localhost:6060
 ✔ Container test_task-db      Created                 0.0s # контейнер с mongoDB для приложения
 ✔ Container test_task-web     Recreated               0.0s # контейнер с нашим приложнием - localhost:8004
```
Для локальной разработки:
```
make poetry-install # установка poetry
make poetry-shell # создание и вход в виртуальную оболочку poetry

```

В test_tinode_api.py прощупал api tinode - say_hi , регистрация, авторизация, создание топика -работает, публикация - не успел разведать.

## curl
curl -X POST http://localhost:8004/signup \
-H "Content-Type: application/json" \
-d '{ "email": "user@example.com", "password": "password123" }'
