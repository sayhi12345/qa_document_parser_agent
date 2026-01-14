from fastapi import FastAPI
from routes import figma
from routes import confluence

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="Figma Parser Agent API")

app.include_router(figma.router, prefix="/figma", tags=["figma"])
app.include_router(confluence.router, prefix="/confluence", tags=["confluence"])

app.mount("/ui", StaticFiles(directory="web_ui"), name="ui")

@app.get("/")
async def read_root():
    return FileResponse('web_ui/index.html')

@app.get("/healthcheck")
async def health_check():
    return JSONResponse(content={"message": "ok"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
