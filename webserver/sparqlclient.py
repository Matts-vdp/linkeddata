from SPARQLWrapper import SPARQLWrapper, JSON
from matplotlib.figure import Figure
import numpy as np

def exec_query(query: str, local=True):
    if local:
        sparql = SPARQLWrapper(
            "http://virtuoso:8890/sparql", 
            defaultGraph="http://localhost:8890/dataset", 
            agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
            )
    else:
        sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
    

def get_countries():
    """retrieves all country names"""
    query = """
    prefix ex: <http://example.com/>
    select ?o
    WHERE {
        ?s a ex:Country.
        ?s ex:hasName ?o.
    }
    ORDER BY ?o
    """
    results = exec_query(query)
    names = []
    for result in results["results"]["bindings"]:
        names.append(result["o"]["value"])
    return names

def stats(country: str):
    """retrieves the production and use stats for a country"""
    query = f"""
    prefix ex: <http://example.com/>
    select ?y SUM(?pr) SUM(?u)
    WHERE {{
        ?c a ex:Country.
        ?c ex:hasName "{country}".
        ?p ex:inCountry ?c.
        ?p ex:year ?y.
        ?p ex:produced ?pr.
        ?p ex:used ?u.
    }}
    GROUP BY ?y
    ORDER BY ?y
    """
    results = exec_query(query)
    years, produced, used = [], [], []
    for result in results['results']['bindings']:
        years.append(int(result["y"]['value']))
        produced.append(float(result["callret-1"]['value']))
        used.append(float(result["callret-2"]['value']))
    return years, produced, used

def get_link(country: str):
    query = f"""
    prefix ex: <http://example.com/>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    select ?o
    WHERE {{
        ?c a ex:Country.
        ?c ex:hasName "{country}".
        ?c owl:sameAs ?o
    }}
    """
    results = exec_query(query)
    if len(results['results']['bindings']) == 0:
        return ""
    res = results['results']['bindings'][0]['o']['value']
    cid = res.split("/")[-1]
    return cid


def info(country: str):
    cid = get_link(country)
    if cid == "":
        return "", "Country not found on Wikidata", "Country not found on Wikidata", "Country not linked to Wikidata"
    query = f"""
    prefix ex: <http://example.com/>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix wd: <http://www.wikidata.org/entity/>
    select ?inc ?img ?capl
    WHERE {{
        wd:{cid} wdt:P18 ?img.
        wd:{cid} wdt:P571 ?inc.
        wd:{cid} wdt:P36 ?cap.
        ?cap rdfs:label ?capl
        FILTER(lang(?capl)="en").
    }}
    LIMIT 10
    """
    try:
        results = exec_query(query, False)
        res = results['results']['bindings'][0]
        return res['img']['value'], res['inc']['value'], res['capl']['value'], ""
    except Exception as e:
        return "", "Wikidata timeout", "Wikidata timeout", e

def getTop(country: str, value: str):
    """top produced and used products of a country"""
    query = f"""
    prefix ex: <http://example.com/>
    select ?name (SUM(?pr) as ?val)
    WHERE {{
        ?c a ex:Country.
        ?c ex:hasName "{country}".
        ?p ex:inCountry ?c.
        ?p ex:{value} ?pr.
        ?p ex:product ?com.
        ?com ex:hasName ?name.
    }}
    GROUP BY ?name
    ORDER BY DESC (?val) 
    LIMIT 5
    """
    results = exec_query(query)
    top = {}
    for result in results['results']['bindings']:
        top[result['name']['value']] = float(result['val']['value'])
    return top

if __name__ == "__main__":
    print(getTop("Belgium", 'used'))
    