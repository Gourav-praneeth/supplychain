import time
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, Lot, HistoryEntry, RecallEvent, init_db
from blockchain import blockchain_service
from config import settings


class EventIndexer:
    """
    Background service that listens to blockchain events and indexes them to PostgreSQL.
    """

    def __init__(self):
        """
        PSEUDOCODE:
        1. Initialize blockchain service connection
        2. Load last indexed block number from database or start from deployment block
        3. Set polling interval (e.g., 5 seconds)
        """
        self.blockchain = blockchain_service
        self.polling_interval = 5
        self.last_indexed_block = self._get_last_indexed_block()

    def _get_last_indexed_block(self) -> int:
        """
        Get the last block number that was indexed.

        PSEUDOCODE:
        1. Query database for the highest block_number in history_entries
        2. If no records exist, return contract deployment block or 0
        3. Return the block number
        """
        pass

    def _save_last_indexed_block(self, block_number: int):
        """
        Save the last indexed block number (could be in a separate metadata table).

        PSEUDOCODE:
        1. Update a metadata table with key="last_indexed_block", value=block_number
        2. Or simply track it based on latest entry in history_entries table
        """
        pass

    def index_transfer_events(self, from_block: int, to_block: int, db: Session):
        """
        Index ERC-721 Transfer events (lot ownership changes).

        PSEUDOCODE:
        1. Fetch Transfer events from blockchain between from_block and to_block
        2. For each Transfer event:
            a. Extract tokenId, from_address, to_address, transaction_hash, block_number
            b. Update or create Lot record in database
            c. Update owner_address field
            d. Create HistoryEntry with event_type="Transfer"
        3. Commit database transaction
        """
        pass

    def index_lot_recalled_events(self, from_block: int, to_block: int, db: Session):
        """
        Index LotRecalled events.

        PSEUDOCODE:
        1. Fetch LotRecalled events from blockchain
        2. For each LotRecalled event:
            a. Extract tokenId, regulator, timestamp, transaction_hash, block_number
            b. Update Lot.is_recalled = True
            c. Update Lot.status = "Recalled"
            d. Create RecallEvent record
            e. Create HistoryEntry with event_type="Recalled"
        3. Commit database transaction
        """
        pass

    def index_all_events(self, from_block: int, to_block: int):
        """
        Index all relevant events for a block range.

        PSEUDOCODE:
        1. Create database session
        2. Index Transfer events
        3. Index LotRecalled events
        4. Index any other custom events from FoodSafe contract
        5. Update last_indexed_block
        6. Commit and close session
        7. Handle errors and rollback if necessary
        """
        db = SessionLocal()
        try:
            self.index_transfer_events(from_block, to_block, db)
            self.index_lot_recalled_events(from_block, to_block, db)

            self._save_last_indexed_block(to_block)
            db.commit()
        except Exception as e:
            print(f"Error indexing events: {e}")
            db.rollback()
        finally:
            db.close()

    def run(self):
        """
        Main loop that continuously polls for new blocks and indexes events.

        PSEUDOCODE:
        1. Initialize database tables
        2. Print startup message
        3. Infinite loop:
            a. Get latest block number from blockchain
            b. If new blocks exist since last_indexed_block:
                i. Calculate from_block and to_block
                ii. Call index_all_events(from_block, to_block)
                iii. Update last_indexed_block
            c. Sleep for polling_interval seconds
            d. Handle interrupts (Ctrl+C) gracefully
        """
        print("Starting Event Indexer...")
        print(f"Connected to blockchain: {self.blockchain.is_connected()}")
        print(f"Starting from block: {self.last_indexed_block}")

        try:
            while True:
                latest_block = self.blockchain.get_latest_block_number()

                if latest_block > self.last_indexed_block:
                    from_block = self.last_indexed_block + 1
                    to_block = latest_block

                    print(f"Indexing blocks {from_block} to {to_block}")
                    self.index_all_events(from_block, to_block)
                    self.last_indexed_block = to_block

                time.sleep(self.polling_interval)
        except KeyboardInterrupt:
            print("\nIndexer stopped by user")
        except Exception as e:
            print(f"Indexer error: {e}")


if __name__ == "__main__":
    init_db()

    indexer = EventIndexer()
    indexer.run()
