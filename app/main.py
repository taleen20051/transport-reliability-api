from fastapi import FastAPI

app = FastAPI(title="Transport Reliability API")

@app.get("/")
def root():
    return {"message": "Transport Reliability API is running"}