from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_mysqldb import MySQL, MySQLdb
from authlib.integrations.flask_client import OAuth
from os import getenv
from dotenv import load_dotenv
from training import ReinoAnimal
from datetime import datetime

import bcrypt
import pdfkit
import time
from fpdf import FPDF

app = Flask(__name__)
app.static_folder = 'static'
# BOT


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(ReinoAnimal.get_response(userText))
#########


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'veterinaria'
mysql = MySQL(app)


# llave secreta
app.secret_key = "applogin"

# semilla encriptacion
semilla = bcrypt.gensalt()

oauth = OAuth(app)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'

oauth.register(
    name='google',
    client_id=getenv("CLIENT_ID"),
    client_secret=getenv("SECRET_ID"),
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)
# registro con google##########################################


@app.route('/registrogoogle')
def registrogoogle():
    redirect_url = url_for("auth", _external=True)
    return oauth.google.authorize_redirect(redirect_url)


@app.route('/auth', methods=["GET", "POST"])
def auth():
    token = oauth.google.authorize_access_token()
    response = oauth.google.parse_id_token(token)
    jscompleto = response["name"]
    jsnombre = response["given_name"]
    jsapellido = "Sin apellido"
    try:
        jsapellido = response["family_name"]
        jsemail = response["email"]
    except:
        jsemail = response["email"]
    print(jscompleto)
    print(jsnombre)
    print(jsapellido)
    print(jsemail)
    # comprueba de que el usuario no este registrado
    if(request.method == "GET"):
        Usuario = jsemail  # se hara la verificacion unica con el correo del usuario y no el que esta aca como dato posiblemente cambiable a futuro
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT Email FROM usuario where Email =  (%s)', ([Usuario]))
        usu = cur.fetchone()
        cur.close()
    if(usu != None):
        print("El usuario ya existe")
    else:
        if(request.method == "GET"):
          # inserta datos
            Usuario = jsnombre
            Contraseña = "contraseña"
            contraseña_encode = Contraseña.encode("utf-8")
            contraseña_encriptado = bcrypt.hashpw(contraseña_encode, semilla)
            Apellidos = jsapellido
            Nombres = jsnombre
            Email = jsemail
            Sexo = "Sin datos"
            CI = "Sin datos"
            Celular = "Sin datos"
            Fecha_Nacimiento = ""
            Rol = "4"
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO usuario (Usuario,Contraseña,Apellidos,Nombres,Email,Sexo,CI,Celular,Fecha_Nacimiento,Rol_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (Usuario, contraseña_encriptado, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol))
            mysql.connection.commit()
            cur.close()

            Estado = "Activo"
            Foto = "Sin Foto"
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO cuenta (Estado_usuario, Foto_Perfil, Usuario_Id) VALUES (%s,%s, (SELECT Id_Usuario FROM usuario ORDER BY Id_Usuario  DESC LIMIT 0,1))',
                        (Estado, Foto))
            mysql.connection.commit()
            cur.close()
            session['usuario'] = Usuario
            session['nombres'] = Nombres
            session['email'] = Email
            return redirect(url_for('login'))
        ################################################################
    return redirect(url_for('registro'))

# login con google


@app.route('/logingoogle')
def logingoogle():
    redirect_url = url_for("auth2", _external=True)
    return oauth.google.authorize_redirect(redirect_url)


@app.route('/auth2', methods=["GET", "POST"])
def auth2():
    token = oauth.google.authorize_access_token()
    response = oauth.google.parse_id_token(token)
    jscompleto = response["name"]
    jsnombre = response["given_name"]
    jsapellido = "Sin apellido"
    try:
        jsapellido = response["family_name"]
        jsemail = response["email"]
    except:
        jsemail = response["email"]
    print(jscompleto)
    print(jsnombre)
    print(jsapellido)
    print(jsemail)

    if(request.method == "GET"):
        Usuario = jsemail  # se hara la verificacion unica con el correo del usuario y no el que esta aca como dato posiblemente cambiable a futuro

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT Usuario, Contraseña, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol_id, Id_usuario FROM usuario where Email =  (%s)', ([Usuario]))
        usu = cur.fetchone()
        cur.close()
    if(usu != None):
        print("usuario correcto correcta")
        session['usuario'] = usu[0]
        session['contraseña'] = usu[1]
        session['apellidos'] = usu[2]
        session['nombres'] = usu[3]
        session['email'] = usu[4]
        session['sexo'] = usu[5]
        session['ci'] = usu[6]
        session['celular'] = usu[7]
        session['fecha_nacimiento'] = usu[8]
        session['rol'] = usu[9]
        session['id'] = usu[10]        
        session['foto'] = usu[10]
    else:
        print("El usuario o la contraseña no es correcto")
        flash("El usuario o la contraseña no es correcto")
        print("El usuario o la contraseña no es correcto")
        return redirect(url_for("login"))
    return render_template("inicio.html")
############################################

# login

@app.route('/')
def host():
    return render_template("inicio_principal.html")

    

@app.route('/login')
def login():
    if 'usuario' in session:
        if(session['rol'] == 1):
            return redirect(url_for('home1'))
        if(session['rol'] == 2):
            return redirect(url_for('home2'))
        if(session['rol'] == 3):
            return redirect(url_for('home3'))
        if(session['rol'] == 4):
            return redirect(url_for('home'))
    else:
        return render_template("login.html")



@app.route('/cancelar/', methods=["GET", "POST"])
def cancelar():
    if 'usuario' in session:
        if(session['rol'] == 1):
            return redirect(url_for('home1'))
        if(session['rol'] == 2):
            return redirect(url_for('home2'))
        if(session['rol'] == 3):
            return redirect(url_for('home3'))
        if(session['rol'] == 4):
            return redirect(url_for('home'))
    else:
        return render_template("login.html")


@app.route('/cancelar2/', methods=["GET", "POST"])
def cancelar2():
    if 'usuario' in session:
        if(session['rol'] == 1):
            return redirect(url_for('home1'))
        if(session['rol'] == 2):
            return redirect(url_for('home2'))
        if(session['rol'] == 3):
            return redirect(url_for('home3'))
        if(session['rol'] == 4):
            return redirect(url_for('home'))
    else:
        return render_template("login.html")

# logout


@app.route("/salir")
def salir():
    session.clear()    
    flash("Usted ha cerrado sesion correctamente")
    return redirect(url_for('home'))


# login
@app.route('/login', methods=["GET", "POST"])
def ingresar():
    if(request.method == "GET"):
        if 'usuario' in session:
            return render_template("inicio.html")
        else:
            return render_template("login.html")
    else:
        Usuario = request.form['usuario']
        Contraseña = request.form['contraseña']
        contraseña_encode = Contraseña.encode("utf-8")
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT Usuario, Contraseña, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol_id, Id_usuario FROM usuario where usuario =  (%s)', ([Usuario]))
        usu = cur.fetchone()
        cur.close()
    if(usu != None):
        contraseña_encriptado_encode = usu[1].encode()
        print("Contraseña_encode: ", usu)
        print("Contraseña_encode: ", contraseña_encode)
        print("contraseña_encriptado_encode: ", contraseña_encriptado_encode)

        # verifica la contraseña
        if(bcrypt.checkpw(contraseña_encode, contraseña_encriptado_encode)):
            # registra la session
            session['usuario'] = usu[0]
            session['contraseña'] = usu[1]
            session['apellidos'] = usu[2]
            session['nombres'] = usu[3]
            session['email'] = usu[4]
            session['sexo'] = usu[5]
            session['ci'] = usu[6]
            session['celular'] = usu[7]
            session['fecha'] = usu[8]
            session['rol'] = usu[9]
            session['id'] = usu[10]       
            session['foto'] = usu[10]
            if(session['rol'] == 1):
                return redirect(url_for('home1'))
            if(session['rol'] == 2):
                return redirect(url_for('home2'))
            if(session['rol'] == 3):
                return redirect(url_for('home3'))
            if(session['rol'] == 4):
                return redirect(url_for('home'))
        else:
            print("El contraseña no es correcta")
            flash("El usuario o la contraseña no es correcto")
            
            return render_template("login.html")
    else:
        print("El usuario no existe")
        flash("El usuario o la contraseña no es correcto")
        return render_template("login.html")


@app.route('/inicio1')
def home1():
    if 'usuario' in session:        
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario')
        data = cur.fetchall()
        return render_template("inicio1.html", contacts = data)
    else:
        return render_template("login.html")

@app.route('/inicio2')
def home2():
    if 'usuario' in session:        
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE Rol_Id = 4')
        data = cur.fetchall()
        return render_template("inicio2.html", contacts = data)
    else:
        return render_template("login.html")

@app.route('/inicio2-2/<id>')
def home22(id):
    if 'usuario' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Mascota WHERE Usuario_Id = %s',([id]))
        data = cur.fetchall()
        return render_template('inicio2-2.html', contacts = data)
    else:
        return render_template("login.html")



@app.route('/inicio3')
def home3():
    if 'usuario' in session:        
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario')
        data = cur.fetchall()
        return render_template("inicio3.html", contacts = data)
    else:
        return render_template("login.html")

@app.route('/inicio')
def home():    
    if 'usuario' in session:
        return render_template("inicio.html")
    else:
        return render_template("inicio_principal.html")

#METODO REGISTRO 2
@app.route("/registro2/", methods=["GET", "POST"])
def registro2():
    if(request.method == "GET"):
        if 'usuario' in session:
            return render_template("inicio1.html")
        else:  # ACCESO NO CONSEDIDO
            return render_template("registro.html")
    else:  # inserta datos
        Usuario = request.form['usuario']
        Contraseña = request.form['contraseña']
        contraseña_encode = Contraseña.encode("utf-8")
        contraseña_encriptado = bcrypt.hashpw(contraseña_encode, semilla)
        Apellidos = request.form['apellidos']
        Nombres = request.form['nombres']
        Email = request.form['email']
        Sexo = request.form['sexo']
        CI = request.form['ci']
        Celular = request.form['celular']
        Fecha_Nacimiento = request.form['fecha_nacimiento']
        Rol = request.form['rol']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT Email FROM usuario where Email =  (%s)', ([Email]))
        usu = cur.fetchone()
        cur.close()
        if(usu != None):
            print("El usuario ya existe")            
            flash("El usuario ya existe con ese correo")
            return redirect(url_for('login'))
        else:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO usuario (Usuario,Contraseña,Apellidos,Nombres,Email,Sexo,CI,Celular,Fecha_Nacimiento,Rol_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (Usuario, contraseña_encriptado, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol))
            mysql.connection.commit()
            cur.close()
            Estado = "Activo"
            Foto = "Sin Foto"
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO cuenta (Estado_usuario, Foto_Perfil, Usuario_Id) VALUES (%s,%s, (SELECT Id_Usuario FROM usuario ORDER BY Id_Usuario  DESC LIMIT 0,1))',
                        (Estado, Foto))
            mysql.connection.commit()
            cur.close()

            cur = mysql.connection.cursor()
            cur.execute(
                'SELECT Usuario, Contraseña, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol_id, Id_usuario FROM usuario where usuario =  (%s)', ([Usuario]))
            usu = cur.fetchone()
            cur.close()
            session['usuario'] = usu[0]
            session['contraseña'] = usu[1]
            session['apellidos'] = usu[2]
            session['nombres'] = usu[3]
            session['email'] = usu[4]
            session['sexo'] = usu[5]
            session['ci'] = usu[6]
            session['celular'] = usu[7]
            session['fecha'] = usu[8]
            session['rol'] = usu[9]
            session['id'] = usu[10]
            flash("Se ha creado el usuario correctamente")
    return redirect(url_for('home1'))


# registrar
@app.route("/registro/", methods=["GET", "POST"])
def registro():
    if(request.method == "GET"):
        if 'usuario' in session:
            return render_template("inicio.html")
        else:  # ACCESO NO CONSEDIDO
            return render_template("registro.html")
    else:  # inserta datos
        Usuario = request.form['usuario']
        Contraseña = request.form['contraseña']
        contraseña_encode = Contraseña.encode("utf-8")
        contraseña_encriptado = bcrypt.hashpw(contraseña_encode, semilla)
        Apellidos = request.form['apellidos']
        Nombres = request.form['nombres']
        Email = request.form['email']
        Sexo = request.form['sexo']
        CI = request.form['ci']
        Celular = request.form['celular']
        Fecha_Nacimiento = request.form['fecha_nacimiento']
        Rol = "4"
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT Email FROM usuario where Email =  (%s)', ([Email]))
        usu = cur.fetchone()
        cur.close()
        if(usu != None):
            print("El usuario ya existe")            
            flash("El usuario ya existe con ese correo")
            return redirect(url_for('login'))
        else:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO usuario (Usuario,Contraseña,Apellidos,Nombres,Email,Sexo,CI,Celular,Fecha_Nacimiento,Rol_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (Usuario, contraseña_encriptado, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol))
            mysql.connection.commit()
            cur.close()
            Estado = "Activo"
            Foto = "Sin Foto"
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO cuenta (Estado_usuario, Foto_Perfil, Usuario_Id) VALUES (%s,%s, (SELECT Id_Usuario FROM usuario ORDER BY Id_Usuario  DESC LIMIT 0,1))',
                        (Estado, Foto))
            mysql.connection.commit()
            cur.close()

            cur = mysql.connection.cursor()
            cur.execute(
                'SELECT Usuario, Contraseña, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol_id, Id_usuario FROM usuario where usuario =  (%s)', ([Usuario]))
            usu = cur.fetchone()
            cur.close()
            session['usuario'] = usu[0]
            session['contraseña'] = usu[1]
            session['apellidos'] = usu[2]
            session['nombres'] = usu[3]
            session['email'] = usu[4]
            session['sexo'] = usu[5]
            session['ci'] = usu[6]
            session['celular'] = usu[7]
            session['fecha'] = usu[8]
            session['rol'] = usu[9]
            session['id'] = usu[10]
            flash("Se ha creado el usuario correctamente")
    return redirect(url_for('login'))

# Guardar o Editar


@app.route("/subir/", methods=["GET", "POST"])
def editar():
    if(request.method == "GET"):
        if 'usuario' in session:
            return render_template("inicio.html")
        else:  # ACCESO NO CONSEDIDO
            return render_template("registro.html")
    else:  # rescatar datos
        id = 0
        id = session['id']
        Usuario = request.form['usuario']
        Contraseña = request.form['contraseña_confirmada']
        if(Contraseña != ""):
            contraseña_encode = Contraseña.encode("utf-8")
            contraseña_encriptado = bcrypt.hashpw(contraseña_encode, semilla)
            Apellidos = request.form['apellidos']
            Nombres = request.form['nombres']
            Email = request.form['email']
            print(request.form['sexo1'])#####no se puede aun cambiar le sexo se sigue cambiando
            Sexo = request.form['sexo1']
            if(Sexo == "none"):
                print("Sexo == none")
                Ci = request.form['ci']
                Celular = request.form['celular']
                Fecha_Nacimiento = request.form['fecha_nacimiento']
                cur = mysql.connection.cursor()
                cur.execute('UPDATE usuario SET Usuario = %s, Contraseña = %s, Apellidos = %s, Nombres = %s, Email = %s, CI = %s, Celular = %s, Fecha_Nacimiento = %s WHERE Id_Usuario = %s',
                            (Usuario, contraseña_encriptado, Apellidos, Nombres, Email, Ci, Celular, Fecha_Nacimiento, id))
                mysql.connection.commit()
                cur.close()        
                session['usuario'] = Usuario
                session['apellidos'] = Apellidos
                session['nombres'] = Nombres
                session['email'] = Email
                session['ci'] = Ci
                session['celular'] = Celular
                session['fecha'] = Fecha_Nacimiento
                session['id'] = id
            
                # session['correo'] = correo
                flash("Cambios guardados exitosamente")
                return redirect(url_for('informacion'))
            if(Sexo != "none" and Sexo != session['sexo']):                
                print("Sexo == none and session = sexo1")
                Ci = request.form['ci']
                Celular = request.form['celular']
                Fecha_Nacimiento = request.form['fecha_nacimiento']
                cur = mysql.connection.cursor()
                cur.execute('UPDATE usuario SET Usuario = %s, Contraseña = %s, Apellidos = %s, Nombres = %s, Email = %s, Sexo = %s, CI = %s, Celular = %s, Fecha_Nacimiento = %s WHERE Id_Usuario = %s',
                            (Usuario, contraseña_encriptado, Apellidos, Nombres, Email, Sexo, Ci, Celular, Fecha_Nacimiento, id))
                mysql.connection.commit()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute(
                    'SELECT Usuario, Contraseña, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol_id, Id_usuario FROM usuario where usuario =  (%s)', ([Usuario]))
                usu = cur.fetchone()
                cur.close()
                session['usuario'] = usu[0]
                session['contraseña'] = usu[1]
                session['apellidos'] = usu[2]
                session['nombres'] = usu[3]
                session['email'] = usu[4]
                session['sexo'] = usu[5]
                session['ci'] = usu[6]
                session['celular'] = usu[7]
                session['fecha'] = usu[8]
                session['rol'] = usu[9]
                session['id'] = usu[10]
            
                # session['correo'] = correo
                flash("Cambios guardados exitosamente")
                return redirect(url_for('informacion'))
            else:      
                print("Sexo == none and session = sexo1 DIO ELSE")
                Ci = request.form['ci']
                Celular = request.form['celular']
                Fecha_Nacimiento = request.form['fecha_nacimiento']
                cur = mysql.connection.cursor()
                cur.execute('UPDATE usuario SET Usuario = %s, Contraseña = %s, Apellidos = %s, Nombres = %s, Email = %s, Sexo = %s, CI = %s, Celular = %s, Fecha_Nacimiento = %s WHERE Id_Usuario = %s',
                            (Usuario, contraseña_encriptado, Apellidos, Nombres, Email, Sexo, Ci, Celular, Fecha_Nacimiento, id))
                mysql.connection.commit()
                cur.close()        
                session['usuario'] = Usuario
                session['apellidos'] = Apellidos
                session['nombres'] = Nombres
                session['email'] = Email
                session['sexo'] = Sexo
                session['ci'] = Ci
                session['celular'] = Celular
                session['fecha'] = Fecha_Nacimiento
                session['id'] = id
            
                # session['correo'] = correo
                flash("Cambios guardados exitosamente")
                return redirect(url_for('informacion'))
        else:
            print("ELSE SIN NADA EN CONTRASEÑA NUEVA")
            Apellidos = request.form['apellidos']
            Nombres = request.form['nombres']
            Email = request.form['email']
            Sexo = request.form['sexo1']
            if(Sexo == "none"):
                print("Sexo == none SIN CONTRASEÑA")
                Ci = request.form['ci']
                Celular = request.form['celular']
                Fecha_Nacimiento = request.form['fecha_nacimiento']
                cur = mysql.connection.cursor()
                cur.execute('UPDATE usuario SET Usuario = %s, Apellidos = %s, Nombres = %s, Email = %s, CI = %s, Celular = %s, Fecha_Nacimiento = %s WHERE Id_Usuario = %s',
                            (Usuario, Apellidos, Nombres, Email, Ci, Celular, Fecha_Nacimiento, id))
                mysql.connection.commit()
                cur.close()        
                session['usuario'] = Usuario
                session['apellidos'] = Apellidos
                session['nombres'] = Nombres
                session['email'] = Email
                session['ci'] = Ci
                session['celular'] = Celular
                session['fecha'] = Fecha_Nacimiento
                session['id'] = id
            
                # session['correo'] = correo
                flash("Cambios guardados exitosamente")
                return redirect(url_for('informacion'))
            if(Sexo != "none" and Sexo != session['sexo']):
                print("Sexo == none and session = sexo1 SIN CONTRASEÑA")
                Ci = request.form['ci']
                Celular = request.form['celular']
                Fecha_Nacimiento = request.form['fecha_nacimiento']
                cur = mysql.connection.cursor()
                cur.execute('UPDATE usuario SET Usuario = %s, Apellidos = %s, Nombres = %s, Email = %s, Sexo = %s, CI = %s, Celular = %s, Fecha_Nacimiento = %s WHERE Id_Usuario = %s',
                            (Usuario, Apellidos, Nombres, Email, Sexo, Ci, Celular, Fecha_Nacimiento, id))
                mysql.connection.commit()
                cur.close()
                cur = mysql.connection.cursor()
                cur.execute(
                    'SELECT Usuario, Contraseña, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol_id, Id_usuario FROM usuario where usuario =  (%s)', ([Usuario]))
                usu = cur.fetchone()
                cur.close()
                session['usuario'] = usu[0]
                session['contraseña'] = usu[1]
                session['apellidos'] = usu[2]
                session['nombres'] = usu[3]
                session['email'] = usu[4]
                session['sexo'] = usu[5]
                session['ci'] = usu[6]
                session['celular'] = usu[7]
                session['fecha'] = usu[8]
                session['rol'] = usu[9]
                session['id'] = usu[10]

                # session['correo'] = correo
                flash("Cambios guardados exitosamente")
                return redirect(url_for('informacion'))
            else:      
                print("Sexo == none and session = sexo1 DIO ELSE SIN CONTRASEÑA")
                Ci = request.form['ci']
                Celular = request.form['celular']
                Fecha_Nacimiento = request.form['fecha_nacimiento']
                cur = mysql.connection.cursor()
                cur.execute('UPDATE usuario SET Usuario = %s, Apellidos = %s, Nombres = %s, Email = %s, Sexo = %s, CI = %s, Celular = %s, Fecha_Nacimiento = %s WHERE Id_Usuario = %s',
                            (Usuario, Apellidos, Nombres, Email, Sexo, Ci, Celular, Fecha_Nacimiento, id))
                mysql.connection.commit()
                cur.close()        
                session['usuario'] = Usuario
                session['apellidos'] = Apellidos
                session['nombres'] = Nombres
                session['email'] = Email
                session['sexo'] = Sexo
                session['ci'] = Ci
                session['celular'] = Celular
                session['fecha'] = Fecha_Nacimiento
                session['id'] = id
            
                # session['correo'] = correo
                flash("Cambios guardados exitosamente")
                return redirect(url_for('informacion'))

###########################
            

#METODO DE SERVICIOS
@app.route('/servicios/')
def servicios():   

    if 'usuario' in session:
        return render_template('servicios.html')
    else:
        return render_template("servicios_out.html")
    

#METODO DE CONSULTAS ONLINE
@app.route('/consultas_online/', methods=["GET", "POST"])
def consultas_online():

    if 'usuario' in session:  
        return render_template('consultas_online.html')
    else:
        return render_template("consultas_online_out.html")
    

#METODO DE CONSULTAS ONLINE 2
@app.route('/consultas_online2/', methods=["GET", "POST"])
def consultas_online2():
    if 'usuario' in session:  
        return render_template('consultas_online2.html')
    else:
        return render_template("login.html")


#METODO DE CONTACTOS
@app.route('/contactos/')
def contactos():

    if 'usuario' in session:
        return render_template('contactos.html')
    else:
        return render_template("contactos_out.html")
    

#METODO PERFIL 
@app.route('/perfil/')
def perfil():
    if 'usuario' in session:
        return render_template('perfil.html')
    else:
        return render_template("login.html")

#METODO PERFIL INFORMACION
@app.route('/perfil/informacion/')
def informacion():
    if 'usuario' in session:
        Usuario = session['usuario']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT Usuario, Contraseña, Apellidos, Nombres, Email, Sexo, CI, Celular, Fecha_Nacimiento, Rol_id, Id_usuario FROM usuario where usuario =  (%s)', ([Usuario]))
        usu = cur.fetchone()
        cur.close()
        id = usu[10]
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE Id_Usuario = %s', ([id]))
        data = cur.fetchall()
        print(id)
        print(data)
        return render_template('perfilInformacion.html', consultastabla=data[0])
    else:
        return redirect(url_for('login'))

#METODO PERFIL MASCOTA
@app.route('/perfil/mascotas/')
def mascotas():
    if 'usuario' in session:
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM MASCOTA WHERE Usuario_Id = %s',([id]))
        data = cur.fetchall()
        return render_template('perfilMascotas.html', contacts = data)
    else:
        return render_template("login.html")

#METODO PERSONAL
@app.route('/inicio1')
def home11():
    if 'usuario' in session:
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE Id_Usuario = %s',([id]))
        data = cur.fetchall()
        return render_template('inicio1.html', contacts = data)
    else:
        return render_template("login.html")





#METODO AGREGAR NUEVA MASCOTA
@app.route('/agregar_mascota', methods=['POST'])
def agregar_mascota():
   if request.method == 'POST':
        Nombre = request.form['nombre_mascota']        
        Edad = request.form['edad_mascota']        
        Color_Pelo = request.form['color_pelo_mascota']
        Raza = request.form['raza_mascota']
        Genero = request.form['genero_mascota']
        Usuario_Id = session['id']
        cur = mysql.connection.cursor()        
        cur.execute('INSERT INTO MASCOTA (Nombre, Edad, Color_Pelo, Raza, Genero, Usuario_Id) VALUES (%s, %s, %s, %s, %s, %s)', (Nombre, Edad, Color_Pelo, Raza, Genero, Usuario_Id))
        mysql.connection.commit()
        flash('Mascota agregado correctamente')
        return redirect(url_for("mascotas"))

#METODO EDITAS MASCOTA
@app.route('/Editar/<id>')
def get_contact(id):
        cur = mysql.connection.cursor() 
        cur.execute('SELECT * FROM MASCOTA WHERE Id_Mascota = %s', [(id)])
        data = cur.fetchall()
        return render_template('editar-mascota.html', contact = data[0])

@app.route('/Editar2/<id>')
def get_contact2(id):
        cur = mysql.connection.cursor() 
        cur.execute('SELECT * FROM Usuario WHERE Id_Usuario = %s', [(id)])
        data = cur.fetchall()
        return render_template('editar-mascota2.html', contact = data[0])

#METODO REGISTRO CLINICO
@app.route('/registroclinico/<id>')
def get_contact3(id):    
    try:
        cur = mysql.connection.cursor() 
        cur.execute('SELECT * FROM mascota m, usuario u, registro_clinico r WHERE m.Id_Mascota = %s and u.Id_Usuario = (SELECT Usuario_Id FROM mascota WHERE Id_Mascota = %s) and r.Usuario_Id = (SELECT Usuario_Id FROM mascota WHERE Id_Mascota = %s) and r.Mascota_Id = (SELECT Id_mascota FROM mascota WHERE Id_Mascota = %s);', [(id),(id),(id),(id)])
        data = cur.fetchall()
        print(data)
        return render_template('registroClinico.html', contact = data[0])
    except Exception as e:        
        flash('Registro Clínico no Existente')
        print(e)  
        return redirect(url_for('home2'))


#METODO ACTUALIZAR MASCOTA
@app.route('/update/<id>', methods=['POST'])
def update_contact(id):
   if request.method == 'POST':
        Nombre = request.form['nombre_mascota']        
        Edad = request.form['edad_mascota']        
        Color_Pelo = request.form['color_pelo_mascota']
        Raza = request.form['raza_mascota']
        Genero = request.form['genero_mascota'] 
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE MASCOTA
            SET Nombre = %s,Edad = %s, Color_Pelo = %s, Raza = %s, Genero = %s WHERE Id_Mascota = %s
        """, (Nombre, Edad, Color_Pelo, Raza, Genero, id))
        mysql.connection.commit ()
        flash('Mascota Actualizado')
        return redirect(url_for('mascotas'))

@app.route('/update2/<id>', methods=['POST'])
def update_contact2(id):
   if request.method == 'POST':
        Usuario = request.form['usuario']        
        Apellidos = request.form['apellidos']        
        Nombres = request.form['nombres']
        Email = request.form['email']
        Sexo = request.form['sexo'] 
        Ci = request.form['ci'] 
        Celular = request.form['celular'] 
        fecha = request.form['fecha'] 
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE usuario
            SET Usuario = %s,Apellidos = %s, Nombres = %s, Email = %s, Sexo = %s, Ci = %s, Celular = %s, Fecha_Nacimiento = %s WHERE Id_Usuario = %s
        """, (Usuario, Apellidos, Nombres, Email, Sexo, Ci, Celular, fecha, id))
        mysql.connection.commit ()
        flash('Personal Actualizado')
        return redirect(url_for('home1'))

@app.route('/update3/<id>', methods=['POST'])
def update_contact3(id):
    try:
        if request.method == 'POST':
                Signos = request.form['signos']        
                Temperatura1 = request.form['temperatura1']        
                Temperatura2 = request.form['temperatura2']
                Temperatura3 = request.form['temperatura3']
                Temperatura4 = request.form['temperatura4'] 
                Temperatura5 = request.form['temperatura5'] 
                Diagnostico = request.form['diagnostico'] 
                Tratamiento = request.form['tratamiento']
                DuracionTratamiento = request.form['tratamiento_duracion']
                Farmaco1 = request.form['farmaco1']
                Fecha_farmaco1 = request.form['fecha_farmaco1'] 
                Farmaco2 = request.form['farmaco2']
                Fecha_farmaco2 = request.form['fecha_farmaco2'] 
                Farmaco3 = request.form['farmaco3']
                Fecha_farmaco3 = request.form['fecha_farmaco3'] 
                Farmaco4 = request.form['farmaco4']
                Fecha_farmaco4 = request.form['fecha_farmaco4'] 
                Farmaco5 = request.form['farmaco5']
                Fecha_farmaco5 = request.form['fecha_farmaco5'] 
                cur = mysql.connection.cursor()
                cur.execute("""
                    UPDATE REGISTRO_CLINICO
                    SET Signos_Clinicos = %s,Dia_1_Temperatura = %s, Dia_2_Temperatura = %s, Dia_3_Temperatura = %s, Dia_4_Temperatura = %s, Dia_5_Temperatura = %s, Diagnostico = %s, Tratamiento = %s, Duracion_del_Tratamiento = %s, Dia_1_Tratamiento_Farmaco = %s, Dia_1_Tratamiento_Fecha = %s, Dia_2_Tratamiento_Farmaco = %s, Dia_2_Tratamiento_Fecha = %s, Dia_3_Tratamiento_Farmaco = %s, Dia_3_Tratamiento_Fecha = %s, Dia_4_Tratamiento_Farmaco = %s, Dia_4_Tratamiento_Fecha = %s, Dia_5_Tratamiento_Farmaco = %s, Dia_5_Tratamiento_Fecha = %s WHERE Mascota_Id = %s
                """, (Signos, Temperatura1, Temperatura2, Temperatura3, Temperatura4, Temperatura5, Diagnostico, Tratamiento, DuracionTratamiento, Farmaco1, Fecha_farmaco1, Farmaco2, Fecha_farmaco2, Farmaco3, Fecha_farmaco3, Farmaco4, Fecha_farmaco4, Farmaco5, Fecha_farmaco5, id))
                mysql.connection.commit ()
                flash('Registro CLínico Actualizado')
                return redirect(url_for('home2'))
    except Exception as e:        
        flash('Registro Clínico no Actualizado')
        print(e)  
        return redirect(url_for('home2'))


#BORRAR MASCOTAS
@app.route('/Borrar/<string:id>')
def delete_contact(id):    
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM MASCOTA WHERE Id_Mascota = {0}'.format (id))
        mysql.connection.commit()
        flash("Mascota Borrado Satisfactoriamente")
        return redirect(url_for('mascotas'))
    except Exception as e:        
        flash('Esta mascota ya cuenta con un "Historial Clinico" y no puede ser eliminada')
        print(e)
        return redirect(url_for('mascotas'))
@app.route('/Borrar2/<string:id>')
def delete_contact2(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM cuenta WHERE Usuario_Id = {0}'.format (id))
        mysql.connection.commit()
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM Usuario WHERE Id_Usuario = {0}'.format (id))
        mysql.connection.commit()
        flash("Personal Borrado Satisfactoriamente")
        return redirect(url_for('home1'))
    except Exception as e:        
        flash('Usted no puede eliminar un Cliente')
        print(e)  
        return redirect(url_for('home1'))

#CONSULTAS DE MASCOTAS
@app.route('/perfil/consultas/')
def consultas():
    if 'usuario' in session:
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM MASCOTA m, REGISTRO_CLINICO r, USUARIO u WHERE m.Id_Mascota = r.Mascota_Id and r.Usuario_Id = m.Usuario_Id and u.Id_Usuario = %s and r.Usuario_Id = %s',([id],[id]))
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('perfilConsultas.html', consultas = data)
    else:
        return render_template("login.html")


@app.route('/perfil/informacion/<id>')
def obtener_id(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuario WHERE Id_Usuario = %s', (id))
    data = cur.fetchall()
    return render_template('perfilInformacion.html', consultastabla=data[0])
##################################################################################

#CONSULTAS A SQL
@app.route("/ajaxpost",methods=["POST","GET"])
def ajaxpost():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
    if request.method == 'POST':
        queryString = request.form['queryString']
        print(queryString)        
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM MASCOTA WHERE Nombre LIKE '{}%' and Usuario_Id = {}".format(queryString,(id)))
        countries = cur.fetchall()
        print(id)        
        print(cur)
        print(countries)
    return jsonify({'htmlresponse': render_template('response.html', countries=countries)})

@app.route('/pdf',methods=["POST","GET"])    
def download_report():
    try:
        Nombre = request.form['nombre_mascota']        
        enfermedad = request.form['enfermedad_mascota']
        if(enfermedad == "Parvovirus"):
            signosClinicos = "diarrea, vomito, fiebre, perdida de peso"
        if(enfermedad == "Moquillo"):
            signosClinicos = "fiebre, falta de apetito, bajada de peso, sin ganas de hacer nada, secrecion nasal acuosa, vomitos, diarrea,deshidratacion, dificultad de respirar"
        if(enfermedad == "Hepatitis Virica"):
            signosClinicos = "fiebre, letargo, diarrea, dolor abdominal, moretones en la piel, puntos rojos en la piel"
        if(enfermedad == "Parainfluenza"):
            signosClinicos = "tos, fiebre, alta temperatura, estornudos, depresion, perdida de apetito"
        if(enfermedad == "Rabia"):
            signosClinicos = "fiebre, vomitos, agitacion, desorientacion, hiperactividad, salivacion excesiva, insomnio"
        id = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM MASCOTA WHERE Usuario_Id = %s and Nombre = %s',([id],Nombre))
        data = cur.fetchone()
        idmascota = data[0]
        edad = data[2]
        color = data[3]
        raza = data[4]
        genero = data[5]
        dia = ""
        #usuario
        Usuario_Id = session['id']
        cur = mysql.connection.cursor()        
        cur.execute('INSERT INTO REGISTRO_CLINICO(Signos_Clinicos, Diagnostico, Dia_1_Tratamiento_Fecha, Usuario_Id, Mascota_Id) VALUES (%s, %s, %s, %s, %s)', (signosClinicos, enfermedad, dia, Usuario_Id, idmascota))
        mysql.connection.commit()

        print("llego aca")
        pdf = FPDF()
        pdf.add_page()
         
        page_width = pdf.w - 2 * pdf.l_margin
        
        pdf.image('./static/recursos/logo verde con letras oscuras.png',180,5,20,25,'png')
        pdf.ln(5)
        pdf.set_font('Arial','B',16.0) 
        pdf.cell(page_width, 0.0, 'Resultado de la Consulta Online', align='C')
        pdf.ln(15)

        pdf.cell(page_width, 0.0, 'Datos del Paciente: ', align='C')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Nombre: ' + Nombre, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)
        
        pdf.cell(page_width, 0.0, 'Edad: ' + edad, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Color de pelaje: ' + color, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)        

        pdf.cell(page_width, 0.0, 'Raza: ' + raza, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)   

        pdf.cell(page_width, 0.0, 'Genero: ' + genero, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Enfermedad que aparenta: ' + enfermedad, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(15)
       
        Usuario = session['usuario']
        Apellidos = session['apellidos']
        Nombres = session['nombres']
        Email = session['email']
        Sexo = session['sexo']
        Ci = session['ci']
        Celular = session['celular']
        
        pdf.set_font('Arial','B',16.0) 
        pdf.cell(page_width, 0.0, 'Datos del Cliente: ', align='C')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Usuario: ' + Usuario, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)        

        pdf.cell(page_width, 0.0, 'Apellidos: ' + Apellidos, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Nombres: ' + Nombres, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Email: ' + Email, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Sexo: ' + Sexo, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Cedula de Identidad: ' + Ci, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(10)

        pdf.cell(page_width, 0.0, 'Celular: ' + Celular, align='L')
        pdf.set_font('Arial', '', 12)
        pdf.ln(15)


        pdf.set_font('Times','',10.0) 
        pdf.cell(page_width, 0.0, '------ Fin del Resultado ------', align='C')

        pdf.ln(5)
        pdf.set_font('Times','',10.0) 
        pdf.cell(page_width, 0.0, '(Este reporte no es un testimonio de un Medico Veterinario, pero si es un reporte de un Sistema Experto', align='C')
        pdf.ln(5)
        pdf.set_font('Times','',10.0) 
        pdf.cell(page_width, 0.0, 'supervisado por un Medico Veterinario)', align='C')

        flash('Guardado Finalizado')
        return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=ConsultaChatbot.pdf'})
    except Exception as e:
        print(e)
        
@app.route('/perfil/informacion/cambiarfoto',methods=["POST","GET"])    
def cambiarfoto():          
    id = session['id']
    portada = request.files["foto"]
    portada.save("./static/fotosperfil/" + str(id) + ".jpg" )    
    flash("Cambio actualizado satisfactoriamente")        
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuario WHERE Id_Usuario = %s', ([id]))
    data = cur.fetchall()
    print(id)
    print(data)
    cur = mysql.connection.cursor()
    cur.execute('UPDATE cuenta SET Foto_Perfil = %s WHERE Usuario_Id = %s',(id, id))
    mysql.connection.commit()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute('SELECT Foto_Perfil FROM cuenta WHERE Usuario_Id = %s', ([id]))
    data = cur.fetchall()
    session['foto'] = id
    return render_template('perfilInformacion.html', consultastabla=data[0])

@app.route('/reportes/', methods=["GET", "POST"])
def reportes():
    if 'usuario' in session:  
        return render_template('reportes.html')
    else:
        return render_template("login.html")

#CONSULTAS DE REPORTES 
@app.route('/reportes/1/')
def reportes1():
    if 'usuario' in session:
        id = 4
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Usuario WHERE Rol_Id = %s',([id]))
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('reportes1.html', contacts = data)
    else:
        return render_template("login.html")

@app.route('/reportes/2/')
def reportes2():
    if 'usuario' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM MASCOTA m, USUARIO u where m.Usuario_Id = u.Id_Usuario')
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('reportes2.html', contacts = data)
    else:
        return render_template("login.html")

@app.route('/reportes/3/')
def reportes3():
    if 'usuario' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT u.Usuario, u.CI, m.Nombre ,m.Raza, m.Genero, r.Diagnostico, r.Signos_Clinicos, r.Dia_1_Tratamiento_Farmaco, r.Dia_1_Tratamiento_Fecha FROM MASCOTA m, REGISTRO_CLINICO r, USUARIO u where r.Usuario_Id = u.Id_Usuario and r.Mascota_Id = m.Id_Mascota' )
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('reportes3.html', contacts = data)
    else:
        return render_template("login.html")

@app.route('/reportes/4/')
def reportes4():
    if 'usuario' in session:
        id = 4
        cur = mysql.connection.cursor()
        cur.execute('SELECT u.Usuario, u.CI, m.Nombre ,m.Raza, m.Genero, r.Diagnostico, r.Signos_Clinicos, r.Dia_1_Tratamiento_Farmaco, r.Dia_1_Tratamiento_Fecha FROM MASCOTA m, REGISTRO_CLINICO r, USUARIO u where r.Usuario_Id = u.Id_Usuario and r.Mascota_Id = m.Id_Mascota and r.Diagnostico = "Parvovirus";')
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('reportes4.html', contacts = data)
    else:
        return render_template("login.html")

@app.route('/reportes/5/')
def reportes5():
    if 'usuario' in session:
        id = 4
        cur = mysql.connection.cursor()
        cur.execute('SELECT u.Usuario, u.CI, m.Nombre ,m.Raza, m.Genero, r.Diagnostico, r.Signos_Clinicos, r.Dia_1_Tratamiento_Farmaco, r.Dia_1_Tratamiento_Fecha FROM MASCOTA m, REGISTRO_CLINICO r, USUARIO u where r.Usuario_Id = u.Id_Usuario and r.Mascota_Id = m.Id_Mascota and r.Diagnostico = "Moquillo";')
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('reportes5.html', contacts = data)
    else:
        return render_template("login.html")

@app.route('/reportes/6/')
def reportes6():
    if 'usuario' in session:
        id = 4
        cur = mysql.connection.cursor()
        cur.execute('SELECT u.Usuario, u.CI, m.Nombre ,m.Raza, m.Genero, r.Diagnostico, r.Signos_Clinicos, r.Dia_1_Tratamiento_Farmaco, r.Dia_1_Tratamiento_Fecha FROM MASCOTA m, REGISTRO_CLINICO r, USUARIO u where r.Usuario_Id = u.Id_Usuario and r.Mascota_Id = m.Id_Mascota and r.Diagnostico = "Hepatitis Virica";')
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('reportes6.html', contacts = data)
    else:
        return render_template("login.html")

@app.route('/reportes/7/')
def reportes7():
    if 'usuario' in session:
        id = 4
        cur = mysql.connection.cursor()
        cur.execute('SELECT u.Usuario, u.CI, m.Nombre ,m.Raza, m.Genero, r.Diagnostico, r.Signos_Clinicos, r.Dia_1_Tratamiento_Farmaco, r.Dia_1_Tratamiento_Fecha FROM MASCOTA m, REGISTRO_CLINICO r, USUARIO u where r.Usuario_Id = u.Id_Usuario and r.Mascota_Id = m.Id_Mascota and r.Diagnostico = "Parainfluenza";')
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('reportes7.html', contacts = data)
    else:
        return render_template("login.html")

@app.route('/reportes/8/')
def reportes8():
    if 'usuario' in session:
        id = 4
        cur = mysql.connection.cursor()
        cur.execute('SELECT u.Usuario, u.CI, m.Nombre ,m.Raza, m.Genero, r.Diagnostico, r.Signos_Clinicos, r.Dia_1_Tratamiento_Farmaco, r.Dia_1_Tratamiento_Fecha FROM MASCOTA m, REGISTRO_CLINICO r, USUARIO u where r.Usuario_Id = u.Id_Usuario and r.Mascota_Id = m.Id_Mascota and r.Diagnostico = "Rabia";')
        data = cur.fetchall()
        print(data)
        cur.close()
        return render_template('reportes8.html', contacts = data)
    else:
        return render_template("login.html")

if __name__ == '__main__':
    load_dotenv()
    app.run(host='0.0.0.0', debug=True)


###############################################################################
