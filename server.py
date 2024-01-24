import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Mail(BaseModel):
    content: str
    source: str | None = 'unknown'
    timestamp: float | None = time.time()
    type: str | None = 'unknown'

class Output(BaseModel):
    content: str
    source: str | None = 'Lucid'
    timestamp: float | None = time.time()
    
    
app = FastAPI()

mailbox = []
# Using .append we can get mail into the 'mailbox'
# mail info: 
# message
# source
# timestamp
# 
new_message = Output(content='')
@app.get("/")
async def root():
    return {'message':'Hello Mom!'}

@app.post("/postbox")
async def post_mail(mail: Mail):
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

@app.post("/output") # Needs a more creative name, and I'm not even sure if I should put it here
async def output(output: Output):
    global new_message
    #logging.INFO(f'Lucid: {output.content}')
    new_message=output
    return 

@app.get('/display')
async def display_output():
    global new_message
    _ = Output(content='')
    _, new_message = new_message, _
    return _
    