from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import auth, blog_content, password_reset, users

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(password_reset.router)
app.include_router(blog_content.router)


@app.get("/")
async def main():
    return {"detail": "Welcome to FastAPI Home page"}
