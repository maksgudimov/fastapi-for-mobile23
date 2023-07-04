from os import environ
from fastapi import FastAPI
import databases

# берем параметры БД из переменных окружения
DB_USER = environ.get("DB_USER", "test")
DB_PASSWORD = environ.get("DB_PASSWORD", "pass")
DB_HOST = environ.get("DB_HOST", "45.12.238.138")
DB_NAME = "test"
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)
# создаем объект database, который будет использоваться для выполнения запросов
database = databases.Database(SQLALCHEMY_DATABASE_URL)


app = FastAPI()


@app.on_event("startup")
async def startup():
    # когда приложение запускается устанавливаем соединение с БД
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    # когда приложение останавливается разрываем соединение с БД
    await database.disconnect()


@app.get("/")
async def read_root():
    # изменим роут таким образом, чтобы он брал данные из БД
    query = (
        select(
            [
                posts_table.c.id,
                posts_table.c.created_at,
                posts_table.c.title,
                posts_table.c.content,
                posts_table.c.user_id,
                users_table.c.name.label("user_name"),
            ]
        )
        .select_from(posts_table.join(users_table))
        .order_by(desc(posts_table.c.created_at))
    )
    return await database.fetch_all(query)


