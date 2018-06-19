import datetime
from flask import Flask,render_template,session,request, jsonify, Response
from sqlalchemy import or_, and_
from model import entities
from database import connector
import json

app = Flask(__name__)
app.secret_key = "secret key"
db = connector.Manager()

cache = {}
engine = db.createEngine()


@app.route('/')
def hello_world():
    return render_template('Portada.html')

@app.route('/signin')
def signin():
    return render_template('Sign.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dologin',  methods = ['POST'])
def do_login():
    data = request.form
    sessiondb = db.getSession(engine)
    users = sessiondb.query(entities.Profesor)
    for user in users:
        if user.email == data['email'] and user.password == data['password']:
            session['logged'] = user.id;
            return render_template('index.html', user=user)

    return render_template('login.html')
@app.route('/crear', methods=['POST'])
def crearuser():
    data=request.form
    session = db.getSession(engine)
    profesor=entities.Profesor(email=data['email'],fullname=data['fullname'], password=data['password'])
    session.add(profesor)
    session.commit()
    return render_template('login.html')

@app.route('/current', methods = ['GET'])
def current():
    sessiondb = db.getSession(engine)
    user = sessiondb.query(entities.Profesor).filter(entities.Profesor.id == session['logged']).first()
    js = json.dumps(user, cls=connector.AlchemyEncoder)
    return Response(js, status=200, mimetype='application/json')

@app.route('/Datos/<id>')
def datos(id):
    session = db.getSession(engine)
    profesor=session.query(entities.Profesor).filter(entities.Profesor.id == id).first()
    print(profesor.id)
    return render_template("Alumno.html",profesor=profesor)


@app.route('/users', methods = ['GET'])
def get_users():
    key = 'getUsers'
    if key not in cache.keys():
        sessiondb = db.getSession(engine)
        dbResponse = sessiondb.query(entities.Profesor)
        cache[key] = dbResponse;
        print("From DB")
    else:
        print("From Cache")

    users = cache[key];
    response = []
    for user in users:
        response.append(user)
    return json.dumps(response, cls=connector.AlchemyEncoder)

@app.route('/enc1/<id>')
def enc1(id):
    session = db.getSession(engine)
    profesor = session.query(entities.Profesor).filter_by(id = id).first()
    return render_template("Encuesta1.html", user=profesor)

@app.route('/enc2/<id>')
def enc2(id):
    session = db.getSession(engine)
    profesor = session.query(entities.Profesor).filter(id = id).first()
    return render_template("Encuesta2.html", user=profesor)

@app.route('/setUsers')
def set_user():
    user1 = entities.Profesor(email='ed', fullname='Edward Elric', password='bye123')
    user2 = entities.Profesor(email='jb', fullname='Juan Bellido', password='bye123')
    session = db.getSession(engine)
    session.add(user1)
    session.add(user2)
    session.commit()
    return 'Created users'

@app.route('/resultado1/<id>', methods=['POST'])
def resultado1(id):
    data = request.form.to_dict()
    check = request.form.getlist('check')
    nombre=data['nombre']
    edad=data['edad']
    sum=0
    for dato in check:
        sum=sum+float(dato)
    return render_template("Encuesta2.html",nombre=nombre,edad=edad,sum=sum,id=id)

@app.route('/resultado2/<nombre>/<edad>/<sum>/<id>', methods=['POST'])
def resultado2(nombre,edad,sum,id):
    check = request.form.getlist('check')
    sum2=0
    for dato in check:
        sum2 = sum2+float(dato)
    porcentaje1=(float(sum)/15)*100
    porcentaje2=(float(sum2)/12)*100
    estado=""
    if (porcentaje1<75 and porcentaje2<55) or (porcentaje1<55 and porcentaje2<55):
        estado="Critico"
    elif (porcentaje1<=100 and porcentaje2<55) or (porcentaje1<55 and porcentaje2<=100) or (porcentaje1<55 and porcentaje2<75):
        estado="Observacion"
    else:
        estado="Normal"
    session = db.getSession(engine)
    alumno = entities.Alumno(name=nombre,edad=edad, test1=int(porcentaje1), test2=int(porcentaje2), resultado=estado, profesor_id=id )
    session.add(alumno)
    session.commit()
    return render_template('End.html')

@app.route('/alumnos/<id>', methods=['GET'])
def get_alumnos(id):
    session = db.getSession(engine)
    alumnos = session.query(entities.Alumno).filter(entities.Alumno.profesor_id == id)
    response = []
    for user in alumnos:
        response.append(user)
    return json.dumps(response, cls=connector.AlchemyEncoder)

@app.route('/alumnos/<id>/name', methods=['GET'])
def get_alumno(id,name):
    session = db.getSession(engine)
    alumnos = session.query(entities.Alumno).filter(entities.Alumno.profesor_id == id, entities.Alumno.name==name)
    for alumno in alumnos:
        js = json.dumps(alumno, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { "status": 404, "message": "Not Found"}
    return Response(message, status=404, mimetype='application/json')

if __name__ == '__main__':
    app.run()
