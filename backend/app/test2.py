import json
from pprint import pprint


def process_query_results(query_results, mcj="no"):
    if "documents" not in query_results:
        return []

    documents = query_results["documents"]
    distances = query_results.get("distances", [])

    # Flatten docs if nested
    if len(documents) == 1 and isinstance(documents[0], list):
        try:
            documents = [json.loads(doc) for doc in documents[0]]
        except Exception:
            documents = documents[0]

    # --- Apply distance filter ---
    if mcj == "yes" and distances:
        filtered_pairs = []
        for doc_list, dist_list in zip([documents], distances):  # wrap in list so zip works
            for d, dist in zip(doc_list, dist_list):
                if dist <= 0.9:
                    filtered_pairs.append((d, dist))

        # Sort by distance (nearest first)
        filtered_pairs.sort(key=lambda x: x[1])

        # Keep max 5
        filtered_docs = [d for d, _ in filtered_pairs[:5]]

        return filtered_docs

    return documents


result = {
    'ids': [[
        'id-1', 'id-2', 'id-3', 'id-4', 'id-5',
        'id-6', 'id-7', 'id-8', 'id-9', 'id-10'
    ]],
    'embeddings': None,
    'documents': [[
        '{"question": "Find all people who were awarded in the year 2020.", "sql": "SELECT name, rank, award FROM discipline_data WHERE year = 2020;"}',
        '{"question": "List all distinct categories of offences.", "sql": "SELECT DISTINCT cat FROM discipline_data;"}',
        '{"question": "Get the names and ranks of people from unit \'Alpha Unit\'.", "sql": "SELECT name, rank FROM discipline_data WHERE unit = \'Alpha Unit\';"}',
        '{"question": "Show all records where punishment was awarded.", "sql": "SELECT * FROM discipline_data WHERE punishment IS NOT NULL;"}',
        '{"question": "Find all cases initiated in 2021.", "sql": "SELECT * FROM discipline_data WHERE YEAR(date) = 2021;"}',
        '{"question": "List all unique ranks.", "sql": "SELECT DISTINCT rank FROM discipline_data;"}',
        '{"question": "Get the earliest offence recorded.", "sql": "SELECT * FROM discipline_data ORDER BY date ASC LIMIT 1;"}',
        '{"question": "Count the number of cases per category.", "sql": "SELECT cat, COUNT(*) FROM discipline_data GROUP BY cat;"}',
        '{"question": "Show people with more than 2 offences.", "sql": "SELECT name, COUNT(*) FROM discipline_data GROUP BY name HAVING COUNT(*) > 2;"}',
        '{"question": "Find people belonging to unit \'Bravo Unit\'.", "sql": "SELECT name, rank FROM discipline_data WHERE unit = \'Bravo Unit\';"}'
    ]],
    'uris': None,
    'included': ['metadatas', 'documents', 'distances'],
    'data': None,
    'metadatas': [[None] * 10],
    'distances': [[
        0.824,  # ✅ keep
        0.886,  # ✅ keep
        1.072,  # ❌ too far
        0.350,  # ✅ keep (very close)
        0.920,  # ❌ too far
        0.410,  # ✅ keep
        0.870,  # ✅ keep
        0.760,  # ✅ keep
        0.945,  # ❌ too far
        0.510   # ✅ keep
    ]]
}

pprint(process_query_results(query_results=result, mcj="yes"))

# if 0.4353567361831665 <= 0.9:
#     print("yes: ", round(0.4353567361831665))
# else:
#     print("no: ", round(0.940322995185852))