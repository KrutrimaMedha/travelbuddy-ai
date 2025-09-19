
import axios, { AxiosResponse } from 'axios'
import type { TripRequest, TripResponse, BudgetValidation, ApiResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for trip planning
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Disable credentials to match backend CORS config
})

// Request interceptor for logging and auth
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Log requests in development
    if (import.meta.env.DEV) {
      console.log('API Request:', config.method?.toUpperCase(), config.url, config.data)
    }

    return config
  },
  (error) => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log('API Response:', response.status, response.config.url, response.data)
    }
    return response
  },
  (error) => {
    console.error('Response Error:', error.response?.status, error.response?.data || error.message)

    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

// API Service Functions
export const travelPlannerApi = {
  /**
   * Plan a comprehensive trip with AI agent
   */
  async planTrip(request: TripRequest | string): Promise<ApiResponse<TripResponse>> {
    try {
      const response: AxiosResponse<ApiResponse<TripResponse>> = await api.post('/api/plan-trip', { user_input: request })
      return response.data
    } catch (error) {
      console.error('Trip planning failed:', error)

      // Provide more specific error messages
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNREFUSED') {
          throw new Error('Cannot connect to the server. Please make sure the backend is running on http://localhost:8000')
        }
        if (error.response?.status === 503) {
          throw new Error('Travel planning service is unavailable. Please check your API keys.')
        }
        if (error.response?.data?.detail) {
          throw new Error(error.response.data.detail)
        }
      }

      throw new Error('Failed to plan trip. Please try again.')
    }
  },

  /**
   * Validate budget for a trip
   */
  async validateBudget(request: {
    source: string
    destination: string
    travel_mode: string
    duration: string
    budget: string
  }): Promise<BudgetValidation> {
    try {
      const response: AxiosResponse<BudgetValidation> = await api.post('/api/validate-budget', request)
      return response.data
    } catch (error) {
      console.error('Budget validation failed:', error)
      throw new Error(
        axios.isAxiosError(error) && error.response?.data?.message
          ? error.response.data.message
          : 'Failed to validate budget. Please try again.'
      )
    }
  },

  /**
   * Get detailed budget breakdown with cost estimation and money-saving tips
   */
  async getDetailedBudget(request: {
    source: string
    destination: string
    travel_mode: string
    duration: string
    budget: string
    theme?: string
  }): Promise<{
    total_budget: string
    estimated_cost: string
    breakdown: {
      transportation: string
      accommodation: string
      food: string
      activities: string
      shopping: string
      miscellaneous: string
    }
    detailed_breakdown: {
      transportation: string
      accommodation: string
      food: string
      activities: string
      shopping: string
      miscellaneous: string
    }
    budget_optimization_tips: string[]
    cost_saving_alternatives: string[]
    budget_status: string
    savings_potential: number
  }> {
    try {
      const response = await api.post('/api/detailed-budget', request)
      return response.data
    } catch (error) {
      console.error('Detailed budget calculation failed:', error)
      throw new Error(
        axios.isAxiosError(error) && error.response?.data?.message
          ? error.response.data.message
          : 'Failed to calculate detailed budget. Please try again.'
      )
    }
  },

  /**
   * Validate duration and get feasible options
   */
  async validateDuration(request: {
    source: string
    destination: string
    travel_mode: string
  }): Promise<{
    minimum_duration: number
    feasible_durations: Array<{
      label: string
      value: string
      days?: number
    }>
    message: string
    travel_info: {
      distance_category: string
      travel_considerations: string
    }
  }> {
    try {
      const response = await api.post('/api/validate-duration', request)
      return response.data
    } catch (error) {
      console.error('Duration validation failed:', error)
      throw new Error(
        axios.isAxiosError(error) && error.response?.data?.message
          ? error.response.data.message
          : 'Failed to validate duration. Please try again.'
      )
    }
  },

  /**
   * Search for travel information
   */
  async search(query: string): Promise<any> {
    try {
      const response = await api.post('/api/search', { query })
      return response.data
    } catch (error) {
      console.error('Search failed:', error)
      throw new Error(
        axios.isAxiosError(error) && error.response?.data?.message
          ? error.response.data.message
          : 'Search failed. Please try again.'
      )
    }
  },

  /**
   * Get weather information for a destination
   */
  async getWeather(location: string, dateRange: string = 'current'): Promise<any> {
    try {
      const response = await api.get('/api/weather', {
        params: { location, date_range: dateRange }
      })
      return response.data
    } catch (error) {
      console.error('Weather fetch failed:', error)
      throw new Error('Failed to get weather information')
    }
  },

  /**
   * Get hotel recommendations
   */
  async getHotels(location: string, budgetRange: string, theme: string): Promise<any> {
    try {
      const response = await api.get('/api/hotels', {
        params: { location, budget_range: budgetRange, theme }
      })
      return response.data
    } catch (error) {
      console.error('Hotels fetch failed:', error)
      throw new Error('Failed to get hotel recommendations')
    }
  },

  /**
   * Save trip for later reference
   */
  async saveTrip(trip: TripResponse & { id?: string; name: string }): Promise<{ id: string }> {
    try {
      const response = await api.post('/api/trips/save', trip)
      return response.data
    } catch (error) {
      console.error('Save trip failed:', error)
      throw new Error('Failed to save trip')
    }
  },

  /**
   * Get saved trips
   */
  async getSavedTrips(): Promise<Array<TripResponse & { id: string; name: string; created_at: string }>> {
    try {
      const response = await api.get('/api/trips')
      return response.data
    } catch (error) {
      console.error('Get saved trips failed:', error)
      throw new Error('Failed to retrieve saved trips')
    }
  }
}

// Export the axios instance for direct use if needed
export { api }
export default travelPlannerApi
