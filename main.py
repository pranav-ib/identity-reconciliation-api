from fastapi import FastAPI
from models import IdentifyRequest
from services import identify_contact

app= FastAPI()

@app.get("/")
def home():
    return {"message" : "Bitespeed is working!"}


@app.post("/identify")
def identify(req : IdentifyRequest):

    if not req.email and not req.phoneNumber:
        return {"error": "At least one of email or phone number must be provided."}
    
    return identify_contact(req.email, req.phoneNumber)