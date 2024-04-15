
from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
import uvicorn
import logging
import sys
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.INFO)

# logger.setLevel(logging.DEBUG)
# stream_handler = logging.StreamHandler(sys.stdout)
# log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
# stream_handler.setFormatter(log_formatter)
# logger.addHandler(stream_handler)
app = FastAPI(title='Lucid_server')
# logger.info('API is starting up')
class Mail(BaseModel):
    content: str
    source: str | None = 'unknown'
    timestamp: float | None = time.time()
    type: str | None = 'unknown'

class Output(BaseModel):
    content: str
    source: str | None = 'Lucid'
    timestamp: float | None = time.time()
    
class Summary(BaseModel):
    content: str
    
class DiscordMessage(BaseModel):
    message: str


mailbox = []
# Using .append we can get mail into the 'mailbox'
# mail info: 
# message
# source
# timestamp
# 
new_discord_message = DiscordMessage(message='')
new_summary = Summary(content='No summary available.')
@app.get("/")
async def root():
    return {'message':'Hello Mom!'}

@app.post("/postbox")
async def post_mail(mail: Mail):
    global mailbox
    uvicorn_logger.info(f"Got message from {mail.source}: {mail.content}")
    #test_str = f"content: {mail.message}\nsource: {mail.source}\ntimestamp: {mail.timestamp}"
    mailbox.append(mail)
    return  #test_str

@app.get("/mailbox")
async def retrive_mail():
    global mailbox
    _ = mailbox.copy()
    mailbox = []
    return _


@app.post("/test")
async def test(test):
    return {'result':test['message']}

"""@app.post("/output") # Needs a more creative name, and I'm not even sure if I should put it here
async def output(output: Output):
    global new_message
    # logger.info(f'Lucid: {output.content}')
    new_message=output
    return 
"""
@app.post('/discord/send_message')
async def send_message_to_discord(message:DiscordMessage):
    global new_discord_message
    uvicorn_logger.info(f"Got message from server: {message}")
    new_discord_message = message.message
    return
    
@app.get('/discord/fetch_newest_message')
async def get_ai_response():
    global new_discord_message
    return new_discord_message

@app.post('/discord/post_summary')
async def summary_from_server(summary: Summary):
    global new_summary
    # logger.info(f'Discord: {summary.content}')
    new_summary = summary
    return
@app.get('/discord/get_summary')
async def get_summary():
    global new_summary
    return new_summary
