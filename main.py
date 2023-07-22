from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.home import router as home_router
from app.routes.routes import router as validate_router
import uvicorn


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home_router)
app.include_router(validate_router)


if __name__=="__main__":
    uvicorn.run("main:app", host = '0.0.0.0', port = 10000,reload=True)