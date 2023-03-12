from fastapi import FastAPI,Response,Request,File,UploadFile,Form
from fastapi.responses import JSONResponse
from bodyRequest import *
from models import *
from typing import Union
import json

app = FastAPI()

routes = [
     '/'
    ,'/login'
]

# CAPA INTERMEDIA DE VALIDACION
@app.middleware('http')
async def verifyEntrance(request: Request, next):
    
    if request.url.path not in routes:
        apiKey = request.headers.get('api-key')

        if apiKey is None:
            return JSONResponse(content={'error': 'Api-key is required'},status_code=403)
        
        # OBTENGO LOS DATOS DE SESSION POR EL TOKEN
        ut = Usuarios.getUserByToken(apiKey)
        
        if type(ut) is not dict:
            return JSONResponse(content={'error': 'Is not a valid token'},status_code=200)

    response = await next(request)
    return response


############################
#### RUTAS #################
@app.get('/')
def index(): 
    return { "msg": "Welcome to Api CallIdUs" }


# LOGIN DE USUARIOS
@app.post('/login')
async def login(
     request: Request
) -> Response: 
    isLogin = True
    isCaduced = False

    if request.headers['Content-Type'] == 'application/json':
        item = await request.json()
    else:
        item = await request.form()

    item = LoginBodyRequest(** item)

    try:
        # VERIFICA LA DATA DEL USUARIO
        res = Usuarios.verifyLogin(item)
        # CIERRA POSIBLES SESIONES PREVIAS
        clo = Usuarios.closeSession(res)
        # GENERA UN TOKEN NUEVO
        to = Usuarios.generateToken(res)
        # CALCULA LA CADUCIDAD DE LA SESION
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
    

@app.get('/logout')
def logout(request:Request):

    token = request.headers['api-token']
    res = Usuarios.getUserFullDataByToken(token)
    clo = Usuarios.closeSession(res)

    if clo: 
        return {
            'logout': True,
            'msg': 'Session close!'
        }
    else:
        return {
            'logout': False,
            'msg': "Can't disable the session"
        }


# GENERAR REGISTRO DE USUARIO
@app.post('/signup')
async def signup(
     request:Request = None
) -> Response:
    
    if request.headers['Content-Type'] == 'application/json':
        item = await request.json()
    else:
        item = await request.form()

    item = UserBodyRequest(** item)
    
    res = Usuarios.signUp(item)

    if res:
        return {
            'active': True,
            'msg': 'Customer signup!'
        }
    else:
        return {
            'active': False,
            'msg': "Can't customer signup!"
        }


# GENERAR REGISTRO DE USUARIO
@app.post('/signup-company')
async def signupCompany(
     request:Request = None
) -> Response:
    
    if request.headers['Content-Type'] == 'application/json':
        item = await request.json()
    else:
        item = await request.form()

    item = UserBodyRequest(** item)
    
    res = Usuarios.signUpCompany(item)

    if res:
        return {
            'active': True,
            'msg': 'Company signup!'
        }
    else:
        return {
            'active': False,
            'msg': "Can't company signup!"
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


@app.get('/document/list')
async def documentList(request:Request) -> Response:

    token = request.headers['api-key']
    ut = Usuarios.getUserByToken(token)

    if type(ut) is not dict:
        return 'Token is not valid!'

    d = SessionBodyRequest(** ut)

    list_ = Documentos.getFilesList(d.user_id)

    return list_






