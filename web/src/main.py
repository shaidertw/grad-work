from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
#from fastapi.templating import Jinja2Templates

from src.router import router as routerDefault
from src.user.router import router as routerUser
from src.db import create_table, engine
from src.pages.router import router as routerPages

app = FastAPI(
    title="Users API"
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.include_router(routerDefault)
app.include_router(routerUser)
app.include_router(routerPages)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    """ Создание таблицы """
    create_table(engine)
