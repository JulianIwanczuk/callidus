from configparser import ConfigParser
import psycopg2,re

def config(filename='database.ini',section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1}'.format(section,filename))


    return db

def connect():

    conn = None

    try: 

        params = config()

        # TRY CONNECT TO DATABASE
        conn = psycopg2.connect(**params)

        return conn

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally: 
        if conn is not None:
            #conn.close()
            print('# aqui puede cerrarse la conexión')


# BALIDA CORREO
def solve(s):
        pat = "^[a-zA-Z0-9-_.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if re.match(pat,s):
            return True
        else:
            return False

        
# FETCH OBJECT DATA
def fetchObjectData(cursor):
    data = {}

    rows = cursor.fetchone()
    cols = list(map(lambda x: x[0], cursor.description))
    
    for index,row in enumerate(rows):
        data[cols[index]] = row

    return data






