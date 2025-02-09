# Что успел...
Да вообще-то немного.
Я увяз в дебаге grpc_service - впервые писал использование стримингового grpc клиента
signin работает нестабильно, я не усспеваю понять причину почему

# Основные команды:
```

docker compose up 
 ✔ Container test_task-mysql   Created                 0.0s # контейнер с БД для tinode
 ✔ Container test_task-tinode  Created                 0.0s # контейнер с tinode - доступен по адресу localhost:6060
 ✔ Container test_task-db      Created                 0.0s # контейнер с mongoDB для приложения
 ✔ Container test_task-web     Recreated               0.0s # контейнер с нашим приложнием - localhost:8004

make poetry-install # установка poetry
make poetry-shell # создание и вход в виртуальную оболочку poetry

```

# ToDo - просто исследования 
Для grpc можно было скомпилить из исходных прото файлов pb:
```
wget https://raw.githubusercontent.com/tinode/chat/refs/heads/master/pbx/model.proto -O pbx/model.proto

python -m grpc_tools.protoc -I../pbx --python_out=. --pyi_out=. --grpc_python_out=. ../../pbx/model.proto
```
или исползовать либу:
```
poetry add  tinode_grpc
``

В test_tinode_api.py прощупал api tinode - asy_hi , регистрация, авторизация, создание топика -работает, публикация - не успел разведать.

## curl
curl -X POST http://localhost:8004/signup \
-H "Content-Type: application/json" \
-d '{ "email": "user@example.com", "password": "password123" }'