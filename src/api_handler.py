from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from classifier import classify_query

app = FastAPI(
    title="KBLI Agent MVP",
    description="API minimal untuk klasifikasi KBLI dari teks deskriptif usaha",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"message": "KBLI Agent API aktif. Gunakan endpoint /classify?query=..."}

@app.get("/classify")
def classify(query: str = Query(..., description="Deskripsi usaha atau pekerjaan")):
    try:
        result = classify_query(query)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

# Untuk testing langsung dari terminal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_handler:app", host="0.0.0.0", port=8000, reload=True)
