from flask import render_template, redirect, url_for, request, send_file
from app.models import Opinion, Product
from app import app
import pandas as pd
import numpy as np
import requests
import os

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html.jinja")

@app.route('/products')
def products():
    products = []
    for file in os.listdir("app/products"):
        products.append(Product(int(file[:-5])).import_from_json())
    return render_template("products.html.jinja", products=products)

@app.route('/product/<product_id>')
def product(product_id):
    product = Product(product_id)
    product.import_from_json()
    return render_template("product.html.jinja", product=product)

@app.route('/author')
def author():
    return render_template("author.html.jinja")

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    if request.method == 'POST':
        product_id = request.form.get("product_id")
        product = Product(product_id)
        product.extract_name()
        if product.product_name is None:
            return render_template("extract.html.jinja", error="Podana wartość nie jest poprawnym kodem produktu.")
        else:
            product.extract_opinions().analyze().export_to_json()
            return redirect(url_for('product', product_id=product_id))
    return render_template("extract.html.jinja")

@app.route('/file/csv/<product_id>')
def download_csv(product_id):
    product = Product(product_id)
    product.import_from_json()
    opinions = []
    for opinion in product.opinions:
        opinions.append(opinion.to_dict())
    dataframe = pd.DataFrame(opinions)
    dataframe.to_csv("app/meta/" + str(product_id) + ".csv")
    return send_file('meta/' + str(product_id) + '.csv', mimetype='csv', as_attachment=True)

@app.route('/file/json/<product_id>')
def download_json(product_id):
    product = Product(product_id)
    product.import_from_json()
    opinions = []
    for opinion in product.opinions:
        opinions.append(opinion.to_dict())
    dataframe = pd.DataFrame(opinions)
    dataframe.to_json("app/meta/" + str(product_id) + ".json", orient='records')
    return send_file('meta/' + str(product_id) + '.json', as_attachment=True)

@app.route('/file/xlsx/<product_id>')
def download_xlsx(product_id):
    product = Product(product_id)
    product.import_from_json()
    opinions = []
    for opinion in product.opinions:
        opinions.append(opinion.to_dict())
    dataframe = pd.DataFrame(opinions)
    dataframe.to_excel("app/meta/" + str(product_id) + ".xlsx")
    return send_file('meta/' + str(product_id) + '.xlsx', mimetype='xlsx', as_attachment=True)

@app.route('/chart/<product_id>')
def chart(product_id):
    product = Product(product_id)
    product.import_from_json()
    product.create_pie_chart()
    return render_template('charts.html.jinja')
