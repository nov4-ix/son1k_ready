import React, { useEffect, useState } from 'react'

type Stats = {
  by_plan: { plan: 'free'|'pro'|'enterprise'; _count: { plan:number } }[]
  total_revenue_cents: number
  revenue_by_source: { source: string; _sum:{ amount:number|null } }[]
}

type PayoutAccount = {
  id: string
  name: string
  provider: 'stripe'|'mercadopago'|'manual'
  active: boolean
}

type Transaction = {
  id: string
  source: string
  amount: number
  currency: string
  description: string
  created_at: string
}

type DashboardData = {
  stats: Stats
  active_payout_account: PayoutAccount | null
  recent_transactions: Transaction[]
  user_count: number
  account_count: number
  last_updated: string
}

const API_BASE = process.env.NEXT_PUBLIC_SON1K_API_URL || 'https://son1kvers3.com'

export default function Son1kTrackerWidget() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function fetchDashboardData(){
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/api/tracker/dashboard`, {
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      const data = await response.json()
      setDashboardData(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading && !dashboardData) {
    return (
      <div className="p-6 border border-white/10 rounded-2xl bg-zinc-950/50 backdrop-blur-xl">
        <div className="animate-pulse">
          <div className="h-6 bg-white/10 rounded mb-4"></div>
          <div className="grid grid-cols-3 gap-4 mb-6">
            {[1,2,3].map(i => (
              <div key={i} className="h-20 bg-white/10 rounded"></div>
            ))}
          </div>
          <div className="h-24 bg-white/10 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 border border-red-500/20 rounded-2xl bg-red-950/20 text-red-300">
        <h3 className="font-semibold mb-2">Error loading dashboard</h3>
        <p className="text-sm">{error}</p>
        <button 
          onClick={fetchDashboardData}
          className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition"
        >
          Retry
        </button>
      </div>
    )
  }

  if (!dashboardData) return null

  const { stats, active_payout_account, recent_transactions, user_count, account_count } = dashboardData

  const getPlanCount = (plan: 'free'|'pro'|'enterprise') => 
    stats.by_plan.find(x => x.plan === plan)?._count.plan || 0

  const formatCurrency = (cents: number, currency = 'USD') => {
    const amount = (cents || 0) / 100
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: currency 
    }).format(amount)
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="p-6 border border-white/10 rounded-2xl bg-zinc-950/50 backdrop-blur-xl shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-neon">Son1kVers3 Dashboard</h3>
          <p className="text-sm text-zinc-400">Revenue & User Analytics</p>
        </div>
        <div className="text-xs text-zinc-500">
          Last updated: {formatDate(dashboardData.last_updated)}
        </div>
      </div>

      {/* User Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <StatsCard label="Users" value={user_count} color="text-blue-400" />
        <StatsCard label="Accounts" value={account_count} color="text-green-400" />
        <StatsCard label="Free" value={getPlanCount('free')} color="text-zinc-400" />
        <StatsCard label="Pro" value={getPlanCount('pro')} color="text-neon" />
        <StatsCard label="Enterprise" value={getPlanCount('enterprise')} color="text-purple-400" />
      </div>

      {/* Revenue */}
      <div className="p-4 border border-white/10 rounded-xl mb-6">
        <div className="text-sm text-zinc-400 mb-2">Total Revenue</div>
        <div className="text-3xl font-bold text-neon">
          {formatCurrency(stats.total_revenue_cents)}
        </div>
        <div className="text-xs text-zinc-500 mt-2 flex flex-wrap gap-3">
          {stats.revenue_by_source.map(source => (
            <span key={source.source} className="flex items-center">
              <div className="w-2 h-2 bg-neon rounded-full mr-1"></div>
              {source.source}: {formatCurrency(source._sum.amount || 0)}
            </span>
          ))}
        </div>
      </div>

      {/* Active Payout */}
      <div className="p-4 border border-white/10 rounded-xl mb-6">
        <div className="text-sm text-zinc-400 mb-2">Active Payout Account</div>
        {active_payout_account ? (
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            <span className="font-medium">{active_payout_account.name}</span>
            <span className="ml-2 px-2 py-1 bg-white/10 rounded text-xs">
              {active_payout_account.provider.toUpperCase()}
            </span>
          </div>
        ) : (
          <div className="flex items-center text-zinc-500">
            <div className="w-3 h-3 bg-zinc-500 rounded-full mr-2"></div>
            No active payout account configured
          </div>
        )}
      </div>

      {/* Recent Transactions */}
      <div className="border border-white/10 rounded-xl">
        <div className="p-4 border-b border-white/10">
          <h4 className="font-semibold">Recent Transactions</h4>
        </div>
        <div className="max-h-64 overflow-y-auto">
          {recent_transactions.length === 0 ? (
            <div className="p-4 text-center text-zinc-500 text-sm">
              No transactions yet
            </div>
          ) : (
            <div className="space-y-1">
              {recent_transactions.map(tx => (
                <div key={tx.id} className="p-3 hover:bg-white/5 transition">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${
                        tx.source === 'music_generation' ? 'bg-neon' :
                        tx.source === 'store' ? 'bg-green-400' :
                        'bg-blue-400'
                      }`}></div>
                      <div>
                        <div className="text-sm font-medium">
                          {tx.description || tx.source}
                        </div>
                        <div className="text-xs text-zinc-500">
                          {formatDate(tx.created_at)}
                        </div>
                      </div>
                    </div>
                    <div className="text-sm font-mono">
                      {formatCurrency(tx.amount, tx.currency)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Refresh Button */}
      <div className="mt-4 text-center">
        <button 
          onClick={fetchDashboardData}
          disabled={loading}
          className="px-4 py-2 bg-neon/10 text-neon border border-neon rounded-lg text-sm hover:bg-neon/20 transition disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>
    </div>
  )
}

function StatsCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="p-4 border border-white/10 rounded-xl text-center">
      <div className="text-xs text-zinc-400 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
    </div>
  )
}

// Usage examples:

// 1. Create new account
export async function createAccount(email: string, fullName: string, plan: 'free'|'pro'|'enterprise') {
  const response = await fetch(`${API_BASE}/api/tracker/accounts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, full_name: fullName, plan })
  })
  return response.json()
}

// 2. Record transaction
export async function recordTransaction(accountId: string, source: string, amount: number, currency = 'USD', description?: string) {
  const response = await fetch(`${API_BASE}/api/tracker/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      account_id: accountId, 
      source, 
      amount, 
      currency, 
      description 
    })
  })
  return response.json()
}

// 3. Create payout account
export async function createPayoutAccount(name: string, provider: 'stripe'|'mercadopago'|'manual', config: any) {
  const response = await fetch(`${API_BASE}/api/tracker/payout-accounts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, provider, config, active: false })
  })
  return response.json()
}

// 4. Select active payout account
export async function selectPayoutAccount(payoutAccountId: string) {
  const response = await fetch(`${API_BASE}/api/tracker/payout/select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ payout_account_id: payoutAccountId })
  })
  return response.json()
}