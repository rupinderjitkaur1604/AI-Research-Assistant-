import os
import shutil


from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse


router = APIRouter()


UPLOAD_DIR    = "uploads"
FAISS_DIR     = "faiss_indexes"


os.makedirs(UPLOAD_DIR, exist_ok=True)




@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)


    # ✅ Skip re-upload if file already exists
    if os.path.exists(file_path):
        return {
            "filename": file.filename,
            "file_path": file_path,
            "message": f"'{file.filename}' already exists. Ready to use!"
        }


    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)


    return {
        "filename": file.filename,
        "file_path": file_path,
        "message": f"'{file.filename}' uploaded successfully!"
    }




@router.get("/pdfs")
async def list_pdfs():
    """Return list of all uploaded PDFs."""
    if not os.path.exists(UPLOAD_DIR):
        return {"pdfs": []}


    files = [
        f for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".pdf")
    ]


    return {"pdfs": files}




@router.delete("/pdfs/{filename}")
async def delete_pdf(filename: str):
    """Delete a PDF and its FAISS index."""


    file_path = os.path.join(UPLOAD_DIR, filename)
    index_path = os.path.join(FAISS_DIR, os.path.splitext(filename)[0])


    deleted = []


    # Delete PDF file
    if os.path.exists(file_path):
        os.remove(file_path)
        deleted.append("pdf")


    # Delete FAISS index folder
    if os.path.exists(index_path):
        shutil.rmtree(index_path)
        deleted.append("faiss_index")


    if not deleted:
        return JSONResponse(status_code=404, content={"error": f"'{filename}' not found."})


    return {"message": f"'{filename}' deleted successfully.", "deleted": deleted}


