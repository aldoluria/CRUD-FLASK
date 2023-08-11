import os
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mysqldb import MySQL
#pip install Flask-MySQLdb
from flask_wtf.csrf import CSRFProtect
#pip install Flask-WTF
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
csrf=CSRFProtect()

# Conexión MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'tiard'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ruta=app.config['UPLOAD_FOLDER']='./app/static/img/uploads/alumnos'

db = MySQL(app)

app.secret_key='mysecretkey'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def Ver():
    cur=db.connection.cursor()
    sql="SELECT * FROM alumnos"
    cur.execute(sql)
    alumnos=cur.fetchall()
    print(alumnos) 
    cur.close()
    return render_template('ver.html', alumnos=alumnos)

@app.route("/Crear")
def Crear():
    return render_template('crear.html')

@app.route("/Insertar" , methods=['POST'])
def Insertar():
    if request.method == 'POST':
        Matricula=request.form['Matricula']
        Nombre=request.form['Nombre']
        Grupo=request.form['Grupo']
        Satus=1
        Creado=datetime.now()
        Activo=1
        file=request.files['Imagen']

        if file and allowed_file(file.filename):
            # Verificar si el archivo con el mismo nombre ya existe
            # Creamos un nombre dinamico para la foto de perfil con el nombre y el numero de empleado
            filename = "img" + Nombre + "_" + Matricula + "_" + secure_filename(file.filename)
            file_path = os.path.join(ruta, filename)
            if os.path.exists(file_path):
                flash('Advertencia: ¡Un archivo con el mismo nombre ya existe!')
            
            # Guardar el archivo y registrar en la base de datos
            file.save(file_path)
        else:
            flash('Error: ¡Extensión de archivo invalida!')

            return redirect(url_for('Ver'))

        cur=db.connection.cursor()
        sql="INSERT INTO alumnos (matricula, nombre, grupo, status, creado, activo, file_url) VALUES (%s, %s, %s,%s, %s, %s, %s)"
        valores=(Matricula.upper(), Nombre, Grupo, Satus, Creado, Activo, filename)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        flash('¡Usuario agregado exitosamente!')

        return redirect(url_for('Ver'))

@app.route("/Editar/<string:id>")
def Editar(id):
    cur=db.connection.cursor()
    sql="SELECT * FROM alumnos WHERE idalumnos={0}".format(id)
    cur.execute(sql)
    alumno=cur.fetchall()
    cur.close()
    return render_template('editar.html', alumno=alumno[0])

@app.route("/Actualizar/<string:id>", methods=['POST'])
def Actualizar(id):
    if request.method == 'POST':
        Matricula=request.form['Matricula']
        Nombre=request.form['Nombre']
        Grupo=request.form['Grupo']
        Imagen=request.form['Imagen']

        cur=db.connection.cursor()
        sql="UPDATE alumnos SET matricula=%s, nombre=%s, grupo=%s, file_url=%s WHERE idalumnos=%s" 
        valores=(Matricula.upper(), Nombre, Grupo, Imagen,id)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        flash('!Alumno editado exitosamente!')

        return redirect(url_for('Ver'))

@app.route("/Elimiar/<string:id>")
def Eliminar(id):
    print(id)
    cur=db.connection.cursor()
    sql="DELETE FROM alumnos WHERE idalumnos={0}".format(id)
    cur.execute(sql)
    db.connection.commit()
    cur.close()
    flash('¡Alumno  eliminado correctamente!')
    return redirect(url_for('Ver'))


if __name__ == '__main__':
    csrf.init_app(app)
    app.run(debug=True,port=8000)