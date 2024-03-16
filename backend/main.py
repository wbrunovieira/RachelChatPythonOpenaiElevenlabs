from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai



app = FastAPI()

origins = [ "http://localhost:5173", "http://localhost:5174/"]

app.add_middleware( CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

@app.get("/health")
async def check_health():
  return {"message": "healthy"}

