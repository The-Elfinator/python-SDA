import uuid

from fastapi import FastAPI, HTTPException, Header, Query, Depends
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    age: int


class Track(BaseModel):
    name: str
    artist: str
    year: int | None = None
    genres: list[str] = []


token_to_user_mapping = {}
tracks: dict[int, Track] = {}


class TrackInfo(BaseModel):
    name: str
    artist: str


@app.post("/api/v1/registration/register_user", response_model=dict)
async def register_user(user: User) -> dict[str, str]:
    token = f"{uuid.uuid4()}{uuid.uuid4()}"[:40]
    token_to_user_mapping[token] = user
    return {"token": token}


async def get_user_from_token(x_token: str = Header(default=None)) -> User:
    token = x_token
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    if token not in token_to_user_mapping:
        raise HTTPException(status_code=401, detail="Incorrect token")

    return token_to_user_mapping[token]


@app.post("/api/v1/tracks/add_track", response_model=dict, status_code=201)
async def add_track(track: Track, user: User = Depends(get_user_from_token)) -> dict[str, int]:
    if len(tracks.items()) == 0:
        next_id = 1
    else:
        next_id = max(tracks.keys()) + 1
    track_info = {"track_id": next_id}
    tracks[next_id] = track
    return track_info


@app.delete("/api/v1/tracks/{track_id}", response_model=dict)
async def delete_track(track_id: int, user: User = Depends(get_user_from_token)) -> dict[str, str]:
    if track_id not in tracks:
        raise HTTPException(status_code=404, detail="Invalid track_id")
    tracks.pop(track_id)
    return {"status": "track removed"}


@app.get("/api/v1/tracks/all", response_model=list[Track])
async def view_all_tracks(user: User = Depends(get_user_from_token)) -> list[Track]:
    return list(tracks.values())


@app.get("/api/v1/tracks/search", response_model=dict)
async def search_tracks(name: str = Query(default=None), artist: str = Query(default=None),
                        user: User = Depends(get_user_from_token)) -> dict[str, list[int]]:
    if not name and not artist:
        raise HTTPException(status_code=422, detail="You should specify at least one search argument")

    result = []
    for trackId, track in tracks.items():
        if (not name or name == track.name) and (not artist or artist == track.artist):
            result.append(trackId)
    return {"track_ids": result}


@app.get("/api/v1/tracks/{track_id}", response_model=TrackInfo)
async def find_track(track_id: int, user: User = Depends(get_user_from_token)) -> TrackInfo:
    if track_id not in tracks:
        raise HTTPException(status_code=404, detail="Invalid track_id")

    track = tracks[track_id]
    return TrackInfo(name=track.name, artist=track.artist)
