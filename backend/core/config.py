# import jwt
from jsmin import jsmin
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from functools import lru_cache
from pydantic import BaseSettings
from routes.data import data_route
from routes.question import question_route
from source.geoconfig import GeoLevels

CONFIG_NAME = "bali"
SOURCE_PATH = "./source"
TOPO_JSON = f"{SOURCE_PATH}/bali-topojson.json"
TOPO_JSON = open(TOPO_JSON).read()
GEO_CONFIG = GeoLevels[CONFIG_NAME].value
CHART_CONFIG = f"{SOURCE_PATH}/charts.js"
CHART_CONFIG = jsmin(open(CHART_CONFIG).read())

MINJS = jsmin(
    "".join(
        [
            "var levels="
            + str([g["alias"] for g in GEO_CONFIG])
            + ";var map_config={shapeLevels:"
            + str([g["name"] for g in GEO_CONFIG])
            + "};",
            "var topojson=",
            TOPO_JSON,
            ";",
            CHART_CONFIG,
        ]
    )
)
JS_FILE = f"{SOURCE_PATH}/config.min.js"
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

app.include_router(data_route)
app.include_router(question_route)


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
