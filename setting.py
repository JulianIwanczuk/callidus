from configparser import ConfigParser
import psycopg2,re

filename='database_remote.ini'
#filename='database_local.ini'

def config(filename,section='postgresql'):
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

        params = config(filename)

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
        pat = '[^@]+@[^@]+\.[^@]+'
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
        
# FETCH OBJECT DATA
def fetchObjectAllData(cursor):
    data = {}
    list_ = []

    rows = cursor.fetchall()
    cols = list(map(lambda x: x[0], cursor.description))
    
    for key,elm in enumerate(rows):
        for index,row in enumerate(elm):
            data[cols[index]] = row

        list_.append(dict(data))

    return list_






