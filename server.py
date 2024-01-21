import uvicorn
from fastapi import FastAPI

app = FastAPI()
#port = 8001

@app.get("/")
async def root():
    return {"message": "Hello World"}


#if __name__ == "__main__":
#    uvicorn.run(app, port=port)