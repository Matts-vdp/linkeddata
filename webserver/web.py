import base64
from io import BytesIO

from flask import Flask, render_template, request, redirect
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sparqlclient as sc
import numpy as np

app = Flask(__name__)


def fig_to_html(fig: Figure):
    """convert figure to html with base 64 encoded image"""
    
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    img = f"<img src='data:image/png;base64,{data}'/>"
    return img

def stats_graph(country):
    y, p, u = sc.stats(country)
    if len(y) == 0:
        return ""
    x = np.arange(len(y))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    fig.set_figheight(10)
    fig.set_figwidth(10)  
    ax.bar(x - width/2, p, width, label='Production')
    ax.bar(x + width/2, u, width, label='Use')

    ax.set_ylabel('Thousand tons')
    ax.set_xlabel('Year')
    ax.set_title(f'Production and use in {country}')
    ax.set_xticks(x)
    ax.set_xticklabels(y)
    ax.legend()

    return fig_to_html(fig)

def get_countries():
    countries = sc.get_countries()
    html = ""
    for c in countries:
        html += f"<a href='/country?name={c}'>{c}</a>"
    return html


@app.route("/")
def hello():
    l = get_countries()
    return render_template("web.html", list=l) 

@app.route('/country', methods=['GET'])
def country():
    args = request.args
    name = args.get("name", default="", type=str)
    if name == "":
        return redirect("/")
    img = stats_graph(name)
    if img == "":
        return redirect("/")
    return render_template("country.html", graph=img)
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')