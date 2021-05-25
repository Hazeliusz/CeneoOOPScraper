from app.models import Product
from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/products')
def products():
    pass

@app.route('/product/<product_id>')
def product(product_id):
    pass

@app.route('/author')
def author():
    pass

@app.route('/extract/<product_id>')
def extract(product_id):
    product = Product(product_id)
    product.extract_opinions().analyze().export_to_json()
    return str(product)

