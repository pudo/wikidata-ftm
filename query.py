import requests
from pprint import pprint

ENDPOINT_URL = "https://query.wikidata.org/sparql"

def uri_to_entity(uri):
    return uri.rsplit('/', 1)[-1]


class Statement(object):
    def __init__(self, binding):
        self.statement_url = 


def execute_query(query):
    headers = {"Accept": "application/sparql-results+json"}
    res = requests.get(ENDPOINT_URL, headers=headers, params={"query": query})
    data = res.json()
    results = data.get("results", {})
    for result in results.get("bindings"):
        pprint(result)
    # print(data)


QUERY = """
select distinct ?statement ?prop ?propLabel ?value ?valueLabel ?starttime ?endtime ?time where {
    wd:Q180589 ?p ?statement .
    ?statement ?ps ?value .

    ?prop wikibase:claim ?p.
    ?prop wikibase:statementProperty ?ps.

    OPTIONAL {
      ?statement pq:P580 ?starttime.
    }
    OPTIONAL {
      ?statement pq:P582 ?endtime.
    }
    OPTIONAL {
      ?statement pq:P585 ?time.
    }

    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
"""

BOJO = "Q180589"

execute_query(QUERY)
