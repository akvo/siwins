import json

prev_file = "./source/forms/647170919.json"
new_file = "./source/new_form.json"

with open(prev_file, 'r') as json_file:
    prev_json = json.load(json_file)

with open(new_file, 'r') as json_file:
    new_json = json.load(json_file)

prev_qg = prev_json.get('questionGroup')
new_qg = new_json.get('questionGroup')

for qgi, qg in enumerate(new_qg):
    find_prev_qg = prev_qg[qgi]

    prev_question = find_prev_qg['question']
    if isinstance(prev_question, dict):
        prev_question = [prev_question]

    for qi, q in enumerate(qg['question']):
        qid = q['id']
        if "Q" in qid:
            qid = qid[1:]
        find_prev_q = list(filter(
            lambda obj: obj["id"] == qid,
            prev_question
        ))[0]
        # remap
        q["id"] = qid
        if "attributes" in find_prev_q:
            q["attributes"] = find_prev_q["attributes"]
        if "displayName" in find_prev_q:
            q["displayName"] = find_prev_q["displayName"]
        # end of remap

new_json["questionGroup"] = new_qg

with open("./source/remapped_form.json", 'w') as json_file:
    json.dump(new_json, json_file, indent=2)
