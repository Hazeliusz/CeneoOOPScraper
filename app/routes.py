from flask import render_template, redirect, url_for
from app.models import Product
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template("layout.html.jinja")

@app.route('/products')
def products():
    return render_template("products")

@app.route('/product/<product_id>')
def product(product_id):
    product = Product(product_id)
    product.import_from_json()
    return render_template("product.html.jinja", product=str(product))

@app.route('/author')
def author():
    pass

@app.route('/extract/<product_id>')
def extract(product_id):
    product = Product(product_id)
    product.extract_opinions().analyze().export_to_json()
    return redirect(url_for('product', product_id=product_id))
    # return render_template("extract.html.jinja", product=str(product))

