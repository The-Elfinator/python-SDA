import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI()

url_key_mapping = {}
key_url_mapping: dict[str, str] = {}


class ToShort(BaseModel):
    url: str


class Shorted(BaseModel):
    url: str
    key: str


@app.post("/shorten", response_model=Shorted, status_code=201)
async def short_url(request: ToShort) -> Shorted:
    url = request.url
    if url in key_url_mapping:
        key = key_url_mapping[url]
    else:
        key = str(uuid.uuid4())
    url_key_mapping[key] = url
    key_url_mapping[url] = key
    return Shorted(url=url, key=key)


@app.get("/go/{key}", response_class=RedirectResponse, status_code=307,
         responses={
             307: {
                 "content": {"application/json": {"schema": {"title": "Response Redirect To Url Go  Key  Get"}}},
             }
         }
         )
async def redirect_to_url(key: str) -> RedirectResponse:
    url = url_key_mapping.get(key)
    if url is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return RedirectResponse(url)
