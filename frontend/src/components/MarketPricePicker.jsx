import { useState } from 'react'
import { fetchCommodityPrices } from '../api/commodityPrices'

/**
 * A button that fetches live commodity prices for the given materialType
 * and lets the user select one to populate a rate_per_kg field.
 *
 * Props:
 *   materialType  — e.g. "Copper", "Steel"
 *   onSelect(price) — called with the chosen INR/kg value (number)
 */
export default function MarketPricePicker({ materialType, onSelect }) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [prices, setPrices] = useState(null)
  const [error, setError] = useState(null)

  const handleOpen = async () => {
    if (!materialType) return
    setOpen(true)
    setLoading(true)
    setError(null)
    setPrices(null)
    try {
      const data = await fetchCommodityPrices(materialType)
      setPrices(data.prices || [])
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to fetch market prices')
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (price) => {
    onSelect(price.price_inr_per_kg)
    setOpen(false)
  }

  return (
    <>
      <button
        type="button"
        onClick={handleOpen}
        title="Fetch live market price"
        className="ml-1 flex h-9 items-center gap-1 rounded-lg border border-brand-200 bg-brand-50 px-2 text-xs font-semibold text-brand-600 hover:bg-brand-100 whitespace-nowrap"
      >
        <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z" clipRule="evenodd" />
        </svg>
        Live Price
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          onClick={() => setOpen(false)}
        >
          <div
            className="w-full max-w-md rounded-xl bg-white shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-surface-100 px-5 py-4">
              <div>
                <h3 className="text-sm font-semibold text-surface-800">Live Market Prices</h3>
                <p className="text-xs text-surface-400 mt-0.5">
                  {materialType} &middot; All prices in INR/kg
                </p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="rounded-md p-1 text-surface-400 hover:bg-surface-100"
              >
                <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            {/* Body */}
            <div className="px-5 py-4">
              {loading && (
                <div className="flex items-center justify-center py-8 text-sm text-surface-400">
                  <svg className="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Fetching live prices...
                </div>
              )}

              {error && (
                <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
                  {error}
                </div>
              )}

              {prices && prices.length === 0 && !loading && (
                <p className="py-6 text-center text-sm text-surface-400">
                  No market price data available for {materialType}.
                </p>
              )}

              {prices && prices.length > 0 && (
                <div className="space-y-2">
                  {prices.map((p, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => handleSelect(p)}
                      className="w-full rounded-lg border border-surface-200 bg-surface-50 px-4 py-3 text-left hover:border-brand-300 hover:bg-brand-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-sm font-semibold text-surface-800">
                            {p.commodity}
                          </span>
                          <span className="ml-2 rounded-full bg-surface-200 px-2 py-0.5 text-[10px] font-medium text-surface-500">
                            {p.exchange}
                          </span>
                        </div>
                        <span className="font-mono text-base font-bold text-brand-600">
                          ₹{p.price_inr_per_kg.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                          <span className="ml-1 text-xs font-normal text-surface-400">/kg</span>
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-3 text-[11px] text-surface-400">
                        <span>
                          <span className="font-medium">Source:</span>{' '}
                          <a
                            href={p.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-brand-500 hover:underline"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {p.source_ticker}
                          </a>
                        </span>
                        <span>&middot;</span>
                        <span>{p.fetched_at.replace('T', ' ').replace('Z', ' UTC')}</span>
                      </div>
                      {p.conversion_note && p.conversion_note !== 'INR/kg' && (
                        <p className="mt-0.5 text-[10px] text-surface-400 italic">
                          {p.conversion_note}
                        </p>
                      )}
                    </button>
                  ))}
                  <p className="pt-1 text-center text-[10px] text-surface-300">
                    Click a price to apply it to the rate field
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
