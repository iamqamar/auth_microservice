from fastapi import FastAPI, status

from routes import auth, user

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)

@app.get("/", tags=["health"])
def health_check():
    return {
        "status": status.HTTP_200_OK,
        "server": "ok"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
