import { HTMLAttributes, forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/utils/cn'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold tracking-wide transition-colors focus:outline-none focus:ring-2 focus:ring-emt-blue-light focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-emt-blue text-white shadow hover:bg-emt-blue-dark',
        secondary: 'border-transparent bg-emt-sky text-emt-blue hover:bg-emt-skyLight',
        destructive: 'border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80',
        outline: 'border-emt-blue text-emt-blue',
        success: 'border-transparent bg-green-500 text-white shadow hover:bg-green-600',
        warning: 'border-transparent bg-emt-orange text-white shadow hover:bg-emt-orange-dark',
        info: 'border-transparent bg-emt-blue-light text-emt-navy shadow hover:bg-emt-blue',
        adventure: 'border-transparent bg-travel-adventure text-white shadow',
        cultural: 'border-transparent bg-travel-cultural text-white shadow',
        devotional: 'border-transparent bg-travel-devotional text-white shadow',
        nightlife: 'border-transparent bg-travel-nightlife text-white shadow',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

const Badge = forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(badgeVariants({ variant }), className)}
        {...props}
      />
    )
  }
)

Badge.displayName = 'Badge'

export { Badge, badgeVariants }
