from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from config import settings

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
    product_name: Optional[str] = None
    origin: Optional[str] = None
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
    """
    try:
        lots = db.query(Lot).offset(skip).limit(limit).all()
        return lots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lots: {str(e)}")


@app.get("/lots/{token_id}", response_model=LotResponse)
def get_lot(token_id: int, db: Session = Depends(get_db)):
    """
    Get specific lot details by token ID.
    """
    lot = db.query(Lot).filter(Lot.token_id == token_id).first()
    
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot {token_id} not found")
    
    return lot


@app.get("/lots/{token_id}/history", response_model=List[HistoryEntryResponse])
def get_lot_history(token_id: int, db: Session = Depends(get_db)):
    """
    Get complete audit trail for a lot.
    """
    # Check if lot exists
    lot = db.query(Lot).filter(Lot.token_id == token_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot {token_id} not found")
    
    # Get history entries ordered by timestamp
    history = db.query(HistoryEntry).filter(
        HistoryEntry.token_id == token_id
    ).order_by(HistoryEntry.timestamp.asc()).all()
    
    return history


@app.get("/recalls", response_model=List[RecallEventResponse])
def get_all_recalls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all recall events with pagination.
    """
    try:
        recalls = db.query(RecallEvent).order_by(
            RecallEvent.timestamp.desc()
        ).offset(skip).limit(limit).all()
        return recalls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recalls: {str(e)}")


@app.get("/lots/{token_id}/recalled")
def check_recall_status(token_id: int, db: Session = Depends(get_db)):
    """
    Check if a specific lot is recalled.
    """
    lot = db.query(Lot).filter(Lot.token_id == token_id).first()
    
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot {token_id} not found")
    
    return {
        "token_id": token_id,
        "is_recalled": lot.is_recalled,
        "status": lot.status
    }


@app.post("/upload", response_model=IPFSUploadResponse)
async def upload_to_ipfs(file: UploadFile = File(...)):
    """
    Upload a file to IPFS via Pinata.
    """
    import tempfile
    import os
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    
    try:
        # Write uploaded content to temp file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Upload to IPFS
        ipfs_hash = ipfs_service.upload_file(temp_file_path, file.filename)
        gateway_url = ipfs_service.get_file_url(ipfs_hash)
        
        return IPFSUploadResponse(
            ipfs_hash=ipfs_hash,
            gateway_url=gateway_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading to IPFS: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@app.post("/upload-json", response_model=IPFSUploadResponse)
def upload_json_to_ipfs(data: dict):
    """
    Upload JSON data to IPFS via Pinata.
    """
    try:
        ipfs_hash = ipfs_service.upload_json(data)
        gateway_url = ipfs_service.get_file_url(ipfs_hash)
        
        return IPFSUploadResponse(
            ipfs_hash=ipfs_hash,
            gateway_url=gateway_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading JSON to IPFS: {str(e)}")


@app.get("/blockchain/status")
def blockchain_status():
    """
    Check blockchain connection status and network info.
    """
    try:
        is_connected = blockchain_service.is_connected()
        
        if not is_connected:
            return {
                "connected": False,
                "message": "Not connected to blockchain"
            }
        
        latest_block = blockchain_service.get_latest_block_number()
        
        return {
            "connected": True,
            "contract_address": blockchain_service.contract_address,
            "latest_block": latest_block,
            "rpc_url": settings.POLYGON_AMOY_RPC_URL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking blockchain status: {str(e)}")


@app.get("/lots/owner/{address}", response_model=List[LotResponse])
def get_lots_by_owner(address: str, db: Session = Depends(get_db)):
    """
    Get all lots owned by a specific address.
    """
    # Basic Ethereum address validation
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
    
    try:
        lots = db.query(Lot).filter(Lot.owner_address == address).all()
        return lots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lots by owner: {str(e)}")


@app.get("/lots/status/{status}", response_model=List[LotResponse])
def get_lots_by_status(status: str, db: Session = Depends(get_db)):
    """
    Get all lots by status (Created, InTransit, OnShelf, Recalled).
    """
    valid_statuses = ["Created", "InTransit", "OnShelf", "Recalled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        lots = db.query(Lot).filter(Lot.status == status).all()
        return lots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lots by status: {str(e)}")


@app.get("/stats")
def get_statistics(db: Session = Depends(get_db)):
    """
    Get overall system statistics.
    """
    try:
        # Count total lots
        total_lots = db.query(Lot).count()
        
        # Count recalled lots
        recalled_lots = db.query(Lot).filter(Lot.is_recalled == True).count()
        
        # Count lots by status
        created_lots = db.query(Lot).filter(Lot.status == "Created").count()
        in_transit_lots = db.query(Lot).filter(Lot.status == "InTransit").count()
        on_shelf_lots = db.query(Lot).filter(Lot.status == "OnShelf").count()
        recalled_by_status = db.query(Lot).filter(Lot.status == "Recalled").count()
        
        # Count total history entries
        total_history_entries = db.query(HistoryEntry).count()
        
        # Count total recall events
        total_recall_events = db.query(RecallEvent).count()
        
        return {
            "total_lots": total_lots,
            "recalled_lots": recalled_lots,
            "lots_by_status": {
                "Created": created_lots,
                "InTransit": in_transit_lots,
                "OnShelf": on_shelf_lots,
                "Recalled": recalled_by_status
            },
            "total_history_entries": total_history_entries,
            "total_recall_events": total_recall_events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


@app.get("/ipfs/{ipfs_hash}")
def get_ipfs_content(ipfs_hash: str):
    """
    Retrieve content from IPFS by hash.
    """
    try:
        content = ipfs_service.get_content(ipfs_hash)
        return content
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error retrieving IPFS content: {str(e)}")


@app.get("/lots/{token_id}/blockchain")
def get_lot_from_blockchain(token_id: int):
    """
    Get lot details directly from blockchain (bypasses database).
    Useful for verification and debugging.
    """
    try:
        lot_details = blockchain_service.get_lot_details(token_id)
        return lot_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lot from blockchain: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
