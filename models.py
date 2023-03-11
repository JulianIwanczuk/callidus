import psycopg2,datetime,calendar
from setting import *

class Usuarios: 

    def __init__(self) -> None:
        pass

    @classmethod
    def verifyLogin(self,req):

        try: 
            conn = connect()
            cursor = conn.cursor()
            col = None
            co = solve(req.username)
            data = {}

            # VALIDA SI ES USUARIO O EMAIL
            if co != False:
                col = "email"
            else:
                col = "username"
                
            sql = 'SELECT * FROM usuarios WHERE ' + col + ' = %s AND password = MD5(%s) AND status = 1'
            cursor.execute(sql,[req.username, req.password])
            data = fetchObjectData(cursor)

            return data
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            return "can't get user data from db <----"
        finally: 
            cursor.close()
            conn.close()


    def verifyTokenDate(data):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM session_log where user_id = %s AND status = 1"
            cursor.execute(sql,[data['id']])
            data = fetchObjectData(cursor)

            date = datetime.datetime.now()
            range = calendar.monthrange(date.year,date.month)
            lastdate = datetime.datetime(date.year,date.month,range[1])
            fec = lastdate - data['date_create']

            return {
                'days': fec.days,
                'token': data['token']
            }
        except:
            return False
        finally: 
            cursor.close()
            conn.close()


    def getUserByToken(token):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM session_log WHERE token = %s AND status = 1"
            cursor.execute(sql,[token])
            data = fetchObjectData(cursor)

            return data
        except(Exception, psycopg2.DatabaseError) as error:
            return error
        finally:
            cursor.close()
            conn.close()





########################
### CLASE MODELO DOCUMENTOS
class Documentos:

    def insertData(data):

        try: 
            conn = connect()
            cursor = conn.cursor()

            sql = "INSERT INTO documentos (user_id,name,size) values (%s,%s,%s)"
            cursor.execute(sql,[data['user'],data['name'],data['size']])

            sql = "SELECT * FROM documentos WHERE user_id = %s"
            cursor.execute(sql,[data['user']])

            result = fetchObjectAllData(cursor)

            return result
        except(Exception,psycopg2.DatabaseError) as error:
            conn.rollback()
            return "Sorry, can't insert into documentos"
        finally: 
            conn.commit()
            cursor.close()
            conn.close()





