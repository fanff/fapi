import json
from logging.config import fileConfig
import os
from typing import Annotated, Any, Dict, List, Union
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasicCredentials
import datetime
import logging
from pydantic import BaseModel
import time
import base64 
import urllib.parse
from fastapi.middleware.cors import CORSMiddleware
import whisper

import dotenv

dotenv.load_dotenv()


fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger()



origins = [
    "http://127.0.0.1:8060",
    "http://localhost:8060",
    "http://192.168.1.54",
]

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)



@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    )











def godo_decoder(body_bytes):

    #logger.info("request content: %s",body_bytes)
    body_str = body_bytes.decode("utf-8")

    body_str = urllib.parse.parse_qs(body_str)

    #logger.info("request content: %s",body_str)
    
    d = body_str["g"][0] #base64.b64decode(request.audio)
    
    content_was = base64.b64decode(d)
    #logger.info("content_was: %s",content_was)
    return content_was

# global variable to act as cache ? 
model_DB = {}
async def whisper_model_load():
    
    language=os.getenv("WHISPER_LANGUAGE","English")
    model_name=os.getenv("WHISPER_MODEL_NAME","tiny")
    device=os.getenv("WHISPER_DEVICE","cpu")

    if model_name in model_DB:
        logger.debug("model is cached %s",model_name)
        return model_DB[model_name]
    
    logger.info("Loading model %s",model_name)
    model = whisper.load_model(model_name,device=device)
    # decode the audio
    options = whisper.DecodingOptions(language=language,fp16 = False)

    model_DB[model_name] = (model,options)
    return (model ,options)

# Define the API endpoint for the home page
@app.get("/")
async def handle_home():
    return JSONResponse({
        "status":"ok",
        "whisper":whisper.available_models(),
        "current": list(model_DB.keys())
    })

@app.post("/test_decoding")
async def testing_decoding(request: Request):
    try:
        body_bytes = await request.body()
        content_was = godo_decoder(body_bytes)
        return JSONResponse({
            "content_was":str(content_was)
        })

    except Exception as e:

        logger.error(str(e))
        logger.exception("dfsq")
        return JSONResponse({
            "txt":str(e)
        })
    
@app.get("/sample")
async def sample(request: Request, mo: Annotated[dict, Depends(whisper_model_load)]):
    # Check if a valid username and password are provided in the request body
    start_dc = time.time()
    audio = whisper.load_audio("record.wav")
    model,options = mo
    # load audio and pad/trim it to fit 30 seconds
    loading_dur = time.time()-start_dc

    audio = whisper.pad_or_trim(audio)
    duration_audio_proc = time.time()-start_dc
    


    # make log-Mel spectrogram and move to the same device as the model
    start_dc = time.time()
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    spectro_proc_dur = time.time()-start_dc
    
    start_dc = time.time()
    result = whisper.decode(model, mel, options)
    end_dc = time.time()-start_dc

    return JSONResponse({
        "txt": result.text,
        "dur": end_dc,

        "audio_proc_dur":duration_audio_proc,
        "spectro_proc_dur":spectro_proc_dur,
        "loading_dur":loading_dur
    })

    
class AudioQuery(BaseModel):
    audio: str
    

@app.post("/txt")
async def txt(request: Request, mo: Annotated[dict, Depends(whisper_model_load)]):
    # Check if a valid username and password are provided in the request body


    try:
        
        start_dc = time.time()
        body_bytes = await request.body()

        

        with open("to_text.wav" ,'wb') as fou:
            fou.write(godo_decoder(body_bytes))

        model,options =  mo
        # load audio and pad/trim it to fit 30 seconds
        loading_dur = time.time()-start_dc


        start_dc = time.time()
        audio = whisper.load_audio("to_text.wav")
        audio = whisper.pad_or_trim(audio)
        duration_audio_proc = time.time()-start_dc
        # make log-Mel spectrogram and move to the same device as the model
        start_dc = time.time()
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        spectro_proc_dur = time.time()-start_dc

        start_dc = time.time()
        result = whisper.decode(model, mel, options)
        end_dc = time.time()-start_dc
        logger.info("got %s",result.text)
        return JSONResponse({
            "txt": result.text,
            "dur": end_dc,
            "audio_proc_dur":duration_audio_proc,
            "spectro_proc_dur":spectro_proc_dur,
            "loading_dur":loading_dur
        })
    except Exception as e:
        logger.exception("ldfqlf")
        return JSONResponse({
            "error":str(e)
        })

