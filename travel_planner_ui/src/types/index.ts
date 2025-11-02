// Travel Planning Types
export interface TripRequest {
  source: string
  destination: string
  travel_mode: 'Self' | 'Booking'
  budget: string
  theme: 'Adventure' | 'Cultural' | 'Devotional' | 'Nightlife' | 'Relaxation'
  duration: string
  start_date?: string
  travelers_count?: number
  vehicle_type?: string // For Self mode
  transport_preferences?: string[] // For Booking mode
}

export interface TripOverview {
  source: string
  destination: string
  travel_mode: 'Self' | 'Booking'
  budget: string
  theme: string
  duration: string
  budget_status: 'sufficient' | 'insufficient'
  estimated_cost: string
  minimum_budget_required?: string
}

export interface Destination {
  name: string
  description: string
  theme_alignment: string
  highlights: string[]
  estimated_time: string
  entry_fees: string
  best_time_to_visit?: string
  booking_options?: {
    available: boolean
    booking_url?: string
  }
}

export interface Hotel {
  name: string
  location: string
  rating: string
  price_range: string
  amenities: string[]
  distance_from_attractions?: string
  theme_suitability: string
  booking_options?: {
    available: boolean
    booking_url?: string
    one_click_booking?: boolean
  }
}

export interface Restaurant {
  name: string
  cuisine_type: string
  location: string
  rating: string
  price_range: string
  specialties: string[]
  theme_alignment: string
  distance_from_hotels?: string
}

export interface Transportation {
  mode: string
  self_mode?: {
    route_details: string
    fuel_estimate: {
      vehicle_type: string
      total_distance: string
      fuel_cost: string
      toll_charges?: string
    }
    route_hotels: string[]
    route_restaurants: string[]
  }
  booking_mode?: {
    transport_options: Array<{
      type: string
      operator: string
      price: string
      duration: string
      booking_url?: string
      one_click_booking?: boolean
    }>
  }
}

export interface BudgetBreakdown {
  total_budget: string
  estimated_cost?: string
  breakdown: {
    transportation: string
    accommodation: string
    food: string
    activities: string
    shopping?: string
    miscellaneous?: string
  }
  detailed_breakdown?: {
    transportation?: string
    accommodation?: string
    food?: string
    activities?: string
    shopping?: string
    miscellaneous?: string
  }
  budget_optimization_tips?: string[]
  cost_saving_alternatives?: string[]
  budget_status?: 'sufficient' | 'tight' | 'insufficient'
  savings_potential?: number
}

export interface WeatherInfo {
  current_conditions: string
  temperature_range: string
  seasonal_info: string
  weather_recommendations: string[]
  climate_considerations: string
}

export interface DailyActivity {
  activity: string
  location: string
  duration: string
  cost: string
  weather_suitability?: string
}

export interface DailyItinerary {
  day: number
  weather_forecast?: string
  theme_focus: string
  morning: DailyActivity
  afternoon: DailyActivity
  evening: DailyActivity
  accommodation: string
  meals: {
    breakfast: string
    lunch: string
    dinner: string
  }
  daily_total_cost: string
  weather_tips?: string[]
}

export interface BookingSummary {
  one_click_bookings_available: boolean
  booking_links: {
    transportation?: string
    hotels: string[]
    activities: string[]
  }
  booking_instructions: string
}

export interface MockHotelBookingRequest {
  hotel_name: string
  destination: string
  location: string
  price: string
  check_in?: string
  check_out?: string
  guests?: number
  amenities?: string[]
  theme?: string
  travel_mode?: string
  room_type?: string
}

export interface MockHotelBookingResponse {
  status: string
  provider: string
  confirmation_id: string
  booking_reference: string
  payment_status: string
  total_amount: string
  check_in: string
  check_out: string
  guests: number
  room_type: string
  redirect_url: string
  support_message: string
  highlights: string[]
  next_steps: string[]
  branding: {
    cta_label: string
    badge: string
  }
  hotel_snapshot: {
    name: string
    location: string
    destination: string
    price: string
    theme?: string
    amenities: string[]
  }
}

export interface TripResponse {
  trip_overview: TripOverview
  destinations: Destination[]
  hotels: Hotel[]
  restaurants: Restaurant[]
  local_markets?: Array<{
    name: string
    location: string
    unique_products: string[]
    best_time_to_visit: string
    price_range: string
    theme_relevance: string
  }>
  transportation: Transportation
  budget_breakdown: BudgetBreakdown
  weather_info: WeatherInfo
  daily_itinerary: DailyItinerary[]
  booking_summary: BookingSummary
  sources: string[]
}

export interface BudgetValidation {
  valid: boolean
  message: string
  minimum_required: number
  user_budget: number
  shortfall?: number
  // Alternative format that backend might return
  budget_sufficient?: boolean
  current_market_rates?: any
}

export interface DurationValidation {
  minimum_duration: number
  feasible_durations: Array<{
    label: string
    value: string
    days: number
  }>
  message: string
  travel_info: {
    distance_category: string
    travel_considerations: string
  }
}

export interface ApiResponse<T> {
  status: 'success' | 'error'
  query?: string
  structured_input?: TripRequest
  agent_response?: T
  method?: string
  functions_called?: string[]
  search_data?: any
  error_message?: string
}

// UI State Types
export interface LoadingState {
  isLoading: boolean
  message?: string
  progress?: number
}

export interface ErrorState {
  hasError: boolean
  message?: string
  code?: string
}

// Form Types
export interface FormErrors {
  [key: string]: string | undefined
}

export interface FormState {
  values: TripRequest
  errors: FormErrors
  isValid: boolean
  isSubmitting: boolean
}
