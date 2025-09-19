import { useState, useEffect, useCallback, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { MapPin, Calendar, IndianRupee, Users, Car, Bus } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { DatePicker } from '@/components/ui/DatePicker'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

import { TRAVEL_THEMES, TRAVEL_MODES, POPULAR_DESTINATIONS, DURATION_OPTIONS, VEHICLE_TYPES, TRANSPORT_OPTIONS } from '@/utils/constants'
import type { TripRequest } from '@/types'
import { useTripPlanner } from '@/hooks/useTripPlanner'

// Simple debounce utility
function debounce<T extends (...args: any[]) => void>(func: T, delay: number) {
  let timeoutId: ReturnType<typeof setTimeout>
  const debouncedFunction = (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
  debouncedFunction.cancel = () => clearTimeout(timeoutId)
  return debouncedFunction
}

// Validation schema
const tripPlanningSchema = z.object({
  source: z.string().min(2, 'Source must be at least 2 characters'),
  destination: z.string().min(2, 'Destination must be at least 2 characters'),
  travel_mode: z.enum(['Self', 'Booking'], { required_error: 'Please select a travel mode' }),
  budget: z.string().min(1, 'Budget is required').refine(
    (val) => /^\d+$/.test(val.replace(/[Rs,]/g, '')) && parseInt(val.replace(/[Rs,]/g, '')) >= 1000,
    'Budget must be at least Rs1,000'
  ),
  theme: z.enum(['Adventure', 'Cultural', 'Devotional', 'Nightlife', 'Relaxation'], {
    required_error: 'Please select a travel theme'
  }),
  duration: z.string().min(1, 'Duration is required'),
  start_date: z.string().optional(),
  travelers_count: z.number().min(1).max(20).optional(),
  vehicle_type: z.string().optional(),
  transport_preferences: z.array(z.string()).optional()
})

type TripPlanningFormData = z.infer<typeof tripPlanningSchema>

interface TripPlanningFormProps {
  onSubmit: (data: TripRequest) => void
  isLoading?: boolean
}

export function TripPlanningForm({ onSubmit, isLoading }: TripPlanningFormProps) {
  const [selectedTheme, setSelectedTheme] = useState<string>('')
  const [selectedTravelMode, setSelectedTravelMode] = useState<string>('')
  const [selectedVehicleType, setSelectedVehicleType] = useState<string>('')
  const [selectedTransportOptions, setSelectedTransportOptions] = useState<string[]>([])
  // const [budgetSuggestion, setBudgetSuggestion] = useState<string>('')
  const [availableDurations, setAvailableDurations] = useState(DURATION_OPTIONS)
  const [durationValidationMessage, setDurationValidationMessage] = useState<string>('')

  const {
    validateBudget,
    budgetValidation,
    isValidatingBudget,
    validateDuration,
    durationValidation,
    isValidatingDuration
  } = useTripPlanner()

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid }
  } = useForm<TripPlanningFormData>({
    resolver: zodResolver(tripPlanningSchema),
    defaultValues: {
      travelers_count: 2,
      duration: '3-4 days'
    },
    mode: 'onChange'
  })

  const watchedValues = watch()

  // Track last validation parameters to prevent duplicate calls
  const lastBudgetValidationRef = useRef<string>('')
  const lastDurationValidationRef = useRef<string>('')

  // Store latest validation functions in refs to avoid stale closures
  const validateBudgetRef = useRef(validateBudget)
  validateBudgetRef.current = validateBudget

  const validateDurationRef = useRef(validateDuration)
  validateDurationRef.current = validateDuration

  // Debounced budget validation to prevent excessive API calls
  const debouncedValidateBudget = useCallback(
    debounce((request: {
      source: string
      destination: string
      travel_mode: string
      duration: string
      budget: string
    }) => {
      try {
        validateBudgetRef.current(request)
      } catch (error) {
        // Silently handle budget validation errors - don't prevent form submission
        console.log('Budget validation failed:', error)
      }
    }, 500), // 500ms delay
    []
  )

  // Auto-validate budget when key fields change (optional)
  useEffect(() => {
    if (
      watchedValues.source &&
      watchedValues.destination &&
      watchedValues.travel_mode &&
      watchedValues.duration &&
      watchedValues.budget
    ) {
      const budget = watchedValues.budget.replace(/[Rs,]/g, '')
      if (parseInt(budget) >= 1000) {
        // Create a unique key for the current validation parameters
        const currentKey = `${watchedValues.source}-${watchedValues.destination}-${watchedValues.travel_mode}-${watchedValues.duration}-${budget}`

        // Only validate if parameters have actually changed
        if (lastBudgetValidationRef.current !== currentKey) {
          lastBudgetValidationRef.current = currentKey
          debouncedValidateBudget({
            source: watchedValues.source,
            destination: watchedValues.destination,
            travel_mode: watchedValues.travel_mode,
            duration: watchedValues.duration,
            budget: `Rs${budget}`
          })
        }
      }
    }

    // Cleanup function to cancel pending debounced calls
    return () => {
      debouncedValidateBudget.cancel()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [watchedValues.source, watchedValues.destination, watchedValues.travel_mode, watchedValues.duration, watchedValues.budget])

  // Validate duration when source, destination, or travel mode changes
  useEffect(() => {
    if (
      watchedValues.source &&
      watchedValues.destination &&
      watchedValues.travel_mode
    ) {
      // Create a unique key for the current validation parameters
      const currentKey = `${watchedValues.source}-${watchedValues.destination}-${watchedValues.travel_mode}`

      // Only validate if parameters have actually changed
      if (lastDurationValidationRef.current !== currentKey) {
        const timeoutId = setTimeout(() => {
          lastDurationValidationRef.current = currentKey
          validateDurationRef.current({
            source: watchedValues.source,
            destination: watchedValues.destination,
            travel_mode: watchedValues.travel_mode
          })
        }, 300) // Debounce for 300ms to prevent multiple calls

        return () => clearTimeout(timeoutId)
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [watchedValues.source, watchedValues.destination, watchedValues.travel_mode])

  // Update available durations when validation result changes
  useEffect(() => {
    if (durationValidation?.feasible_durations) {
      // Always include the "More than 15 days" option even if not in validation results
      const moreThan15DaysOption = DURATION_OPTIONS.find(option => option.value === '15+ days')
      const feasibleDurations = [...durationValidation.feasible_durations]

      // Add "More than 15 days" option if not already present
      const hasMoreThan15Days = feasibleDurations.some(duration => duration.value === '15+ days')
      if (!hasMoreThan15Days && moreThan15DaysOption) {
        feasibleDurations.push(moreThan15DaysOption)
      }

      setAvailableDurations(feasibleDurations)
      setDurationValidationMessage(durationValidation.message)

      // Clear selected duration if it's no longer valid (except for "More than 15 days")
      const currentDuration = watchedValues.duration
      const isCurrentValid = feasibleDurations.some(
        duration => duration.value === currentDuration
      )

      if (currentDuration && !isCurrentValid) {
        setValue('duration', '')
      }
    } else {
      // Reset to default durations if validation fails
      setAvailableDurations(DURATION_OPTIONS)
      setDurationValidationMessage('')
    }
  }, [durationValidation, setValue, watchedValues.duration])

  // Format budget input
  const formatBudget = (value: string) => {
    const numericValue = value.replace(/[^\d]/g, '')
    if (numericValue) {
      return `Rs${parseInt(numericValue).toLocaleString('en-IN')}`
    }
    return ''
  }

  const onFormSubmit = (data: TripPlanningFormData) => {
    const formattedBudget = data.budget.replace(/[Rs,]/g, '')
    const tripRequest: TripRequest = {
      ...data,
      budget: `Rs${formattedBudget}`,
      travelers_count: data.travelers_count || 2
    }
    onSubmit(tripRequest)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center gradient-text">
            Plan Your Perfect Trip
          </CardTitle>
          <p className="text-muted-foreground text-center">
            Let AI create a personalized itinerary tailored to your preferences
          </p>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
            {/* Source & Destination */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-primary" />
                  From (Source)
                </label>
                <Input
                  {...register('source')}
                  placeholder="e.g., Mumbai, Delhi"
                  error={!!errors.source}
                  list="popular-sources"
                />
                <datalist id="popular-sources">
                  {POPULAR_DESTINATIONS.map(dest => (
                    <option key={dest} value={dest} />
                  ))}
                </datalist>
                {errors.source && (
                  <p className="text-xs text-destructive">{errors.source.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-primary" />
                  To (Destination)
                </label>
                <Input
                  {...register('destination')}
                  placeholder="e.g., Goa, Kerala"
                  error={!!errors.destination}
                  list="popular-destinations"
                />
                <datalist id="popular-destinations">
                  {POPULAR_DESTINATIONS.map(dest => (
                    <option key={dest} value={dest} />
                  ))}
                </datalist>
                {errors.destination && (
                  <p className="text-xs text-destructive">{errors.destination.message}</p>
                )}
              </div>
            </div>

            {/* Travel Mode Selection */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Travel Mode</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {TRAVEL_MODES.map((mode) => (
                  <motion.div
                    key={mode.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      className={`cursor-pointer transition-all ${
                        selectedTravelMode === mode.id
                          ? 'ring-2 ring-primary border-primary bg-primary/5'
                          : 'hover:border-primary/50'
                      }`}
                      onClick={() => {
                        setValue('travel_mode', mode.id as 'Self' | 'Booking')
                        setSelectedTravelMode(mode.id)
                      }}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <div className="text-2xl">{mode.icon}</div>
                          <div className="flex-1">
                            <h3 className="font-medium">{mode.label}</h3>
                            <p className="text-xs text-muted-foreground mb-2">
                              {mode.description}
                            </p>
                            <div className="flex flex-wrap gap-1">
                              {mode.benefits.map((benefit) => (
                                <Badge key={benefit} variant="secondary" className="text-xs">
                                  {benefit}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          {selectedTravelMode === mode.id && (
                            <div className="text-primary">
                              {mode.id === 'Self' ? <Car className="h-5 w-5" /> : <Bus className="h-5 w-5" />}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
              {errors.travel_mode && (
                <p className="text-xs text-destructive">{errors.travel_mode.message}</p>
              )}
            </div>

            {/* Vehicle/Transport Selection */}
            {selectedTravelMode === 'Self' && (
              <div className="space-y-3">
                <label className="text-sm font-medium">Select Your Vehicle</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {VEHICLE_TYPES.map((vehicle) => (
                    <motion.div
                      key={vehicle.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Card
                        className={`cursor-pointer transition-all ${
                          selectedVehicleType === vehicle.id
                            ? 'ring-2 ring-primary border-primary bg-primary/5'
                            : 'hover:border-primary/50'
                        }`}
                        onClick={() => {
                          setValue('vehicle_type', vehicle.id)
                          setSelectedVehicleType(vehicle.id)
                        }}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="text-2xl">{vehicle.icon}</div>
                            <div className="flex-1">
                              <h3 className="font-medium">{vehicle.label}</h3>
                              <p className="text-xs text-muted-foreground mb-1">
                                {vehicle.description}
                              </p>
                              <Badge variant="secondary" className="text-xs">
                                {vehicle.fuelEfficiency} km/l
                              </Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {selectedTravelMode === 'Booking' && (
              <div className="space-y-3">
                <label className="text-sm font-medium">Preferred Transport Options</label>
                <p className="text-xs text-muted-foreground">Select one or more transport types you prefer</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {TRANSPORT_OPTIONS.map((transport) => (
                    <motion.div
                      key={transport.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Card
                        className={`cursor-pointer transition-all ${
                          selectedTransportOptions.includes(transport.id)
                            ? 'ring-2 ring-primary border-primary bg-primary/5'
                            : 'hover:border-primary/50'
                        }`}
                        onClick={() => {
                          const newSelection = selectedTransportOptions.includes(transport.id)
                            ? selectedTransportOptions.filter(id => id !== transport.id)
                            : [...selectedTransportOptions, transport.id]
                          setSelectedTransportOptions(newSelection)
                          setValue('transport_preferences', newSelection)
                        }}
                      >
                        <CardContent className="p-3">
                          <div className="text-center">
                            <div className="text-xl mb-1">{transport.icon}</div>
                            <h3 className="text-xs font-medium">{transport.label}</h3>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Travel Theme Selection */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Travel Theme</label>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {TRAVEL_THEMES.map((theme) => (
                  <motion.div
                    key={theme.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      className={`cursor-pointer transition-all ${
                        selectedTheme === theme.id
                          ? 'ring-2 ring-primary border-primary'
                          : 'hover:border-primary/50'
                      }`}
                      onClick={() => {
                        setValue('theme', theme.id as any)
                        setSelectedTheme(theme.id)
                      }}
                    >
                      <CardContent className="p-4">
                        <div className="text-center">
                          <div className={`w-12 h-12 rounded-full bg-gradient-to-r ${theme.gradient} flex items-center justify-center text-white text-xl mb-2 mx-auto`}>
                            {theme.icon}
                          </div>
                          <h3 className="font-medium">{theme.label}</h3>
                          <p className="text-xs text-muted-foreground mt-1">
                            {theme.description}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
              {errors.theme && (
                <p className="text-xs text-destructive">{errors.theme.message}</p>
              )}
            </div>

            {/* Budget & Duration */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <IndianRupee className="h-4 w-4 text-primary" />
                  Total Budget
                  {isValidatingBudget && (
                    <span className="text-xs text-muted-foreground">(Validating...)</span>
                  )}
                </label>
                <Input
                  {...register('budget')}
                  placeholder="e.g., 15000"
                  error={!!errors.budget}
                  onChange={(e) => {
                    const formatted = formatBudget(e.target.value)
                    setValue('budget', formatted)
                  }}
                />
                {errors.budget && (
                  <p className="text-xs text-destructive">{errors.budget.message}</p>
                )}
                {budgetValidation && (
                  <div className={`text-xs p-2 rounded ${
                    (budgetValidation.valid === true || (budgetValidation as any).budget_sufficient === true || (budgetValidation as any).status === 'sufficient')
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                    {/* Show clear sufficient/insufficient status */}
                    <div className="font-medium mb-1">
                      {(budgetValidation.valid === true || (budgetValidation as any).budget_sufficient === true || (budgetValidation as any).status === 'sufficient') ? (
                        <span className="text-green-700">✅ Budget Sufficient</span>
                      ) : (
                        <span className="text-red-700">❌ Budget Insufficient</span>
                      )}
                    </div>

                    {/* Show minimum required if budget is insufficient */}
                    {(budgetValidation.valid !== true && (budgetValidation as any).budget_sufficient !== true && (budgetValidation as any).status !== 'sufficient') && (
                      <>
                        {(budgetValidation.minimum_required || (budgetValidation as any).minimum_required) && (
                          <p className="text-red-600 font-medium">
                            Minimum required: Rs{(budgetValidation.minimum_required || (budgetValidation as any).minimum_required).toLocaleString()}
                          </p>
                        )}
                        {budgetValidation.shortfall && (
                          <p className="text-red-600">
                            Shortfall: Rs{budgetValidation.shortfall.toLocaleString()}
                          </p>
                        )}
                        <p className="text-red-600">
                          Please increase your budget to meet the minimum requirements for this trip.
                        </p>
                      </>
                    )}

                    {/* Show positive message if budget is sufficient */}
                    {(budgetValidation.valid === true || (budgetValidation as any).budget_sufficient === true) && (
                      <p className="text-green-600">
                        Your budget is adequate for this trip. Great choice!
                      </p>
                    )}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-primary" />
                  Duration
                  {isValidatingDuration && (
                    <span className="text-xs text-muted-foreground">(Checking...)</span>
                  )}
                </label>
                <Select
                  {...register('duration')}
                  error={!!errors.duration}
                  options={availableDurations}
                  placeholder="Select duration"
                  disabled={false}
                />
                {errors.duration && (
                  <p className="text-xs text-destructive">{errors.duration.message}</p>
                )}
                {durationValidationMessage && (
                  <div className="text-xs p-2 rounded bg-blue-50 text-blue-700 border border-blue-200">
                    {durationValidationMessage}
                    {durationValidation?.travel_info && (
                      <p className="mt-1 text-blue-600">
                        {durationValidation.travel_info.travel_considerations}
                      </p>
                    )}
                  </div>
                )}
                {watchedValues.duration === '15+ days' && (
                  <div className="text-xs p-2 rounded bg-green-50 text-green-700 border border-green-200">
                    ✨ Extended trip selected! Perfect for comprehensive exploration and immersive experiences.
                  </div>
                )}
              </div>
            </div>

            {/* Optional Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-primary" />
                  Start Date (Optional)
                </label>
                <DatePicker
                  value={watchedValues.start_date}
                  onChange={(date) => setValue('start_date', date)}
                  placeholder="Select your travel start date"
                  minDate={new Date()}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4 text-primary" />
                  Number of Travelers
                </label>
                <Input
                  {...register('travelers_count', { valueAsNumber: true })}
                  type="number"
                  min="1"
                  max="20"
                  placeholder="2"
                />
              </div>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="gradient"
              size="xl"
              className="w-full"
              loading={isLoading}
              disabled={!isValid || isLoading}
            >
              {isLoading ? 'Planning Your Trip...' : 'Generate Trip Plan ✨'}
            </Button>

          </form>
        </CardContent>
      </Card>
    </motion.div>
  )
}