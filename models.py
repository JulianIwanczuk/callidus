import psycopg2,datetime,calendar,time
from setting import *
from dateutil.relativedelta import *

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

            

    @classmethod
    def verifyTokenDate(self,data):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM session_log where user_id = %s AND status = 1"
            cursor.execute(sql,[data['id']])
            rs = fetchObjectData(cursor)

            # OBTENGO LAS AMORTIZACIONES PAGAS
            amoTrue = self.getAmortizations(data,True)
            # OBTENGO LAS AMORTIZACIONES NO PAGAS
            amoFalse = self.getAmortizations(data,False)
            # CALCULO LA FECHA DEL PROXIMO PAGO
            dateTrue = amoFalse[0]['payment_date']
            dp = dateTrue.day
            mp = dateTrue.month
            yp = dateTrue.year
            deltaP = datetime.date(yp,mp,dp) # OBTENGO EL FORMATO INDICADO PARA COMPARAR
            dateToday = datetime.date.today()
            fec =  deltaP - dateToday
            days = fec.days - 1

            if days < 0:
                days = 30

            # ASIGNO LOS DIAS DE CADUCIDAD
            self.assigningDayCaduced(days, data['id'])

            return {
                'days': days,
                'token': rs['token']
            }
        except(Exception,psycopg2.DatabaseError) as error:
            print(error)
            return False
        finally: 
            cursor.close()
            conn.close()



    def assigningDayCaduced(days,userId):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "UPDATE usuarios set days_caduced = %s where id = %s"
            cursor.execute(sql,[days,userId])

            return True
        except:
            conn.rollback()
            return False
        finally: 
            conn.commit()
            cursor.close()
            conn.close()

    def generateToken(data):

        try:
            conn = connect()
            cursor = conn.cursor()
            token = data['email']+str(datetime.datetime.now())

            sql = "INSERT INTO session_log (user_id,token) VALUES (%s,MD5(%s))"
            cursor.execute(sql,[data['id'],token])

            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.commit()
            cursor.close()
            conn.close()


    def closeSession(data):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "UPDATE session_log SET status = %s WHERE user_id = %s"
            cursor.execute(sql,[0,data['id']])

            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.commit()
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


    def getUserFullDataByToken(token):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT u.*,sl.token FROM session_log AS sl "
            sql += "INNER JOIN usuarios AS u ON sl.user_id = u.id "
            sql += "WHERE sl.token = %s AND sl.status = 1" 

            cursor.execute(sql,[token])
            data = fetchObjectData(cursor)

            return data
        except(Exception, psycopg2.DatabaseError) as error:
            return "Can't get user data"
        finally:
            cursor.close()
            conn.close()


    @classmethod
    def signUp(self,data):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM usuarios WHERE username = %s OR email = %s"
            cursor.execute(sql,[data.username,data.email])

            rows = cursor.fetchall()

            if len(rows) > 0:
                return False
        

            sql = "INSERT INTO usuarios (username,password,fullname,email,is_active,category) VALUES (%s,MD5(%s),%s,%s,%s,%s)"
            cursor.execute(sql,[
                 data.username
                ,data.password
                ,data.fullname
                ,data.email
                ,data.is_active
                ,data.category
            ])

            return True
        except(Exception,psycopg2.DatabaseError) as error:
            conn.rollback()
            return False
        finally:
            conn.commit()
            cursor.close()
            conn.close()

    # CREA LA AMORTIZACION
    def createAmortizations(data):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM amortizaciones WHERE user_id = %s"
            cursor.execute(sql,[data['id']])

            rows = cursor.fetchall()

            if(len(rows) == 0):
                months = [1,2,3,4,5,6,7,8,9,10,11,12]
                sql = "INSERT INTO amortizaciones (user_id,quota,payment_date) values (%s,%s,%s)"

                for index,month in enumerate(months):
                    date = datetime.datetime.now() + relativedelta(months=index)
                    cursor.execute(sql,[data['id'],month,date])
                

            return True
        except:
            conn.rollback()
            return False
        finally: 
            conn.commit()
            cursor.close()
            conn.close()


    # OBTENGO LAS AMORTIZACIONES
    def getAmortizations(data,bool=None):
        
        conn = connect()
        cursor = conn.cursor()

        if bool is None:
            sql = "SELECT * FROM amortizaciones WHERE user_id = %s ORDER BY quota"
        elif bool != False:
            sql = "SELECT * FROM amortizaciones WHERE user_id = %s AND paid = true ORDER BY quota"
        else:
            sql = "SELECT * FROM amortizaciones WHERE user_id = %s AND paid = false ORDER BY quota"

        cursor.execute(sql,[data['id']])

        data = fetchObjectAllData(cursor)

        return data


    def setPayAmortizations(amo_id,user_id):
        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "UPDATE amortizaciones SET paid = true WHERE user_id = %s AND id = %s"
            cursor.execute(sql,[user_id,amo_id])

            return True
        except:
            conn.rollback()
            return False
        finally: 
            conn.commit()
            cursor.close()
            conn.close()


    @classmethod
    def getuserByEmail(self,email):
        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM usuarios WHERE email = %s AND status = 1"
            cursor.execute(sql,[email])

            data = fetchObjectData(cursor)

            return data
        except:
            return {}



    @classmethod
    def signUpCompany(self,data):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM usuarios WHERE username = %s OR email = %s"
            cursor.execute(sql,[data.username,data.email])

            rows = cursor.fetchall()

            if len(rows) > 0:
                return False

            sql = "INSERT INTO usuarios (username,password,fullname,email,is_active,category,business_name,business_code) VALUES (%s,MD5(%s),%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,[
                 data.username
                ,data.password
                ,data.fullname
                ,data.email
                ,data.is_active
                ,data.category
                ,data.business_name
                ,data.business_code
            ])

            return True
        except(Exception,psycopg2.DatabaseError) as error:
            conn.rollback()
            return False
        finally:
            conn.commit()
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

    
    def getFilesList(id):

        try:
            conn = connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM documentos WHERE user_id = %s"
            cursor.execute(sql,[id])

            data = fetchObjectAllData(cursor)

            return data
        except:
            return None




