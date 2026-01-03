from backend.db.database import Base, engine
from backend.models import (
    users_model,
    account_model,
    position_model,
    order_model,
    execution_model,
    symbol_model,
    cash_transaction_model,
    liquidation_event_model,
    market_price_model,
    account_activity_log_model,
    notification_model,
)

def reset_database():
    print("⚠️ Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("🛠 Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("✅ Database reset complete!")

if __name__ == "__main__":
    reset_database()
