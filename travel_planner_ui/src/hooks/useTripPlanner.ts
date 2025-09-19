import { useState, useCallback } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { travelPlannerApi } from '@/services/api'
import type { TripRequest, TripResponse, ApiResponse, LoadingState } from '@/types'
import { toast } from 'sonner'

export function useTripPlanner() {
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: false,
    message: undefined,
    progress: 0
  })

  // Trip planning mutation
  const planTripMutation = useMutation({
    mutationFn: async (request: TripRequest | string) => {
      setLoadingState({
        isLoading: true,
        message: 'Analyzing your travel preferences...',
        progress: 20
      })

      return travelPlannerApi.planTrip(request)
    },
    onSuccess: (data: ApiResponse<TripResponse>) => {
      setLoadingState({
        isLoading: false,
        message: undefined,
        progress: 100
      })

      // Don't show success toast here - let TripResultsDisplay handle it after transformation
      if (data.status !== 'success') {
        toast.error(data.error_message || 'Failed to generate trip plan')
      }
    },
    onError: (error: Error) => {
      setLoadingState({
        isLoading: false,
        message: undefined,
        progress: 0
      })
      toast.error(error.message || 'Failed to plan trip')
    },
    onMutate: () => {
      // Progress simulation
      const progressInterval = setInterval(() => {
        setLoadingState(prev => {
          const newProgress = Math.min((prev.progress || 0) + 10, 90)
          let message = prev.message

          if (newProgress === 40) {
            message = 'Searching for destinations and hotels...'
          } else if (newProgress === 60) {
            message = 'Generating personalized itinerary...'
          } else if (newProgress === 80) {
            message = 'Calculating budget breakdown...'
          }

          return {
            isLoading: true,
            message,
            progress: newProgress
          }
        })
      }, 1000)

      // Clear interval after 10 seconds
      setTimeout(() => clearInterval(progressInterval), 10000)

      return () => clearInterval(progressInterval)
    }
  })

  // Budget validation mutation
  const validateBudgetMutation = useMutation({
    mutationFn: travelPlannerApi.validateBudget,
    onError: (error: Error) => {
      console.log('Budget validation error (non-critical):', error.message)
      // Don't show error toast for budget validation - it's optional
    }
  })

  // Duration validation mutation
  const validateDurationMutation = useMutation({
    mutationFn: travelPlannerApi.validateDuration,
    onError: (error: Error) => {
      console.log('Duration validation error (non-critical):', error.message)
      // Don't show error toast for duration validation - it's optional
    }
  })

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: travelPlannerApi.search,
    onError: (error: Error) => {
      toast.error(error.message || 'Search failed')
    }
  })

  // Saved trips query
  const {
    data: savedTrips,
    isLoading: loadingSavedTrips,
    refetch: refetchSavedTrips
  } = useQuery({
    queryKey: ['saved-trips'],
    queryFn: travelPlannerApi.getSavedTrips,
    enabled: false, // Enable when needed
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Save trip mutation
  const saveTripMutation = useMutation({
    mutationFn: travelPlannerApi.saveTrip,
    onSuccess: () => {
      toast.success('Trip saved successfully!')
      refetchSavedTrips()
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to save trip')
    }
  })

  // Convenience methods
  const planTrip = useCallback((request: TripRequest | string) => {
    planTripMutation.mutate(request)
  }, [planTripMutation])

  const validateBudget = useCallback((request: {
    source: string
    destination: string
    travel_mode: string
    duration: string
    budget: string
  }) => {
    validateBudgetMutation.mutate(request)
  }, [validateBudgetMutation])

  const validateDuration = useCallback((request: {
    source: string
    destination: string
    travel_mode: string
  }) => {
    validateDurationMutation.mutate(request)
  }, [validateDurationMutation])

  const search = useCallback((query: string) => {
    searchMutation.mutate(query)
  }, [searchMutation])

  const saveTrip = useCallback((trip: TripResponse & { id?: string; name: string }) => {
    saveTripMutation.mutate(trip)
  }, [saveTripMutation])

  return {
    // Trip planning
    planTrip,
    tripPlan: planTripMutation.data,
    isPlanning: planTripMutation.isPending,
    planningError: planTripMutation.error,
    loadingState,

    // Budget validation
    validateBudget,
    budgetValidation: validateBudgetMutation.data,
    isValidatingBudget: validateBudgetMutation.isPending,
    budgetValidationError: validateBudgetMutation.error,

    // Duration validation
    validateDuration,
    durationValidation: validateDurationMutation.data,
    isValidatingDuration: validateDurationMutation.isPending,
    durationValidationError: validateDurationMutation.error,

    // Search
    search,
    searchResults: searchMutation.data,
    isSearching: searchMutation.isPending,
    searchError: searchMutation.error,

    // Saved trips
    savedTrips,
    loadingSavedTrips,
    refetchSavedTrips,
    saveTrip,
    isSavingTrip: saveTripMutation.isPending,

    // Reset functions
    resetTripPlan: planTripMutation.reset,
    resetBudgetValidation: validateBudgetMutation.reset,
    resetDurationValidation: validateDurationMutation.reset,
    resetSearch: searchMutation.reset,
  }
}