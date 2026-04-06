import { useState, useEffect, createContext, useContext, useCallback } from 'react'
import { CheckCircle, AlertCircle, X, Info } from 'lucide-react'
import clsx from 'clsx'

const ToastContext = createContext(null)

export function useToast() {
  return useContext(ToastContext)
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'success', duration = 4000) => {
    const id = Date.now()
    setToasts((t) => [...t, { id, message, type }])
    if (duration > 0) {
      setTimeout(() => {
        setToasts((t) => t.filter((toast) => toast.id !== id))
      }, duration)
    }
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((t) => t.filter((toast) => toast.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={addToast}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

function ToastItem({ toast, onClose }) {
  const icons = {
    success: <CheckCircle size={16} className="text-emerald-500" />,
    error: <AlertCircle size={16} className="text-red-500" />,
    info: <Info size={16} className="text-blue-500" />,
  }
  const bgColors = {
    success: 'border-emerald-200 bg-emerald-50',
    error: 'border-red-200 bg-red-50',
    info: 'border-blue-200 bg-blue-50',
  }

  return (
    <div className={clsx('flex items-center gap-2 rounded-xl border px-4 py-3 shadow-elevated', bgColors[toast.type])}>
      {icons[toast.type]}
      <span className="text-sm text-surface-700">{toast.message}</span>
      <button onClick={onClose} className="ml-2 text-surface-400 hover:text-surface-600">
        <X size={14} />
      </button>
    </div>
  )
}
