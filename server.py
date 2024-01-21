import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
import time
class Mail(BaseModel):
    message: str
    source: str | None = 'Unknown'
    timestamp: float | None = time.time()



app = FastAPI()

mailbox = []
# Using .append we can get mail into the 'mailbox'
# mail info: 
# message
# source
# timestamp
# 
@app.get("/")
async def root():
    return {'message':'Hello Mom!'}

@app.post("/postbox")
async def you_got_mail(mail: Mail):
    global mailbox
    #test_str = f"content: {mail.message}\nsource: {mail.source}\ntimestamp: {mail.timestamp}"
    mailbox.append(mail)
    return  #test_str

@app.get("/mailbox")
async def retrive_mail():
    global mailbox
    _ = mailbox.copy()
    mailbox.clear()
    return _

@app.post("/test")
async def test(test):
    return {'result':test['message']}
