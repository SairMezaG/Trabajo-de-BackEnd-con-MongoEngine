from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mongoengine import MongoEngine
import urllib.request

app = Flask(__name__)
app.secret_key = 'MiClaveSecreta'

# Configuración de la base de datos MongoDB con MongoEngine
app.config['MONGODB_SETTINGS'] = {
    'db': 'GESTIONPRODUCTOS',
    'host': 'mongodb://localhost:27017/GESTIONPRODUCTOS'
}
db = MongoEngine(app)

# Definimos el modelo de datos de Usuario
class Usuarios(db.Document):
    usuario = db.StringField(required=True)
    contrasenia = db.StringField(required=True)

# Definimos el modelo datos de Producto
class Productos(db.Document):
    codigo = db.StringField(required=True)
    nombre = db.StringField(required=True)
    precio = db.IntField(required=True)
    categoria = db.StringField(required=True)
    foto = db.StringField(required=True)

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/agregarProducto', methods=['GET', 'POST'])
#Recibimos los datos del formulario del name
def agregarProducto():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        precio = request.form['precio']
        categoria = request.form['categoria']
        foto = request.files['foto']

        # Verificar si el código del producto ya existe en la base de datos
        if Productos.objects(codigo=codigo).first():
            flash('Ya existe un producto con ese código', 'error')
            return redirect(url_for('agregarProducto'))

        # Si el código no existe se guarda en la base de datos
        producto = Productos(
            codigo=codigo,
            nombre=nombre,
            precio=precio,
            categoria=categoria,
            foto=foto.filename
        )
        producto.save() #Esta es la instruccion que guarda el producto

        flash('Producto agregado correctamente', 'success') #Flask  es para mostrar los mensajes desde el lado del cliente
        return redirect(url_for('agregarProducto'))

    else:
        productos = Productos.objects().all()
        return render_template('agregarProducto.html', productos=productos)
    
    

@app.route('/consultarProducto', methods=['GET'])
def consultarProducto():
    codigo = request.args.get('codigo')
    producto = Productos.objects(codigo=codigo).first()
    if producto:
        return render_template('productoEncontrado.html', producto=producto)
    else:
        flash(f'No se encontró el producto con el código: {codigo}', 'error')
    return redirect(url_for('productoNoEncontrado', codigo=codigo))


    
#Esta funcion es para que se muestre en un documento aparte si no encontró el producto   
@app.route('/productoNoEncontrado')    
def productoNoEncontrado():
    return render_template('productoNoEncontrado.html') 

#Esta funcion es para que se muestre en un documento aparte si encontró el producto   
@app.route('/productoEncontrado')    
def productoEncontrado():
    return render_template('productoEncontrado.html') 


   

@app.route('/editarProducto/<string:codigo>', methods=['GET', 'POST'])
def editarProducto(codigo):
    producto = Productos.objects(codigo=codigo).first()
    if not producto:
        flash('El producto no existe', 'error')
        return redirect(url_for('agregarProducto'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        categoria = request.form['categoria']
        foto = request.files['foto'] if 'foto' in request.files else None

        producto.nombre = nombre
        producto.precio = precio
        producto.categoria = categoria
        if foto:
            producto.foto = foto.filename
        producto.save()

        flash('Producto actualizado correctamente', 'success')
        return redirect(url_for('agregarProducto'))

    else:
        return render_template('editarProducto.html', producto=producto)
    
    
from flask import abort

@app.route('/eliminarProducto/<string:codigo>', methods=['POST'])
def eliminarProducto(codigo):
    producto = Productos.objects(codigo=codigo).first()
    
    if producto:
        producto.delete()
        return redirect(url_for('agregarProducto'))
    else:
        abort(404, "El producto no existe")

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Validar recaptcha"""
    recaptcha_response = request.form["g-recaptcha-response"]
    url= "https://www.google.com/recaptcha/api/siteverify " 
    values = {
        "secret": "6LfIILcpAAAAAPfyB3L3TqRqpGqh1dez21GvaumE",
        "response": recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data = data)
    respose = urllib.request.urlopen(req)
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasenia = request.form['contrasenia']
      
        user = Usuarios.objects(usuario=usuario, contrasenia=contrasenia).first()

        if user:
            session['usuario'] = usuario
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('agregarProducto'))
        else:
            flash('Usuario o contraseña incorrectos. Inténtalo de nuevo.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(port=3000, debug=True)
    

    