from fastapi import FastAPI,Response,Request,File,UploadFile,Form
from fastapi.responses import JSONResponse
from bodyRequest import *
from models import *
from typing import Union
import json
import psycopg2
from fastapi.middleware.cors import CORSMiddleware
from setting import *


routes = [
     '/'
    ,'/login'
    ,'/logout'
    ,'/signup'
    ,'/signup-company'
    ,'/db-test'
    ,'/get-days-remaining'
]

app = FastAPI()

# Agrega las URLs permitidas en la lista 'allow_origins'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    return JSONResponse(content={ "msg": "Welcome to Api CallIdUs" })

@app.get('/db-test')
async def dbTest(request: Request):
    try:
        conn = connect()

        return { "msg": "connection grand!"}
    except(Exception, psycopg2.DatabaseError) as error:
        return { "msg": "connection failed [:(]"}



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
            'action': isLogin,
            'msg': 'Login', 
            'isCaduced': isCaduced, 
            'daysCaduced': res['days_caduced'],
            'token': td['token'],
        }
    except: 
        return {
            'action': False,
            'msg': 'Login fail', 
            'data': None,
        }
    

@app.post('/logout')
async def logout(request:Request) -> Response:

    token = request.headers['api-key']

    res = Usuarios.getUserByToken(token)
    clo = Usuarios.closeSession(res)

    if clo: 
        return {
            'action': True,
            'msg': 'Session close!'
        }
    else:
        return {
            'action': False,
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
            'action': True,
            'msg': 'Customer signup!'
        }
    else:
        return {
            'action': False,
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
            'action': True,
            'msg': 'Company signup!'
        }
    else:
        return {
            'action': False,
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


@app.get('/get-days-remaining')
async def getDaysRemaining(request: Request) -> Response:

    token = request.headers['api-key']

    try:
        # VERIFICA LA DATA DEL USUARIO
        res = Usuarios.getUserFullDataByToken(token)

        return { "days_caduced": res["days_caduced"] }
    except:
        return False



