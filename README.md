# FollowTheMoney / Wikidata mappings

This repo will contain tools for converting Wikidata entities into FtM schema.

Prefixes: https://www.mediawiki.org/wiki/Wikibase/Indexing/RDF_Dump_Format#Full_list_of_prefixes 

https://github.com/tmtmtmtm/every-politician-scraper/blob/main/lib/every_politician_scraper/wikidata_query.rb#L87

https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Current_U.S._members_of_the_Senate_with_district,_party_and_date_they_assumed_office

https://stackoverflow.com/questions/46383784/wikidata-get-all-properties-with-labels-and-values-of-an-item/46385132

### What do I want?

* People as entities
* Organizations as entities
* Membership of people in certain bodies
    * Query all legislatures
    * Query all cabinets
    * Query SOEs


### Query experimentation

Get statement properties on all properties for the given entity:

```sql
select distinct ?statement ?wd ?wdLabel ?ps_ ?ps_Label ?wdpq ?wdpqLabel ?pq_ ?pq_Label where {
    wd:Q180589 ?p ?statement .
    ?statement ?ps ?ps_ .

    ?wd wikibase:claim ?p.
    ?wd wikibase:statementProperty ?ps.

    OPTIONAL {
      ?statement ?pq ?pq_ .
      ?wdpq wikibase:qualifier ?pq .
    }

    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
```

What statement properties (ie. the metadata properties) are we interested in?

* pq:P580 - start time
* pq:P582 - end time
* pq:P585 - point in time

* wd:P4100 - parliamentary group
* wd:P768 - district 
* wd:P1534 - end cause

```sql
select distinct ?statement ?wd ?wdLabel ?value ?valueLabel ?starttime ?endtime ?time where {
    wd:Q180589 ?p ?statement .
    ?statement ?ps ?value .

    ?wd wikibase:claim ?p.
    ?wd wikibase:statementProperty ?ps.

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
```

How to get source/reference URLs: https://en.wikibooks.org/wiki/SPARQL/WIKIDATA_Qualifiers,_References_and_Ranks 