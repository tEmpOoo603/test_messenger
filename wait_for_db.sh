DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

echo "Ожидаем подключение к базе данных $DB_HOST:$DB_PORT..."
until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "База данных ещё не доступна, ждём..."
  sleep 1
done

echo "База данных доступна, выполняем миграции..."

# Запуск миграций
alembic upgrade head

echo "Миграции завершены, запускаем приложение..."
# Запуск приложения
uvicorn app.main:app --host 0.0.0.0 --port 8000
