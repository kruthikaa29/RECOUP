from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil

from backend.agent import analyze_bill_image

app = FastAPI(title="Recoup API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    return {
        "project": "Recoup",
        "message": "AI Medical Bill Advocate is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/upload-bill")
async def upload_bill(file: UploadFile = File(...)):

    allowed_types = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if file.content_type not in allowed_types:
        return {
            "success": False,
            "message": "Please upload a PDF or image file."
        }

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        if file.content_type.startswith("image/"):

            raw_analysis = analyze_bill_image(
                str(file_path)
            )

            bill_analysis = {}

            if isinstance(raw_analysis, dict):
                bill_analysis = raw_analysis.get(
                    "bill_analysis",
                    {}
                )

            extracted = {}

            if isinstance(bill_analysis, dict):
                extracted = (
                    bill_analysis.get("extracted_information")
                    or bill_analysis.get("extracted_bill_information")
                    or bill_analysis.get("bill_information")
                    or {}
                )

            analysis_section = {}

            if isinstance(bill_analysis, dict):
                analysis_section = (
                    bill_analysis.get("analysis")
                    or {}
                )

            benchmark_results = []

            if isinstance(raw_analysis, dict):
                benchmark_results = raw_analysis.get(
                    "benchmark_results",
                    []
                )

            coding_audit = {}

            if isinstance(raw_analysis, dict):
                coding_audit = raw_analysis.get(
                    "coding_audit",
                    {}
                )

            negotiation_letter = ""

            if isinstance(raw_analysis, dict):
                negotiation_letter = raw_analysis.get(
                    "negotiation_letter",
                    ""
                )

            final_response = {
                "success": True,
                "message": "Medical bill uploaded and analyzed successfully!",
                "filename": file.filename,
                "file_type": file.content_type,
                "bill": extracted,
                "analysis": analysis_section,
                "benchmark_results": benchmark_results,
                "coding_audit": coding_audit,
                "negotiation_letter": negotiation_letter
            }

            print("\n========== FINAL FRONTEND RESPONSE ==========\n")
            print(final_response)

            return final_response

        else:

            return {
                "success": True,
                "message": "PDF uploaded successfully. PDF analysis will be added next.",
                "filename": file.filename,
                "file_type": file.content_type
            }

    except Exception as e:

        print("\n========== ANALYSIS ERROR ==========\n")
        print(str(e))

        return {
            "success": False,
            "message": "Bill uploaded, but AI analysis failed.",
            "filename": file.filename,
            "error": str(e)
        }