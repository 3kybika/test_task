
# Используем базовый образ для Tinode
FROM tinode/tinode:latest

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем конфигурацию
COPY tinode.conf /etc/tinode.conf

# Устанавливаем переменные окружения
ENV TINODE_DB_TYPE=mysql
ENV TINODE_DB_HOST=mysql
ENV TINODE_DB_PORT=3306
ENV TINODE_DB_USER=root
ENV TINODE_DB_PASSWORD=your_password
ENV TINODE_DB_NAME=your_database

# Открываем порт для Tinode
EXPOSE 6060

# Запускаем Tinode
CMD ["tinode", "-config", "/etc/tinode.conf"]
