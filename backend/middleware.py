import re
from fastapi import HTTPException

query_pattern = re.compile(r"[0-9]*\|(.*)")


def check_query(keywords):
    keys = []
    if not keywords:
        return keys
    for q in keywords:
        if not query_pattern.match(q):
            raise HTTPException(status_code=400, detail="Bad Request")
        else:
            keys.append(q.replace("|", "||"))
    return keys
