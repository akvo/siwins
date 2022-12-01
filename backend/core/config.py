# import jwt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.data import data_route


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
