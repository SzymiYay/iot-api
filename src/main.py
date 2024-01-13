from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from dotenv import load_dotenv

from src.auth import router as auth_router
from src.users import router as user_router
from src.measurements import router as measurement_router
from src import docs

import uvicorn
import os


load_dotenv(".env")

app = FastAPI(
    title="Temperature API",
    description=docs.get_description(),
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": ""
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    }

)

db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_name = os.environ["DB_NAME"]
db_username = os.environ["DB_USERNAME"]
db_password = os.environ["DB_PASSWORD"]
ssl_mode = os.environ["DB_SSL_MODE"]
DATABASE_URL = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode={ssl_mode}"

app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)

app.include_router(auth_router.router, tags=["Auth"])
app.include_router(user_router.router, tags=["Users"])
app.include_router(measurement_router.router, tags=["Measurements"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)