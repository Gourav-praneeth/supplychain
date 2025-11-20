import time
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal, Lot, HistoryEntry, RecallEvent, init_db
from blockchain import blockchain_service
from config import settings


class EventIndexer:
    """
    Background service that listens to blockchain events and indexes them to PostgreSQL.
    """

    def __init__(self):
        """
        Initialize the event indexer with blockchain service and polling settings.
        """
        self.blockchain = blockchain_service
        self.polling_interval = 5  # seconds
        self.last_indexed_block = self._get_last_indexed_block()

    def _get_last_indexed_block(self) -> int:
        """
        Get the last block number that was indexed.
        Returns the highest block_number from history_entries or 0 if none exist.
        """
        db = SessionLocal()
        try:
            max_block = db.query(func.max(HistoryEntry.block_number)).scalar()
            if max_block is None:
                # Try recall events table as well
                max_recall_block = db.query(func.max(RecallEvent.block_number)).scalar()
                max_block = max_recall_block if max_recall_block else 0
            
            return max_block if max_block else 0
        except Exception as e:
            print(f"Error getting last indexed block: {e}")
            return 0
        finally:
            db.close()

    def _save_last_indexed_block(self, block_number: int):
        """
        The last indexed block is tracked implicitly via the block_number 
        field in history_entries and recall_events tables.
        """
        # This is tracked implicitly through the indexed events
        pass

    def index_lot_registered_events(self, from_block: int, to_block: int, db: Session):
        """
        Index LotRegistered events (lot creation/minting).
        """
        try:
            events = self.blockchain.get_event_logs('LotRegistered', from_block, to_block)
            
            for event in events:
                lot_id = event['args']['lotId']
                product_name = event['args']['productName']
                producer = event['args']['producer']
                tx_hash = event['transactionHash']
                block_number = event['blockNumber']
                
                # Check if lot already exists
                existing_lot = db.query(Lot).filter(Lot.token_id == lot_id).first()
                
                if not existing_lot:
                    # Create new lot
                    new_lot = Lot(
                        token_id=lot_id,
                        owner_address=producer,
                        status="Created",
                        is_recalled=False
                    )
                    db.add(new_lot)
                    
                    # Create history entry for registration
                    block_timestamp = self.blockchain.get_block_timestamp(block_number)
                    history_entry = HistoryEntry(
                        token_id=lot_id,
                        timestamp=block_timestamp,
                        stakeholder_address=producer,
                        ipfs_hash="",  # Will be filled from blockchain if available
                        event_type="LotRegistered",
                        transaction_hash=tx_hash,
                        block_number=block_number
                    )
                    db.add(history_entry)
                    
                    print(f"Indexed LotRegistered event for lot {lot_id}")
                    
        except Exception as e:
            print(f"Error indexing LotRegistered events: {e}")
            raise

    def index_transfer_events(self, from_block: int, to_block: int, db: Session):
        """
        Index ERC-721 Transfer events (lot ownership changes).
        """
        try:
            events = self.blockchain.get_event_logs('Transfer', from_block, to_block)
            
            for event in events:
                from_address = event['args']['from']
                to_address = event['args']['to']
                token_id = event['args']['tokenId']
                tx_hash = event['transactionHash']
                block_number = event['blockNumber']
                
                # Skip minting events (from zero address) - handled by LotRegistered
                if from_address == '0x0000000000000000000000000000000000000000':
                    continue
                
                # Update lot ownership
                lot = db.query(Lot).filter(Lot.token_id == token_id).first()
                if lot:
                    lot.owner_address = to_address
                    lot.updated_at = datetime.utcnow()
                else:
                    # Create lot if it doesn't exist (shouldn't happen normally)
                    lot = Lot(
                        token_id=token_id,
                        owner_address=to_address,
                        status="InTransit",
                        is_recalled=False
                    )
                    db.add(lot)
                
                # Create history entry for transfer
                block_timestamp = self.blockchain.get_block_timestamp(block_number)
                
                # Check if this history entry already exists
                existing_entry = db.query(HistoryEntry).filter(
                    HistoryEntry.transaction_hash == tx_hash
                ).first()
                
                if not existing_entry:
                    history_entry = HistoryEntry(
                        token_id=token_id,
                        timestamp=block_timestamp,
                        stakeholder_address=to_address,
                        ipfs_hash="",
                        event_type="Transfer",
                        transaction_hash=tx_hash,
                        block_number=block_number
                    )
                    db.add(history_entry)
                    print(f"Indexed Transfer event for lot {token_id}")
                    
        except Exception as e:
            print(f"Error indexing Transfer events: {e}")
            raise

    def index_lot_status_updated_events(self, from_block: int, to_block: int, db: Session):
        """
        Index LotStatusUpdated events.
        """
        try:
            events = self.blockchain.get_event_logs('LotStatusUpdated', from_block, to_block)
            
            for event in events:
                lot_id = event['args']['lotId']
                new_status = event['args']['newStatus']
                ipfs_hash = event['args']['ipfsHash']
                updater = event['args']['updater']
                tx_hash = event['transactionHash']
                block_number = event['blockNumber']
                
                # Map status enum to string
                status_map = {0: "Created", 1: "InTransit", 2: "OnShelf", 3: "Recalled"}
                status_str = status_map.get(new_status, "Unknown")
                
                # Update lot status
                lot = db.query(Lot).filter(Lot.token_id == lot_id).first()
                if lot:
                    lot.status = status_str
                    lot.owner_address = updater
                    lot.updated_at = datetime.utcnow()
                
                # Create history entry
                block_timestamp = self.blockchain.get_block_timestamp(block_number)
                
                # Check if this history entry already exists
                existing_entry = db.query(HistoryEntry).filter(
                    HistoryEntry.transaction_hash == tx_hash
                ).first()
                
                if not existing_entry:
                    history_entry = HistoryEntry(
                        token_id=lot_id,
                        timestamp=block_timestamp,
                        stakeholder_address=updater,
                        ipfs_hash=ipfs_hash,
                        event_type="LotStatusUpdated",
                        transaction_hash=tx_hash,
                        block_number=block_number
                    )
                    db.add(history_entry)
                    print(f"Indexed LotStatusUpdated event for lot {lot_id}")
                    
        except Exception as e:
            print(f"Error indexing LotStatusUpdated events: {e}")
            raise

    def index_lot_recalled_events(self, from_block: int, to_block: int, db: Session):
        """
        Index LotRecalled events.
        """
        try:
            events = self.blockchain.get_event_logs('LotRecalled', from_block, to_block)
            
            for event in events:
                lot_id = event['args']['lotId']
                regulator = event['args']['regulator']
                tx_hash = event['transactionHash']
                block_number = event['blockNumber']
                
                # Update lot to recalled status
                lot = db.query(Lot).filter(Lot.token_id == lot_id).first()
                if lot:
                    lot.is_recalled = True
                    lot.status = "Recalled"
                    lot.updated_at = datetime.utcnow()
                
                # Get block timestamp
                block_timestamp = self.blockchain.get_block_timestamp(block_number)
                
                # Check if this recall event already exists
                existing_recall = db.query(RecallEvent).filter(
                    RecallEvent.transaction_hash == tx_hash
                ).first()
                
                if not existing_recall:
                    # Create recall event record
                    recall_event = RecallEvent(
                        token_id=lot_id,
                        regulator_address=regulator,
                        timestamp=block_timestamp,
                        transaction_hash=tx_hash,
                        block_number=block_number
                    )
                    db.add(recall_event)
                    
                    # Create history entry for recall
                    history_entry = HistoryEntry(
                        token_id=lot_id,
                        timestamp=block_timestamp,
                        stakeholder_address=regulator,
                        ipfs_hash="RECALL_TRIGGERED",
                        event_type="LotRecalled",
                        transaction_hash=tx_hash,
                        block_number=block_number
                    )
                    db.add(history_entry)
                    
                    print(f"Indexed LotRecalled event for lot {lot_id}")
                    
        except Exception as e:
            print(f"Error indexing LotRecalled events: {e}")
            raise

    def index_all_events(self, from_block: int, to_block: int):
        """
        Index all relevant events for a block range.
        """
        db = SessionLocal()
        try:
            # Index all event types
            self.index_lot_registered_events(from_block, to_block, db)
            self.index_transfer_events(from_block, to_block, db)
            self.index_lot_status_updated_events(from_block, to_block, db)
            self.index_lot_recalled_events(from_block, to_block, db)

            self._save_last_indexed_block(to_block)
            db.commit()
            print(f"Successfully indexed blocks {from_block} to {to_block}")
            
        except Exception as e:
            print(f"Error indexing events: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def run(self):
        """
        Main loop that continuously polls for new blocks and indexes events.
        """
        print("=" * 60)
        print("Starting FoodSafe Event Indexer")
        print("=" * 60)
        print(f"Blockchain connected: {self.blockchain.is_connected()}")
        print(f"Contract address: {self.blockchain.contract_address}")
        print(f"Starting from block: {self.last_indexed_block}")
        print(f"Polling interval: {self.polling_interval} seconds")
        print("=" * 60)

        try:
            while True:
                try:
                    latest_block = self.blockchain.get_latest_block_number()

                    if latest_block > self.last_indexed_block:
                        from_block = self.last_indexed_block + 1
                        to_block = latest_block

                        print(f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Indexing blocks {from_block} to {to_block}")
                        self.index_all_events(from_block, to_block)
                        self.last_indexed_block = to_block
                    else:
                        print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] No new blocks. Latest: {latest_block}")

                    time.sleep(self.polling_interval)
                    
                except Exception as e:
                    print(f"Error in indexing loop: {e}")
                    print("Retrying in 10 seconds...")
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("Indexer stopped by user")
            print("=" * 60)
        except Exception as e:
            print(f"\nFatal indexer error: {e}")
            raise


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized.")
    
    indexer = EventIndexer()
    indexer.run()
