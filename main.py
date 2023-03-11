from fastapi import FastAPI,Response,Request,File,UploadFile
from bodyRequest import *
from models import Usuarios
from typing import Union

app = FastAPI()

@app.middleware('http')
def verifyEntrance(request: Request, next):
    response = next(request)
    return response


############################
#### RUTAS #################
@app.get('/')
def index(): 
    return { "msg": "Welcome to Api Pagos Usuario" }


# LOGIN DE USUARIOS
@app.post('/login')
def login(req: LoginBodyRequest): 
    isLogin = True
    isCaduced = False

    try:
        res = Usuarios.verifyLogin(req)
        td = Usuarios.verifyTokenDate(res)

        if res is None:
            isLogin = False

        if td['days'] == 0:
            isCaduced = True

        return {
            'msg': 'Login', 
            'isCaduced': isCaduced, 
            'daysCaduced': td['days'],
            'token': td['token'],
            'isLogin': isLogin
        }
    except: 
        return {
            'msg': 'Login fail', 
            'data': None 
        }
    

# REGISTRO DE DOCUMENTOS
@app.post('/document')
def saveDocuments(request: Request):

    data = Usuarios.getUserByToken(request.headers['api-token'])

    return data
    
    return {
        'file_size': file.size,
        'file_name': file.filename,
    }

