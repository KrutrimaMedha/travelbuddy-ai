import { cn } from '@/utils/cn'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  message?: string
  progress?: number
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12'
}

export function LoadingSpinner({ size = 'md', className, message, progress }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center gap-4">
      {/* Spinner */}
      <div className={cn('animate-spin', sizeClasses[size], className)}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          className="h-full w-full"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>

      {/* Progress bar */}
      {progress !== undefined && (
        <div className="w-full max-w-xs">
          <div className="mb-2 flex justify-between text-sm">
            <span className="text-muted-foreground">Processing...</span>
            <span className="text-muted-foreground">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-secondary">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-primary to-primary/80 transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Loading message */}
      {message && (
        <p className="text-sm text-muted-foreground animate-pulse text-center">
          {message}
        </p>
      )}
    </div>
  )
}

export function FullPageLoader({ message, progress }: { message?: string; progress?: number }) {
  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-card p-8 rounded-xl shadow-lg border max-w-md w-full mx-4">
        <LoadingSpinner size="xl" message={message} progress={progress} />
      </div>
    </div>
  )
}