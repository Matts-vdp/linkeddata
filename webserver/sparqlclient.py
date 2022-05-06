from SPARQLWrapper import SPARQLWrapper, JSON
from matplotlib.figure import Figure
import numpy as np

def exec_query(query):
    sparql = SPARQLWrapper("http://localhost:8890/sparql")
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
    """retreives for the production stats for a country"""
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
        years.append(result["y"]['value'])
        produced.append(result["callret-1"]['value'])
        used.append(result["callret-2"]['value'])
    return years, produced, used


if __name__ == "__main__":
    print(get_countries())
    