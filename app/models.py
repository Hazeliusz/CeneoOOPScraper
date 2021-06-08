from app.utils import get_component
from bs4 import BeautifulSoup
import requests
import json
import re

class Product:

    def __init__(self, product_id, product_name = None, opinions = [], opinions_count = None, pros_count = None, cons_count = None, average_score = None):
        self.product_id = product_id
        self.product_name = product_name
        self.opinions = opinions.copy()
        self.opinions_count = opinions_count
        self.pros_count = pros_count
        self.cons_count = cons_count
        self.average_score = average_score

    def extract_name(self):
        response = requests.get(f"https://www.ceneo.pl/{self.product_id}#tab=reviews")
        if response.status_code == 200:
            page_dom = BeautifulSoup(response.text, 'html.parser')
            self.product_name = get_component(page_dom, ".js_product-h1-link")

    def extract_opinions(self):
        page = 1
        while True:
            response = requests.get(f"https://www.ceneo.pl/{self.product_id}/opinie-{page}", allow_redirects=False)
            if response.status_code == 200:
                page_dom = BeautifulSoup(response.text, 'html.parser')
                opinions = page_dom.select("div.js_product-review")
                for opinion in opinions:
                    self.opinions.append(Opinion().extract_components(opinion).transform_components())
                page += 1
            else: break
        return self

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "opinions_count": self.opinions_count,
            "pros_count": self.pros_count,
            "cons_count": self.cons_count,
            "average_score": self.average_score,
            "opinions": [opinion.to_dict() for opinion in self.opinions]
        }

    def __str__(self) -> str:
        return f"""product_id: {self.product_id}<br>
        product_name: {self.product_name}<br>
        opinions_count: {self.opinions_count}<br>
        pros_count: {self.pros_count}<br>
        cons_count: {self.cons_count}<br>
        average_score: {self.average_score}<br>
        opinions: <br><br>
        """ + "<br><br>".join(str(opinion) for opinion in self.opinions)

    def __repr__(self) -> str:
        return f"Product(product_id={self.product_id}, product_name={self.product_name}, opinions_count=\
        {self.opinions_count}, pros_count={self.pros_count}, cons_count={self.cons_count}, average_score=\
        {self.average_score}, opinions=[" + ", >".join(opinion.__repr__() for opinion in self.opinions)\
         + "])"

    def export_to_json(self):
        with open(f"app/products/{self.product_id}.json", "w", encoding="UTF-8") as jf:
            json.dump(self.to_dict(), jf, ensure_ascii=False, indent=4)
        return self

    def import_from_json(self):
        with open(f"app/products/{self.product_id}.json", "r", encoding="UTF-8") as jf:
            product = json.load(jf)
        self.product_id = product['product_id']
        self.product_name = product['product_name']
        self.opinions_count = product['opinions_count']
        self.pros_count = product['pros_count']
        self.cons_count = product['cons_count']
        self.average_score = product['average_score']
        opinions = product['opinions']
        for opinion in opinions:
            self.opinions.append(Opinion(**opinion))
        return product

    def analyze(self):
        self.opinions_count = len(self.opinions)
        # self.pros_count = self.opinions.pros.map(bool).sum()
        # self.cons_count = self.opinions.cons.map(bool).sum()
        # self.average_score = self.opinions.stars.mean()
        return self

    def get_bar_chart(self):
        pass

    def get_pie_chart(self):
        pass


class Opinion:

    def __init__(self, opinion_id = None, author = None, recommendation = None, stars = None, content = None, pros = None, cons = None, verified = None,
     post_date = None, purchase_date = None, usefulness = None, uselessness = None) -> None:
        self.opinion_id = opinion_id
        self.author = author
        self.recommendation = recommendation
        self.stars = stars
        self.content = content
        self.pros = pros
        self.cons = cons
        self.verified = verified
        self.post_date = post_date
        self.purchase_date = purchase_date
        self.usefulness = usefulness
        self.uselessness = uselessness

    selectors = {
    "author": ["span.user-post__author-name"],
    "recommendation": ["span.user-post__author-recomendation > em"],
    "stars": ["span.user-post__score-count"],
    "content": ["div.user-post__text"],
    "pros": ["div.review-feature__col:has(> div[class*='positives']) > div.review-feature__item", None, True],
    "cons": ["div.review-feature__col:has(> div[class*='negatives']) > div.review-feature__item", None, True],
    "verified": ["div.review-pz"],
    "post_date": ["span.user-post__published > time:nth-child(1)", "datetime"],
    "purchase_date": ["span.user-post__published > time:nth-child(2)", "datetime"],
    "usefulness": ["span[id^='votes-yes']"],
    "uselessness": ["span[id^='votes-no']"]
    }

    def extract_components(self, opinion):
        for key, value in self.selectors.items():
            setattr(self, key, get_component(opinion, *value))
        self.opinion_id = opinion["data-entry-id"]
        return self

    def transform_components(self):
        self.usefulness = int(self.usefulness)
        self.uselessness = int(self.uselessness)
        self.content = re.sub("\\s", " ", self.content)
        self.stars = float(self.stars.split("/")[0].replace(",", "."))
        self.recommendation = True if self.recommendation == "Polcam" else False if self.recommendation == "Nie polecam" else None
        self.verified = bool(self.verified)
        return self

    def to_dict(self):
        return {key: getattr(self, key) # -> Pyton3.7 :< {"opinion_id": self.opinion_id} | {key: getattr(self, key)
        for key in self.selectors.keys()}

    def __str__(self) -> str:
        return f"opinion_id: {self.opinion_id}<br>" + "<br>".join(f"{key}: {str(getattr(self, key))}" for key in self.selectors.keys())

    def __repr__(self) -> str:
        return f"Opinion(opinion_id={self.opinion_id}, " + ", ".join(f"{key}={str(getattr(self, key))}" for key in self.selectors.keys()) + ")"