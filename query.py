import requests
from pprint import pprint
from followthemoney import model
from requests_cache import CachedSession

ENDPOINT_URL = "https://query.wikidata.org/sparql"
LINKS = {
    "P40": "child",
    "P26": "spouse",
    "P25": "mother",
    "P22": "father",
    "P43": "stepfather",
    "P44": "stepmother",
    "P1038": "relative",
    "P7": "brother",
    "P9": "sister",
    # 'P108': 'employer',
    # 'P102': 'party',
    # 'P463': 'member'
}

session = CachedSession()


def uri_to_entity(uri):
    return uri.rsplit("/", 1)[-1]


class Statement(object):
    def __init__(self, binding):
        self.binding = binding
        prop = binding.get("prop", {})
        self.prop = uri_to_entity(prop.get("value"))
        claim_label = binding.get("claimLabel", {})
        self.prop_label = claim_label.get("value")
        value = binding.get("statement")
        value = binding.get("value", value)
        self.value = value.get("value")
        self.type = value.get("type")
        self.lang = value.get("xml:lang")
        value_label = binding.get("valueLabel", {})
        value_label = claim_label.get("value")
        self.value_label = None
        if value_label == self.value:
            self.value_label = value_label

    def __repr__(self):
        vtext = self.value
        if self.value_label is not None:
            vtext = "%s (%s)" % (vtext, self.value_label)
        return "%s %s -[%s:%s]-> %s" % (
            self.prop,
            self.prop_label,
            self.type,
            self.lang,
            vtext,
        )


def execute_query(query):
    headers = {"Accept": "application/sparql-results+json"}
    res = session.get(ENDPOINT_URL, headers=headers, params={"query": query})
    if res.status_code == 429:
        import time

        time.sleep(2)
        return
    data = res.json()
    results = data.get("results", {})
    for result in results.get("bindings"):
        yield result


def values(statements, prop, pick=True):
    values = []
    for stmt in statements.pop(prop, []):
        if stmt.type == "uri":
            qid = uri_to_entity(stmt.value)
            values.extend(fetch_labels(qid, pick=pick))
        if stmt.type == "literal":
            values.append(stmt.value)
    return values


def fetch_labels(qid, pick=True):
    query = """
    select distinct ?value where { wd:%s rdfs:label ?value . }
    """
    for binding in execute_query(query % qid):
        value = binding.get("value", {})
        if not pick or value.get("xml:lang") == "en":
            yield value.get("value")


def fetch_entity(qid):
    query = """
    select distinct ?prop ?claim ?claimLabel ?statement ?value ?valueLabel
                    ?starttime ?endtime ?time where {
        wd:%s ?prop ?statement .
        OPTIONAL {
        ?statement ?ps ?value .

        ?claim wikibase:claim ?prop.
        ?claim wikibase:statementProperty ?ps.
        }
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
    statements = {}
    for result in execute_query(query % qid):
        stmt = Statement(result)
        if stmt.prop not in statements:
            statements[stmt.prop] = []
        statements[stmt.prop].append(stmt)

    instance_of = statements.pop("P31", [])
    instance_of = [uri_to_entity(s.value) for s in instance_of]
    if "Q5" not in instance_of:
        print("NOT A HUMAN", qid)
        return None

    entity = model.make_entity("Person")
    entity.id = qid
    entity.add("alias", values(statements, "rdf-schema#label"))
    entity.add("weakAlias", values(statements, "core#altLabel"))
    entity.add("alias", values(statements, "P1477"))
    entity.add("name", values(statements, "P1559"))
    entity.add("firstName", values(statements, "P735"))
    entity.add("lastName", values(statements, "P734"))
    entity.add("gender", values(statements, "P21", pick=True))
    entity.add("religion", values(statements, "P140", pick=True))
    entity.add("political", values(statements, "P1142", pick=True))
    entity.add("birthDate", values(statements, "P569"))
    entity.add("birthPlace", values(statements, "P19", pick=True))
    entity.add("website", values(statements, "P856"))
    entity.add("education", values(statements, "P512", pick=True))
    entity.add("nationality", values(statements, "P27"))

    descriptions = statements.pop("description")
    descriptions = [
        d.value for d in descriptions if d.lang is None or d.lang.startswith("en")
    ]
    entity.add("notes", descriptions)

    pprint(entity.to_dict())
    pprint(statements)


BOJO = "Q180589"

fetch_entity(BOJO)
# fetch_labels("Q666112")
