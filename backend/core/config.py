# import jwt
import json
from jsmin import jsmin
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from functools import lru_cache
from pydantic import BaseSettings
from routes.data import data_route
from routes.question import question_route
from routes.cascade import cascade_route
from routes.charts import charts_route
from routes.answer import answer_route
from AkvoResponseGrouper.routes import collection_route
from source.geoconfig import GeoLevels, GeoCenter
from source.main_config import CLASS_PATH, TOPO_JSON_PATH, FRONTEND_CONFIG_PATH

TOPO_JSON = open(TOPO_JSON_PATH).read()
GEO_CONFIG = GeoLevels[CLASS_PATH].value
MAP_CENTER = GeoCenter[CLASS_PATH].value
CHART_CONFIG = f"{FRONTEND_CONFIG_PATH}/charts.js"
CHART_CONFIG = jsmin(open(CHART_CONFIG).read())
HINT_CONFIG = f"{FRONTEND_CONFIG_PATH}/indicator-hint.json"
JMP_HINT_CONFIG = f"{FRONTEND_CONFIG_PATH}/jmp-hint.json"
JMP_CONFIG = f"{FRONTEND_CONFIG_PATH}/dashboard.json"
HINT_JSON = open(HINT_CONFIG).read()
JMP_HINT_JSON = open(JMP_HINT_CONFIG).read()
DASHBOARD_JSON = open(JMP_CONFIG).read()

MINJS = jsmin(
    "".join(
        [
            "var levels=",
            json.dumps([g["alias"] for g in GEO_CONFIG]),
            ";",
            "var mapConfig={shapeLevels:",
            json.dumps([g["name"] for g in GEO_CONFIG]),
            ", center:",
            json.dumps(MAP_CENTER),
            "};",
            "var topojson=",
            TOPO_JSON,
            ";",
            "var hintjson=",
            HINT_JSON,
            ";",
            "var jmphintjson=",
            JMP_HINT_JSON,
            ";",
            "var dashboardjson=",
            DASHBOARD_JSON,
            ";",
            CHART_CONFIG,
        ]
    )
)
JS_FILE = f"{FRONTEND_CONFIG_PATH}/config.min.js"
open(JS_FILE, "w").write(MINJS)


class Settings(BaseSettings):
    js_file: str = JS_FILE


settings = Settings()
app = FastAPI(
    root_path="/api",
    title="SI-WINS",
    description="Solomon Island - WASH in Schools",
    version="1.0.0",
    contact={
        "name": "Akvo",
        "url": "https://akvo.org",
        "email": "dev@akvo.org",
    },
    license_info={
        "name": "AGPL3",
        "url": "https://www.gnu.org/licenses/agpl-3.0.en.html",
    },
)

origins = ["http://localhost:3000"]
methods = ["GET"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=["*"],
)

app.include_router(cascade_route)
app.include_router(question_route)
app.include_router(data_route)
app.include_router(collection_route)
app.include_router(charts_route)
app.include_router(answer_route)


@lru_cache()
def get_setting():
    return Settings()


@app.get(
    "/config.js",
    response_class=FileResponse,
    tags=["Config"],
    name="config.js",
    description="static javascript config",
)
async def main(res: Response):
    res.headers["Content-Type"] = "application/x-javascript; charset=utf-8"
    return settings.js_file


@app.get("/", tags=["Dev"])
def read_main():
    return "OK"


@app.get("/health-check", tags=["Dev"])
def health_check():
    return "OK"


# @app.middleware("http")
# async def route_middleware(request: Request, call_next):
#     auth = request.headers.get('Authorization')
#     if auth:
#         auth = jwt.decode(
#             auth.replace("Bearer ", ""), options={"verify_signature": False})
#         request.state.authenticated = auth
#     response = await call_next(request)
#     return response
