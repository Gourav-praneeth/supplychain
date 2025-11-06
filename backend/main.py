from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db, init_db, Lot, HistoryEntry, RecallEvent
from blockchain import blockchain_service
from ipfs_service import ipfs_service

app = FastAPI(title="FoodSafe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """
    PSEUDOCODE:
    1. Initialize database tables
    2. Verify blockchain connection
    3. Log startup information
    """
    init_db()
    print(f"Blockchain connected: {blockchain_service.is_connected()}")


class LotResponse(BaseModel):
    token_id: int
    owner_address: str
    status: str
    is_recalled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HistoryEntryResponse(BaseModel):
    id: int
    token_id: int
    timestamp: datetime
    stakeholder_address: str
    ipfs_hash: str
    event_type: str
    transaction_hash: str

    class Config:
        from_attributes = True


class RecallEventResponse(BaseModel):
    id: int
    token_id: int
    regulator_address: str
    timestamp: datetime
    transaction_hash: str

    class Config:
        from_attributes = True


class IPFSUploadResponse(BaseModel):
    ipfs_hash: str
    gateway_url: str


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "FoodSafe API"}


@app.get("/lots", response_model=List[LotResponse])
def get_all_lots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all lots with pagination.

    PSEUDOCODE:
    1. Query Lot table with offset (skip) and limit
    2. Return list of lots
    3. Handle database errors
    """
    pass


@app.get("/lots/{token_id}", response_model=LotResponse)
def get_lot(token_id: int, db: Session = Depends(get_db)):
    """
    Get specific lot details by token ID.

    PSEUDOCODE:
    1. Query database for lot with token_id
    2. If not found, raise 404 HTTPException
    3. Return lot details
    4. Optionally sync with blockchain for latest status
    """
    pass


@app.get("/lots/{token_id}/history", response_model=List[HistoryEntryResponse])
def get_lot_history(token_id: int, db: Session = Depends(get_db)):
    """
    Get complete audit trail for a lot.

    PSEUDOCODE:
    1. Query HistoryEntry table filtered by token_id
    2. Order by timestamp ascending
    3. Return list of history entries
    4. If lot doesn't exist, return 404
    """
    pass


@app.get("/recalls", response_model=List[RecallEventResponse])
def get_all_recalls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all recall events.

    PSEUDOCODE:
    1. Query RecallEvent table with pagination
    2. Order by timestamp descending (most recent first)
    3. Return list of recall events
    """
    pass


@app.get("/lots/{token_id}/recalled")
def check_recall_status(token_id: int, db: Session = Depends(get_db)):
    """
    Check if a specific lot is recalled.

    PSEUDOCODE:
    1. Query lot from database
    2. Return {"token_id": token_id, "is_recalled": lot.is_recalled}
    3. Optionally verify against blockchain as source of truth
    """
    pass


@app.post("/upload", response_model=IPFSUploadResponse)
async def upload_to_ipfs(file: UploadFile = File(...)):
    """
    Upload a file to IPFS via Pinata.

    PSEUDOCODE:
    1. Save uploaded file temporarily
    2. Call ipfs_service.upload_file(file_path)
    3. Get IPFS hash back
    4. Delete temporary file
    5. Return IPFS hash and gateway URL
    6. Handle upload errors
    """
    pass


@app.post("/upload-json", response_model=IPFSUploadResponse)
def upload_json_to_ipfs(data: dict):
    """
    Upload JSON data to IPFS.

    PSEUDOCODE:
    1. Validate JSON structure
    2. Call ipfs_service.upload_json(data)
    3. Return IPFS hash and gateway URL
    4. Handle errors
    """
    pass


@app.get("/blockchain/status")
def blockchain_status():
    """
    Check blockchain connection status.

    PSEUDOCODE:
    1. Call blockchain_service.is_connected()
    2. Get latest block number
    3. Return connection status and network info
    """
    pass


@app.get("/lots/owner/{address}", response_model=List[LotResponse])
def get_lots_by_owner(address: str, db: Session = Depends(get_db)):
    """
    Get all lots owned by a specific address.

    PSEUDOCODE:
    1. Validate Ethereum address format
    2. Query Lot table filtered by owner_address
    3. Return list of lots
    """
    pass


@app.get("/stats")
def get_statistics(db: Session = Depends(get_db)):
    """
    Get overall system statistics.

    PSEUDOCODE:
    1. Count total lots
    2. Count recalled lots
    3. Count lots by status (InTransit, OnShelf, Recalled)
    4. Count total history entries
    5. Return statistics object
    """
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
