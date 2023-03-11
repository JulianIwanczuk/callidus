from fastapi import FastAPI,Response,Request,File,UploadFile,Form
from bodyRequest import *
from models import *
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
async def saveDocuments(request: Request, file: Union[UploadFile,None] = File(...)):
    token = request.headers['api-token']
    data = Usuarios.getUserByToken(token)

    # SAVE INTO DOCUMENTS TABLE
    res = Documentos.insertData({
        'user': data['id'],
        'size': file.size,
        'name': file.filename,
    })
    
    return res

