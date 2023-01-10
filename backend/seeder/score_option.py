import json
from db import crud_option
from db.connection import SessionLocal

session = SessionLocal()

jmp_criteria_config_source = "./source/static/visualisation.json"
jmp_criteria_json = open(jmp_criteria_config_source, "r")
jmp_criteria_json = json.load(jmp_criteria_json)
jmp_criteria = [cf.get("options") for cf in jmp_criteria_json]
for criterias in jmp_criteria:
    for criteria in criterias:
        for option in criteria.get("options"):
            print(f"update score for question id: {option.get('question')}")
            crud_option.update_score(
                session=session,
                question=option.get("question"),
                names=option.get("option"),
                score=criteria.get("score"),
            )
