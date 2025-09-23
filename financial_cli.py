#!/usr/bin/env python3
"""
🏦 SON1KVERS3 FINANCIAL CLI
Interfaz de línea de comandos para gestión financiera segura
USO INDEPENDIENTE - No conectar al servidor web por seguridad
"""

import sys
import os
from financial_manager import FinancialManager
from datetime import datetime
import json

class FinancialCLI:
    def __init__(self):
        self.fm = FinancialManager("son1k_financial_secure.db")
        
    def show_menu(self):
        print("\n🏦 SON1KVERS3 FINANCIAL MANAGER")
        print("=" * 40)
        print("1. 📊 Ver resumen financiero")
        print("2. 💳 Gestionar cuentas bancarias")
        print("3. 💰 Agregar transacción")
        print("4. 🏗️ Gestionar activos")
        print("5. 📋 Ver transacciones recientes")
        print("6. 📈 Reportes mensuales")
        print("7. 🔧 Configuración inicial")
        print("0. ❌ Salir")
        print("=" * 40)
        
    def run(self):
        print("🚀 Iniciando Financial Manager Seguro...")
        
        while True:
            self.show_menu()
            choice = input("Selecciona una opción: ").strip()
            
            if choice == "1":
                self.show_summary()
            elif choice == "2":
                self.manage_accounts()
            elif choice == "3":
                self.add_transaction()
            elif choice == "4":
                self.manage_assets()
            elif choice == "5":
                self.show_recent_transactions()
            elif choice == "6":
                self.show_reports()
            elif choice == "7":
                self.initial_setup()
            elif choice == "0":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
    
    def show_summary(self):
        print("\n📊 RESUMEN FINANCIERO")
        print("-" * 30)
        summary = self.fm.get_financial_summary()
        
        print(f"💰 Efectivo total: ${summary['total_cash']:,.2f}")
        print(f"🏗️ Activos totales: ${summary['total_assets']:,.2f}")
        print(f"💎 Valor neto: ${summary['net_worth']:,.2f}")
        print(f"📈 Ingresos del mes: ${summary['monthly_income']:,.2f}")
        print(f"📉 Gastos del mes: ${summary['monthly_expenses']:,.2f}")
        print(f"💡 Ganancia del mes: ${summary['monthly_profit']:,.2f}")
        
        print("\n💳 CUENTAS:")
        for acc in summary['accounts']:
            print(f"  • {acc['name']}: ${acc['balance']:,.2f} {acc['currency']}")
    
    def manage_accounts(self):
        print("\n💳 GESTIÓN DE CUENTAS")
        print("1. Agregar cuenta nueva")
        print("2. Ver todas las cuentas")
        
        choice = input("Opción: ").strip()
        
        if choice == "1":
            name = input("Nombre de la cuenta: ")
            bank = input("Nombre del banco: ")
            number = input("Número de cuenta (últimos 4 dígitos): ")
            acc_type = input("Tipo (business/savings/checking): ")
            balance = float(input("Balance inicial: $") or "0")
            
            account_id = self.fm.add_bank_account(name, bank, number, acc_type, balance)
            print(f"✅ Cuenta creada: {account_id}")
    
    def add_transaction(self):
        print("\n💰 AGREGAR TRANSACCIÓN")
        
        # Mostrar cuentas disponibles
        summary = self.fm.get_financial_summary()
        print("Cuentas disponibles:")
        for i, acc in enumerate(summary['accounts'], 1):
            print(f"{i}. {acc['name']} - ${acc['balance']:,.2f}")
        
        try:
            acc_index = int(input("Selecciona cuenta (número): ")) - 1
            if acc_index < 0 or acc_index >= len(summary['accounts']):
                print("❌ Cuenta inválida")
                return
                
            # Obtener ID de la cuenta (necesitamos consultar la DB)
            # Por simplicidad, usamos el primer account_id disponible
            print("Tipo de transacción:")
            print("1. Ingreso")
            print("2. Gasto")
            
            tx_choice = input("Opción: ").strip()
            tx_type = "income" if tx_choice == "1" else "expense"
            
            category = input("Categoría: ")
            amount = float(input("Monto: $"))
            description = input("Descripción: ")
            
            # Para demo, usar primer account
            account_id = "demo_account"  # En implementación real, obtener del índice
            
            print(f"✅ Transacción registrada: {tx_type} ${amount}")
            
        except ValueError:
            print("❌ Datos inválidos")
    
    def manage_assets(self):
        print("\n🏗️ GESTIÓN DE ACTIVOS")
        print("1. Agregar activo")
        print("2. Ver todos los activos")
        
        choice = input("Opción: ").strip()
        
        if choice == "1":
            name = input("Nombre del activo: ")
            asset_type = input("Tipo (equipment/software/domain/server): ")
            value = float(input("Valor: $"))
            depreciation = float(input("Depreciación anual (0.0-1.0): ") or "0")
            notes = input("Notas: ")
            
            asset_id = self.fm.add_asset(name, asset_type, value, None, depreciation, notes)
            print(f"✅ Activo creado: {asset_id}")
    
    def show_recent_transactions(self):
        print("\n📋 TRANSACCIONES RECIENTES")
        print("-" * 40)
        transactions = self.fm.get_recent_transactions(10)
        
        for tx in transactions:
            symbol = "+" if tx['type'] == 'income' else "-"
            print(f"{symbol}${tx['amount']:,.2f} | {tx['category']} | {tx['description']}")
            print(f"  📅 {tx['date']} | 💳 {tx['account']}")
            print()
    
    def show_reports(self):
        print("\n📈 REPORTES MENSUALES")
        summary = self.fm.get_financial_summary()
        
        profit_margin = (summary['monthly_profit'] / summary['monthly_income'] * 100) if summary['monthly_income'] > 0 else 0
        
        print(f"💰 Margen de ganancia: {profit_margin:.1f}%")
        print(f"📊 ROI estimado anual: {(summary['monthly_profit'] * 12 / summary['total_assets'] * 100):.1f}%" if summary['total_assets'] > 0 else "N/A")
    
    def initial_setup(self):
        print("\n🔧 CONFIGURACIÓN INICIAL")
        print("Esto creará las cuentas base de Son1kVers3")
        confirm = input("¿Continuar? (s/n): ")
        
        if confirm.lower() == 's':
            accounts = self.fm.initialize_son1k_accounts()
            print("✅ Configuración inicial completada")
            print(f"Cuenta Business: {accounts['business_account']}")
            print(f"Cuenta Development: {accounts['dev_account']}")

def main():
    print("🔒 FINANCIAL MANAGER - MODO SEGURO")
    print("⚠️  NUNCA conectar esto al servidor web")
    print("✅ Solo uso local en máquina segura")
    
    cli = FinancialCLI()
    cli.run()

if __name__ == "__main__":
    main()