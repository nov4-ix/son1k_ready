"""
Son1kVers3 User Accounts and Revenue Tracking System
Integrated with the existing FastAPI main_production.py
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum
import json
import os

# Data Models for the tracking system
class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Currency(str, Enum):
    MXN = "MXN"
    USD = "USD"

class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    MERCADOPAGO = "mercadopago"
    MANUAL = "manual"

class User(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime
    accounts: List['Account'] = []

class Account(BaseModel):
    id: str
    user_id: str
    plan: PlanType
    status: str = "active"
    created_at: datetime
    transactions: List['Transaction'] = []

class Transaction(BaseModel):
    id: str
    account_id: str
    source: str  # "plan" | "store" | "music_generation"
    amount: int  # in centavos
    currency: Currency
    description: Optional[str] = None
    provider_ref: Optional[str] = None
    created_at: datetime

class PayoutAccount(BaseModel):
    id: str
    name: str
    provider: PaymentProvider
    config: Dict
    active: bool = False
    created_at: datetime

class Settings(BaseModel):
    active_payout_account_id: Optional[str] = None

# Request/Response Models
class CreateAccountRequest(BaseModel):
    email: str
    full_name: str
    plan: PlanType

class CreateTransactionRequest(BaseModel):
    account_id: str
    source: str
    amount: int
    currency: Currency
    description: Optional[str] = None
    provider_ref: Optional[str] = None

class CreatePayoutAccountRequest(BaseModel):
    name: str
    provider: PaymentProvider
    config: Dict
    active: bool = False

class SelectPayoutAccountRequest(BaseModel):
    payout_account_id: str

# In-memory storage (replace with real database in production)
class TrackerStorage:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.accounts: Dict[str, Account] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.payout_accounts: Dict[str, PayoutAccount] = {}
        self.settings: Settings = Settings()
        
        # Load from file if exists
        self.load_data()
    
    def save_data(self):
        """Save data to JSON file for persistence"""
        data = {
            "users": {k: v.dict() for k, v in self.users.items()},
            "accounts": {k: v.dict() for k, v in self.accounts.items()},
            "transactions": {k: v.dict() for k, v in self.transactions.items()},
            "payout_accounts": {k: v.dict() for k, v in self.payout_accounts.items()},
            "settings": self.settings.dict()
        }
        with open("tracker_data.json", "w") as f:
            json.dump(data, f, default=str, indent=2)
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists("tracker_data.json"):
                with open("tracker_data.json", "r") as f:
                    data = json.load(f)
                
                # Convert back to models
                for k, v in data.get("users", {}).items():
                    v["created_at"] = datetime.fromisoformat(v["created_at"])
                    self.users[k] = User(**v)
                
                for k, v in data.get("accounts", {}).items():
                    v["created_at"] = datetime.fromisoformat(v["created_at"])
                    self.accounts[k] = Account(**v)
                
                for k, v in data.get("transactions", {}).items():
                    v["created_at"] = datetime.fromisoformat(v["created_at"])
                    self.transactions[k] = Transaction(**v)
                
                for k, v in data.get("payout_accounts", {}).items():
                    v["created_at"] = datetime.fromisoformat(v["created_at"])
                    self.payout_accounts[k] = PayoutAccount(**v)
                
                if "settings" in data:
                    self.settings = Settings(**data["settings"])
        except Exception as e:
            print(f"Error loading tracker data: {e}")

# Global storage instance
tracker_storage = TrackerStorage()

# Business Logic Functions
def generate_id() -> str:
    """Generate unique ID"""
    import uuid
    return str(uuid.uuid4())

def create_user_account(email: str, full_name: str, plan: PlanType) -> Dict:
    """Create or update user and create new account"""
    # Check if user exists
    existing_user = None
    for user in tracker_storage.users.values():
        if user.email == email:
            existing_user = user
            break
    
    if existing_user:
        user = existing_user
        # Update full name
        user.full_name = full_name
    else:
        # Create new user
        user_id = generate_id()
        user = User(
            id=user_id,
            email=email,
            full_name=full_name,
            created_at=datetime.now()
        )
        tracker_storage.users[user_id] = user
    
    # Create new account
    account_id = generate_id()
    account = Account(
        id=account_id,
        user_id=user.id,
        plan=plan,
        created_at=datetime.now()
    )
    tracker_storage.accounts[account_id] = account
    
    # Save data
    tracker_storage.save_data()
    
    return {
        "user": user.dict(),
        "account": account.dict()
    }

def create_transaction(account_id: str, source: str, amount: int, currency: Currency, 
                      description: Optional[str] = None, provider_ref: Optional[str] = None) -> Transaction:
    """Create new transaction"""
    if account_id not in tracker_storage.accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transaction_id = generate_id()
    transaction = Transaction(
        id=transaction_id,
        account_id=account_id,
        source=source,
        amount=amount,
        currency=currency,
        description=description,
        provider_ref=provider_ref,
        created_at=datetime.now()
    )
    
    tracker_storage.transactions[transaction_id] = transaction
    tracker_storage.save_data()
    
    return transaction

def get_stats() -> Dict:
    """Get summary statistics"""
    # Count accounts by plan
    by_plan = {}
    for account in tracker_storage.accounts.values():
        by_plan[account.plan] = by_plan.get(account.plan, 0) + 1
    
    # Total revenue
    total_revenue_cents = sum(tx.amount for tx in tracker_storage.transactions.values())
    
    # Revenue by source
    revenue_by_source = {}
    for tx in tracker_storage.transactions.values():
        revenue_by_source[tx.source] = revenue_by_source.get(tx.source, 0) + tx.amount
    
    return {
        "by_plan": [{"plan": k, "_count": {"plan": v}} for k, v in by_plan.items()],
        "total_revenue_cents": total_revenue_cents,
        "revenue_by_source": [{"source": k, "_sum": {"amount": v}} for k, v in revenue_by_source.items()]
    }

def create_payout_account(name: str, provider: PaymentProvider, config: Dict, active: bool = False) -> PayoutAccount:
    """Create new payout account"""
    payout_id = generate_id()
    payout_account = PayoutAccount(
        id=payout_id,
        name=name,
        provider=provider,
        config=config,
        active=active,
        created_at=datetime.now()
    )
    
    tracker_storage.payout_accounts[payout_id] = payout_account
    tracker_storage.save_data()
    
    return payout_account

def select_payout_account(payout_account_id: str) -> bool:
    """Select active payout account"""
    if payout_account_id not in tracker_storage.payout_accounts:
        raise HTTPException(status_code=404, detail="Payout account not found")
    
    # Deactivate all others
    for payout in tracker_storage.payout_accounts.values():
        payout.active = False
    
    # Activate selected one
    tracker_storage.payout_accounts[payout_account_id].active = True
    tracker_storage.settings.active_payout_account_id = payout_account_id
    
    tracker_storage.save_data()
    return True

def get_active_payout_account() -> Optional[PayoutAccount]:
    """Get currently active payout account"""
    if tracker_storage.settings.active_payout_account_id:
        return tracker_storage.payout_accounts.get(tracker_storage.settings.active_payout_account_id)
    return None

# Payment Router
def route_payment(amount: int, currency: Currency, meta: Dict = None) -> Dict:
    """Route payment to active payout account"""
    active_payout = get_active_payout_account()
    if not active_payout:
        raise HTTPException(status_code=400, detail="No active payout account configured")
    
    if active_payout.provider == PaymentProvider.STRIPE:
        # Simulate Stripe payment intent
        return {
            "provider": "stripe",
            "payment_intent_id": f"pi_{generate_id()[:10]}",
            "amount": amount,
            "currency": currency.lower(),
            "destination_account": active_payout.config.get("account_id"),
            "simulated": True
        }
    
    elif active_payout.provider == PaymentProvider.MERCADOPAGO:
        # Simulate MercadoPago preference
        return {
            "provider": "mercadopago",
            "preference_id": f"mp_{generate_id()[:10]}",
            "amount": amount,
            "currency": currency,
            "collector_id": active_payout.config.get("collector_id"),
            "simulated": True
        }
    
    else:  # MANUAL
        return {
            "provider": "manual",
            "instructions": active_payout.config.get("instructions", "Manual payment instructions"),
            "amount": amount,
            "currency": currency,
            "simulated": True
        }

# Integration with existing user limits system
def track_music_generation(user_plan: str, amount_charged: int = 0) -> str:
    """Track music generation as transaction"""
    # Find or create account for this plan
    account_id = None
    for account in tracker_storage.accounts.values():
        if account.plan == user_plan:
            account_id = account.id
            break
    
    if not account_id:
        # Create anonymous account for tracking
        result = create_user_account(
            email=f"anonymous_{user_plan}@son1kvers3.com",
            full_name=f"Anonymous {user_plan.title()} User",
            plan=PlanType(user_plan)
        )
        account_id = result["account"]["id"]
    
    # Create transaction
    transaction = create_transaction(
        account_id=account_id,
        source="music_generation",
        amount=amount_charged,
        currency=Currency.USD,
        description=f"Music generation - {user_plan} plan"
    )
    
    return transaction.id