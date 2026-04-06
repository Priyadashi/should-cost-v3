import clsx from 'clsx'

export default function FormField({ label, error, children, className }) {
  return (
    <div className={clsx('space-y-1', className)}>
      {label && (
        <label className="block text-[11px] font-semibold uppercase tracking-wider text-surface-400">
          {label}
        </label>
      )}
      {children}
      {error && <p className="text-[11px] text-red-500">{error}</p>}
    </div>
  )
}

export function Input({ className, ...props }) {
  return (
    <input
      className={clsx(
        'h-9 w-full rounded-lg border border-surface-200 bg-surface-50 px-3 text-sm text-surface-700',
        'outline-none placeholder:text-surface-400',
        'focus:border-brand-300 focus:ring-1 focus:ring-brand-200',
        className
      )}
      {...props}
    />
  )
}

export function Select({ className, children, ...props }) {
  return (
    <select
      className={clsx(
        'h-9 w-full rounded-lg border border-surface-200 bg-surface-50 px-3 text-sm text-surface-700',
        'outline-none focus:border-brand-300 focus:ring-1 focus:ring-brand-200',
        className
      )}
      {...props}
    >
      {children}
    </select>
  )
}

export function Textarea({ className, ...props }) {
  return (
    <textarea
      className={clsx(
        'w-full rounded-lg border border-surface-200 bg-surface-50 px-3 py-2 text-sm text-surface-700',
        'outline-none placeholder:text-surface-400',
        'focus:border-brand-300 focus:ring-1 focus:ring-brand-200',
        className
      )}
      {...props}
    />
  )
}
