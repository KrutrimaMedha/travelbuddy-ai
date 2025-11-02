import { useState, useRef, useEffect } from 'react'
import { format, addMonths, subMonths, startOfMonth, endOfMonth, startOfWeek, endOfWeek, addDays, isSameMonth, isSameDay, isToday, isBefore } from 'date-fns'
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react'
import { Button } from './Button'
import { Input } from './Input'
import { Card } from './Card'
import { cn } from '@/utils/cn'

interface DatePickerProps {
  value?: string
  onChange?: (date: string) => void
  placeholder?: string
  disabled?: boolean
  minDate?: Date
  className?: string
}

export function DatePicker({
  value,
  onChange,
  placeholder = "Select date",
  disabled = false,
  minDate = new Date(),
  className
}: DatePickerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [currentMonth, setCurrentMonth] = useState(value ? new Date(value) : new Date())
  const [selectedDate, setSelectedDate] = useState<Date | null>(value ? new Date(value) : null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Close calendar when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date)
    onChange?.(format(date, 'yyyy-MM-dd'))
    setIsOpen(false)
  }

  const handleInputClick = () => {
    if (!disabled) {
      setIsOpen(!isOpen)
    }
  }

  const goToPreviousMonth = () => {
    setCurrentMonth(subMonths(currentMonth, 1))
  }

  const goToNextMonth = () => {
    setCurrentMonth(addMonths(currentMonth, 1))
  }

  const renderCalendar = () => {
    const monthStart = startOfMonth(currentMonth)
    const monthEnd = endOfMonth(currentMonth)
    const startDate = startOfWeek(monthStart)
    const endDate = endOfWeek(monthEnd)

    const days = []
    let date = startDate

    // Create calendar grid
    while (date <= endDate) {
      for (let i = 0; i < 7; i++) {
        const currentDate = date
        const isCurrentMonth = isSameMonth(currentDate, monthStart)
        const isSelected = selectedDate && isSameDay(currentDate, selectedDate)
        const isTodayDate = isToday(currentDate)
        const isPast = isBefore(currentDate, minDate)

        days.push(
          <button
            key={format(currentDate, 'yyyy-MM-dd')}
            type="button"
            className={cn(
              "h-8 w-8 text-sm rounded-md transition-colors",
              "hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
              {
                "text-muted-foreground": !isCurrentMonth,
                "bg-primary text-primary-foreground": isSelected,
                "bg-muted text-muted-foreground": isTodayDate && !isSelected,
                "text-foreground": isCurrentMonth && !isSelected && !isTodayDate,
                "cursor-not-allowed opacity-50": isPast,
                "hover:bg-primary/20": !isPast && !isSelected
              }
            )}
            onClick={() => !isPast && handleDateSelect(currentDate)}
            disabled={isPast}
          >
            {format(currentDate, 'd')}
          </button>
        )
        date = addDays(date, 1)
      }
    }

    return days
  }

  const displayValue = selectedDate ? format(selectedDate, 'dd/MM/yyyy') : ''

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <div className="relative">
        <Input
          type="text"
          placeholder={placeholder}
          value={displayValue}
          onClick={handleInputClick}
          readOnly
          disabled={disabled}
          className={cn(
            "cursor-pointer pr-10",
            disabled && "cursor-not-allowed"
          )}
        />
        <Calendar
          className="absolute right-5 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none"
        />
      </div>

      {isOpen && !disabled && (
        <Card className="absolute top-full left-0 mt-1 p-4 shadow-lg border bg-background z-50 min-w-[280px]">
          {/* Calendar Header */}
          <div className="flex items-center justify-between mb-4">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={goToPreviousMonth}
              className="h-8 w-8 p-0"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>

            <h2 className="font-semibold text-sm">
              {format(currentMonth, 'MMMM yyyy')}
            </h2>

            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={goToNextMonth}
              className="h-8 w-8 p-0"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>

          {/* Days of week */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => (
              <div key={day} className="h-8 flex items-center justify-center text-xs font-medium text-muted-foreground">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar days */}
          <div className="grid grid-cols-7 gap-1">
            {renderCalendar()}
          </div>

          {/* Quick actions */}
          <div className="space-y-2 mt-4 pt-3 border-t">
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleDateSelect(new Date())}
                className="flex-1 text-xs"
              >
                Today
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleDateSelect(addDays(new Date(), 1))}
                className="flex-1 text-xs"
              >
                Tomorrow
              </Button>
            </div>
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleDateSelect(addDays(new Date(), 7))}
                className="flex-1 text-xs"
              >
                Next Week
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleDateSelect(addDays(new Date(), 30))}
                className="flex-1 text-xs"
              >
                Next Month
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
