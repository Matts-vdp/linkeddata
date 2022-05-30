import base64
from io import BytesIO

from flask import Flask, render_template, request, redirect
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sparqlclient as sc
import numpy as np
from flask_caching import Cache


config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

def fig_to_html(fig: Figure):
    """convert figure to html with base 64 encoded image"""
    
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    img = f"<img class='gr' src='data:image/png;base64,{data}'/>"
    return img

def stats_graph(country: str):
    y, p, u = sc.stats(country)
    if len(y) == 0:
        return ""
    x = np.arange(len(y))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(7)  

    ax.plot(y, p, linewidth=3, label="Production")
    ax.plot(y, u, linewidth=3, label="Use")

    ax.set_ylabel('Thousand tons')
    ax.set_xlabel('Year')
    # ax.set_xticks(x)
    ax.set_xticklabels(y)
    ax.legend()
    ax.grid(True)

    return fig_to_html(fig)

def dispay_top(country:str, value: str):
    top = sc.getTop(country, value)
    html = ''
    i = 1
    for name, amount in top.items():
        html += f'''<tr>
            <div class="first item {value}">{i}</div>
            <div class="item {value}">{name.lower()}</div>
            <div class="last item {value}">{amount:.0f}</div>
        </tr>'''
        i += 1
    return html

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
@cache.cached(timeout=100, query_string=True)
def country():
    args = request.args
    name = args.get("name", default="", type=str)
    if name == "":
        return redirect("/")
    img = stats_graph(name)
    if img == "":
        return redirect("/")
    cim, inc, cap, e = sc.info(name)
    if e != "":
        print(e)
    return render_template(
        "country.html", 
        graph = img, 
        country = name, 
        image = cim,
        capital = cap,
        inception = inc,
        ptable = dispay_top(name, 'produced'),
        utable = dispay_top(name, 'used'),
        )
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')