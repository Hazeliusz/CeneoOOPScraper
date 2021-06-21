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

@app.route('/product/<product_id>', methods=['POST', 'GET'])
def product(product_id):
    if request.method == 'GET':
        product = Product(product_id)
        product.import_from_json()
        return render_template("product.html.jinja", product=product, opinions=product.opinions)
    elif request.method == 'POST':
        product = Product(product_id)
        product.import_from_json()
        opinions = []
        error = 0
        for opinion in product.opinions:
            opinions.append(opinion.to_dict())
        dataframe = pd.DataFrame(opinions)
        print(request.form)
        if len(request.form['sortby']) > 0:
            dataframe = dataframe.sort_values(by=[request.form['sortby']])
            if len(request.form['descending']) != 0:
                dataframe = dataframe.iloc[::-1]
        if request.form['recommendations'] != "recommend_all":
            if request.form['recommendations'] == "recommended":
                dataframe = dataframe.loc[dataframe['recommendation'] == True]
            elif request.form['recommendations'] == "not_recommended":
                dataframe = dataframe.loc[dataframe['recommendation'] == False]
            elif request.form['recommendations'] == "recommended_both":
                dataframe = dataframe.loc[dataframe['recommendation'] != None]
        if len(request.form['stars_higher']) != 0:
            try:
                dataframe = dataframe.loc[dataframe['stars'] > float(request.form['stars_higher_than'])]
            except ValueError:
                error = "Do formularza wprowadzono niepoprawne dane."
        if len(request.form['stars_lower']) != 0:
            try:
                dataframe = dataframe.loc[dataframe['stars'] < float(request.form['stars_lower_than'])]
            except ValueError:
                error = "Do formularza wprowadzono niepoprawne dane."

        if request.form['verified'] != "verified_all":
            if request.form['verified'] == "verified":
                dataframe = dataframe.loc[dataframe['verified'] == True]
            else:
                dataframe = dataframe.loc[dataframe['verified'] == False]

        if len(request.form['useful_higher']) != 0:
            try:
                dataframe = dataframe.loc[dataframe['usefulness'] > int(request.form['useful_higher_than'])]
            except ValueError:
                error = "Do formularza wprowadzono niepoprawne dane."
        if len(request.form['useful_lower']) != 0:
            try:
                dataframe = dataframe.loc[dataframe['usefulness'] < int(request.form['useful_lower_than'])]
            except ValueError:
                error = "Do formularza wprowadzono niepoprawne dane."

        if len(request.form['uselessness_higher']) != 0:
            try:
                dataframe = dataframe.loc[dataframe['uselessness'] > int(request.form['uselessness_higher_than'])]
            except ValueError:
                error = "Do formularza wprowadzono niepoprawne dane."
        if len(request.form['uselessness_lower']) != 0:
            try:
                dataframe = dataframe.loc[dataframe['uselessness'] < int(request.form['uselessness_lower_than'])]
            except ValueError:
                error = "Do formularza wprowadzono niepoprawne dane."
        return render_template("product.html.jinja", product=product, opinions = dataframe.to_dict('records'), error=error)

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
            product.create_pie_chart()
            product.create_bar_chart()
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
    return render_template('charts.html.jinja', product_id=product_id)
