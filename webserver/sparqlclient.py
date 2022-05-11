from SPARQLWrapper import SPARQLWrapper, JSON
from matplotlib.figure import Figure
import numpy as np

def exec_query(query):
    sparql = SPARQLWrapper("http://virtuoso:8890/sparql", 'https://query.wikidata.org')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
    
def get_countries():
    """retrieves all country names"""
    query = """
    prefix ex: <http://example.com/>
    select ?o
    FROM <http://localhost:8890/dataset>
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
    FROM <http://localhost:8890/dataset>
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

def dbpedia(country: str):
    query = f"""
    prefix ex: <http://example.com/>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    select ?s ?o ?p ?o2
    FROM <http://localhost:8890/dataset>
    WHERE {{
        ?s owl:sameAs ?o.
        ?o ?p ?o2.
    }}
    LIMIT 10
    """
    results = exec_query(query)
    for res in results['results']['bindings']:
        print(res['s']['value'], res['o']['value'], res['p']['value'], res['o2']['value'])


if __name__ == "__main__":
    print(dbpedia("Belgium"))
    