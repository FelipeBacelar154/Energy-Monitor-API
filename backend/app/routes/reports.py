from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services import report_service
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

router = APIRouter()

class ReportRequest(BaseModel):
    chart_image: str | None = None

@router.post("/download")
def download_report(data: ReportRequest, db: Session = Depends(get_db)):
    try:
        pdf_path = report_service.generate_pdf(
            db,
            chart_image=data.chart_image
        )

        return FileResponse(
            path=pdf_path,
            filename=os.path.basename(pdf_path),
            media_type="application/pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))