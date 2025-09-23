#!/usr/bin/env python3
"""
🏦 SON1KVERS3 FINANCIAL MANAGER
Herramienta de gestión financiera completa para Son1kVers3
Manejo de cuentas bancarias, activos, ingresos y gastos
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class BankAccount:
    id: str
    name: str
    bank_name: str
    account_number: str
    account_type: str  # 'checking', 'savings', 'business'
    balance: float
    currency: str = 'USD'
    is_active: bool = True
    created_at: datetime = None

@dataclass
class Transaction:
    id: str
    account_id: str
    type: str  # 'income', 'expense', 'transfer'
    category: str
    amount: float
    description: str
    date: datetime
    reference: Optional[str] = None

@dataclass
class Asset:
    id: str
    name: str
    type: str  # 'equipment', 'software', 'domain', 'server', 'other'
    value: float
    purchase_date: datetime
    depreciation_rate: float = 0.0
    notes: str = ""

class FinancialManager:
    def __init__(self, db_path: str = "son1k_financial.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Inicializa la base de datos financiera"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de cuentas bancarias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                bank_name TEXT NOT NULL,
                account_number TEXT NOT NULL,
                account_type TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0.0,
                currency TEXT DEFAULT 'USD',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de transacciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                date TIMESTAMP NOT NULL,
                reference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES bank_accounts (id)
            )
        """)
        
        # Tabla de activos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                value REAL NOT NULL,
                purchase_date TIMESTAMP NOT NULL,
                depreciation_rate REAL DEFAULT 0.0,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de configuración
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("🏦 Base de datos financiera inicializada")
    
    def add_bank_account(self, name: str, bank_name: str, account_number: str, 
                        account_type: str, initial_balance: float = 0.0) -> str:
        """Agrega una nueva cuenta bancaria"""
        account_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bank_accounts (id, name, bank_name, account_number, account_type, balance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (account_id, name, bank_name, account_number, account_type, initial_balance))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💳 Cuenta bancaria agregada: {name} - {bank_name}")
        return account_id
    
    def add_transaction(self, account_id: str, transaction_type: str, category: str,
                       amount: float, description: str, date: datetime = None, 
                       reference: str = None) -> str:
        """Agrega una nueva transacción"""
        if date is None:
            date = datetime.now()
            
        transaction_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insertar transacción
        cursor.execute("""
            INSERT INTO transactions (id, account_id, type, category, amount, description, date, reference)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (transaction_id, account_id, transaction_type, category, amount, description, date, reference))
        
        # Actualizar balance de la cuenta
        if transaction_type == 'income':
            cursor.execute("UPDATE bank_accounts SET balance = balance + ? WHERE id = ?", (amount, account_id))
        elif transaction_type == 'expense':
            cursor.execute("UPDATE bank_accounts SET balance = balance - ? WHERE id = ?", (amount, account_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💰 Transacción agregada: {transaction_type} ${amount} - {description}")
        return transaction_id
    
    def add_asset(self, name: str, asset_type: str, value: float, 
                 purchase_date: datetime = None, depreciation_rate: float = 0.0, 
                 notes: str = "") -> str:
        """Agrega un nuevo activo"""
        if purchase_date is None:
            purchase_date = datetime.now()
            
        asset_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO assets (id, name, type, value, purchase_date, depreciation_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (asset_id, name, asset_type, value, purchase_date, depreciation_rate, notes))
        
        conn.commit()
        conn.close()
        
        logger.info(f"🏗️ Activo agregado: {name} - ${value}")
        return asset_id
    
    def get_financial_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen financiero completo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total en cuentas bancarias
        cursor.execute("SELECT SUM(balance) FROM bank_accounts WHERE is_active = 1")
        total_cash = cursor.fetchone()[0] or 0.0
        
        # Total en activos
        cursor.execute("SELECT SUM(value) FROM assets")
        total_assets = cursor.fetchone()[0] or 0.0
        
        # Ingresos del mes actual
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE type = 'income' AND date >= ?
        """, (start_of_month,))
        monthly_income = cursor.fetchone()[0] or 0.0
        
        # Gastos del mes actual
        cursor.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE type = 'expense' AND date >= ?
        """, (start_of_month,))
        monthly_expenses = cursor.fetchone()[0] or 0.0
        
        # Cuentas bancarias
        cursor.execute("""
            SELECT name, bank_name, balance, currency FROM bank_accounts 
            WHERE is_active = 1 ORDER BY balance DESC
        """)
        accounts = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_cash": total_cash,
            "total_assets": total_assets,
            "net_worth": total_cash + total_assets,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_profit": monthly_income - monthly_expenses,
            "accounts": [
                {
                    "name": acc[0],
                    "bank": acc[1],
                    "balance": acc[2],
                    "currency": acc[3]
                } for acc in accounts
            ]
        }
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene las transacciones más recientes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.type, t.category, t.amount, t.description, t.date, ba.name
            FROM transactions t
            JOIN bank_accounts ba ON t.account_id = ba.id
            ORDER BY t.date DESC
            LIMIT ?
        """, (limit,))
        
        transactions = cursor.fetchall()
        conn.close()
        
        return [
            {
                "type": tx[0],
                "category": tx[1],
                "amount": tx[2],
                "description": tx[3],
                "date": tx[4],
                "account": tx[5]
            } for tx in transactions
        ]
    
    def initialize_son1k_accounts(self):
        """Inicializa las cuentas específicas de Son1kVers3"""
        # Cuenta principal de negocios
        business_id = self.add_bank_account(
            name="Son1kVers3 Business",
            bank_name="Business Bank",
            account_number="****1234",
            account_type="business",
            initial_balance=0.0
        )
        
        # Cuenta de desarrollo
        dev_id = self.add_bank_account(
            name="Development Fund",
            bank_name="Tech Bank",
            account_number="****5678",
            account_type="savings",
            initial_balance=0.0
        )
        
        # Agregar activos iniciales
        self.add_asset(
            name="son1kvers3.com Domain",
            asset_type="domain",
            value=50.0,
            notes="Dominio principal de la plataforma"
        )
        
        self.add_asset(
            name="Railway Hosting",
            asset_type="server",
            value=20.0,
            notes="Hosting mensual en Railway"
        )
        
        self.add_asset(
            name="Development Equipment",
            asset_type="equipment",
            value=2000.0,
            depreciation_rate=0.20,
            notes="Equipos de desarrollo y producción"
        )
        
        logger.info("🚀 Cuentas de Son1kVers3 inicializadas")
        return {"business_account": business_id, "dev_account": dev_id}

def main():
    """Función principal para demostrar el uso"""
    logging.basicConfig(level=logging.INFO)
    
    fm = FinancialManager()
    
    # Inicializar cuentas de Son1kVers3
    accounts = fm.initialize_son1k_accounts()
    
    # Agregar algunas transacciones de ejemplo
    fm.add_transaction(
        account_id=accounts["business_account"],
        transaction_type="income",
        category="subscriptions",
        amount=99.0,
        description="Suscripción Pro mensual - Usuario1"
    )
    
    fm.add_transaction(
        account_id=accounts["business_account"],
        transaction_type="expense",
        category="hosting",
        amount=20.0,
        description="Railway hosting mensual"
    )
    
    # Mostrar resumen
    summary = fm.get_financial_summary()
    print("\n🏦 RESUMEN FINANCIERO SON1KVERS3")
    print("=" * 40)
    print(f"💰 Efectivo total: ${summary['total_cash']:.2f}")
    print(f"🏗️ Activos totales: ${summary['total_assets']:.2f}")
    print(f"💎 Valor neto: ${summary['net_worth']:.2f}")
    print(f"📈 Ingresos del mes: ${summary['monthly_income']:.2f}")
    print(f"📉 Gastos del mes: ${summary['monthly_expenses']:.2f}")
    print(f"💡 Ganancia del mes: ${summary['monthly_profit']:.2f}")
    
    print("\n💳 CUENTAS BANCARIAS:")
    for acc in summary['accounts']:
        print(f"  • {acc['name']} ({acc['bank']}): ${acc['balance']:.2f} {acc['currency']}")
    
    print("\n📋 TRANSACCIONES RECIENTES:")
    recent = fm.get_recent_transactions(5)
    for tx in recent:
        symbol = "+" if tx['type'] == 'income' else "-"
        print(f"  {symbol}${tx['amount']:.2f} | {tx['category']} | {tx['description']}")

if __name__ == "__main__":
    main()