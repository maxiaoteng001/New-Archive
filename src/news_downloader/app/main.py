from fastapi import Depends, FastAPI
import aioredis

from app.routers import articles

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    app.state.redis = await aioredis.from_url("redis://localhost", decode_responses=True)


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()


app.include_router(articles.router)
# app.include_router(items.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
