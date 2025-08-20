from ollama import Client

client = Client()

stream = client.chat(
    model="qwen3:4b",  # "phi4-mini:latest",  # "qwen3:4b",
    messages=[{"role": "system", "content": "You are a MySQL 8 expert. Please help to generate a SQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions. \n===Tables \nCREATE TABLE `discipline_data` (\n  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary key',\n  `doc` date DEFAULT NULL COMMENT 'Date of commission / date of joining',\n  `cat` varchar(255) DEFAULT NULL COMMENT 'Category of offence (e.g., violation of SOP)',\n  `initiation_date` datetime DEFAULT NULL COMMENT 'Exact initiation datetime (yyyy-mm-dd 00:00:00)',\n  `arm` varchar(128) DEFAULT NULL COMMENT 'Employment/arm reflecting war fighting capability',\n  `course` varchar(64) DEFAULT NULL COMMENT 'Unique batch number on passing out from academy',\n  `svc_no` varchar(64) DEFAULT NULL COMMENT 'Unique service number (e.g., PA-12345)',\n  `rank` varchar(64) DEFAULT NULL COMMENT 'Rank of the person',\n  `name` varchar(255) DEFAULT NULL COMMENT 'Name of the person',\n  `parent_unit` varchar(255) DEFAULT NULL COMMENT 'First joining unit after academy',\n  `initiated_by` varchar(255) DEFAULT NULL COMMENT 'Unit/formation initiating the award (organization name)',\n  `award` text COMMENT 'Punishment awarded by formation/HQ (e.g., severe displeasure, warning, reprimand)',\n  `initiation_year` int DEFAULT NULL COMMENT 'Year when the case was initiated (e.g., 2020)',\n  `svc_bracket` int DEFAULT NULL COMMENT 'Service in years at time of award (e.g., 5)',\n  `awardee_unit` varchar(255) DEFAULT NULL COMMENT 'Unit where the person received the award',\n  PRIMARY KEY (`id`),\n  KEY `ix_discipline_data_name` (`name`),\n  KEY `ix_discipline_data_svc_no` (`svc_no`),\n  KEY `ix_discipline_data_initiation_year` (`initiation_year`),\n  KEY `ix_discipline_data_course` (`course`)\n) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci\n\n===Response Guidelines \n1. If the provided context is sufficient, please generate a valid SQL query without any explanations for the question. \n2. If the provided context is almost sufficient but requires knowledge of a specific string in a particular column, please generate an intermediate SQL query to find the distinct strings in that column. Prepend the query with a comment saying intermediate_sql \n3. If the provided context is insufficient, please explain why it can't be generated. \n4. Please use the most relevant table(s). \n5. If the question has been asked and answered before, please repeat the answer exactly as it was given before. \n6. Ensure that the output SQL is MySQL8-compliant and executable, and free of syntax errors. \n"}, {"role": "user", "content": "Find the names and service numbers of all individuals who received more than one type of award."}, {"role": "assistant", "content": "SELECT \n    name,\n    svc_no,\n    initiation_year,\n    COUNT(DISTINCT award) AS distinct_awards\nFROM discipline_data\nGROUP BY name, svc_no, initiation_year\nHAVING COUNT(DISTINCT award) > 1\nORDER BY distinct_awards DESC;"}, {"role": "user", "content": "list the top 3 categories of offences that received the highest number of awards between the years 2018 and 2022"}, {"role": "assistant", "content": "SELECT \n    cat,\n    COUNT(*) AS total_awards,\n    (\n        SELECT award\n        FROM discipline_data d2\n        WHERE d2.cat = d1.cat \n          AND d2.initiation_year BETWEEN 2018 AND 2022\n        GROUP BY award\n        ORDER BY COUNT(*) DESC\n        LIMIT 1\n    ) AS common_award\nFROM discipline_data d1\nWHERE initiation_year BETWEEN 2018 AND 2022\nGROUP BY cat\nORDER BY total_awards DESC\nLIMIT 3;\n"}, {"role": "user", "content": "List the top 3 parent unit that gave the most 'severe displeasure' awards. Show the unit name and total count."}, {"role": "assistant", "content": "SELECT \n    parent_unit,\n    COUNT(*) AS severe_count\nFROM discipline_data\nWHERE award LIKE '%severe displeasure%'\nGROUP BY parent_unit\nORDER BY severe_count DESC\nLIMIT 3;"}, {"role": "user", "content": "please list a simple general trend based on award and offence"}, {"role": "assistant", "content": "SELECT DISTINCT award, cat \nFROM discipline_data"}, {"role": "user", "content": "please list the general trend based on offence"}, {"role": "assistant", "content": "SELECT cat, COUNT(*) AS offense_count\nFROM discipline_data\nGROUP BY cat"}, {"role": "user", "content": "How many distinct awards are there for each category with a non-null and non-empty classification?"}, {"role": "assistant", "content": "SELECT cat, COUNT(DISTINCT award) AS total_awards\nFROM discipline_data\nWHERE cat IS NOT NULL AND cat <> ''\nGROUP BY cat"}, {"role": "user", "content": "Find the person name and service number who had the longest gap in days between their earliest and latest initiation dates."}],
    stream=True,
    think=True,
)

print("\n--- THINKING PROCESS ---\n")
thinking_complete = False
final_answer = ""

import time

start_time = None
for chunk in stream:
    # Show the thinking process in real-time and track thinking time
    if hasattr(chunk.message, 'thinking') and chunk.message.thinking and not thinking_complete:
        if start_time is None:
            start_time = time.time()
        print(chunk.message.thinking, end="", flush=True)
    
    # When thinking is done and we start getting the actual response
    if hasattr(chunk.message, 'content') and chunk.message.content:
        if not thinking_complete:
            if start_time is not None:
                thinking_time = time.time() - start_time
                print(f"\n[Thinking completed in {thinking_time:.2f} seconds]")
            print("\n--- ANSWER ---\n")
            thinking_complete = True
        print(chunk.message.content, end="", flush=True)
        final_answer += chunk.message.content

print("\n\n--- COMPLETE ---\n")