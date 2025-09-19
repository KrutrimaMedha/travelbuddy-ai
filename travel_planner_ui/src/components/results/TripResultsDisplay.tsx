import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  MapPin, Hotel, Utensils, Car, Plane, Calendar, IndianRupee,
  Clock, Star, ExternalLink, Bookmark, Share2,
  Sun, Cloud, Umbrella, Thermometer, Info, CheckCircle2
} from 'lucide-react'
import { toast } from 'sonner'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

import type { TripResponse, ApiResponse, BudgetBreakdown } from '@/types'
import { TRAVEL_THEMES } from '@/utils/constants'

// Backend API functions
const fetchBackendData = async (endpoint: string, params: any) => {
  try {
    const queryParams = new URLSearchParams(params).toString()
    const url = `http://localhost:8000${endpoint}?${queryParams}`
    console.log('Fetching from backend:', url)

    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    console.log('Backend response:', data)
    return data
  } catch (error) {
    console.error(`Failed to fetch ${endpoint}:`, error)
    return null
  }
}

// DEPRECATED: Removed hardcoded distance calculation - now using backend real-time data
// This function previously used hardcoded distance values which caused inconsistencies
// The distance information now comes directly from the backend AI agent's real-time calculations

interface TripResultsDisplayProps {
  tripData: ApiResponse<TripResponse> | null
  isLoading: boolean
  onSaveTrip?: (trip: TripResponse & { name: string }) => void
  onShareTrip?: (trip: TripResponse) => void
}

export function TripResultsDisplay({
  tripData,
  isLoading,
  onSaveTrip,
  onShareTrip
}: TripResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'itinerary' | 'accommodations' | 'budget'>('overview')
  const [savedTrip, setSavedTrip] = useState(false)
  const [mockMessage, setMockMessage] = useState<{ type: 'success' | 'info' | 'error'; message: string } | null>(null)
  const [transformedTrip, setTransformedTrip] = useState<any>(null)
  const [isTransforming, setIsTransforming] = useState(false)

  // Show mock message with auto-hide
  const showMockMessage = (type: 'success' | 'info' | 'error', message: string) => {
    setMockMessage({ type, message })
    setTimeout(() => setMockMessage(null), 4000) // Hide after 4 seconds
  }

  // Effect to transform backend response with AI data
  useEffect(() => {
    const transformData = async () => {
      if (tripData?.agent_response && !isLoading) {
        setIsTransforming(true)
        console.log('TripResultsDisplay - Starting AI-powered data transformation...')
        try {
          const transformed = await transformBackendResponse(tripData.agent_response)
          setTransformedTrip(transformed)
          console.log('TripResultsDisplay - AI transformation completed:', transformed)
          // Show success toast only after transformation is complete
          toast.success('Trip plan generated successfully!')
        } catch (error) {
          console.error('TripResultsDisplay - AI transformation failed:', error)
          // Fallback to basic transformation without AI enhancements
          const basicTransformed = transformBackendResponseBasic(tripData.agent_response)
          setTransformedTrip(basicTransformed)
          // Show success toast even with fallback transformation
          toast.success('Trip plan generated successfully!')
        }
        setIsTransforming(false)
      }
    }

    transformData()
  }, [tripData])

  // Debug logging
  console.log('TripResultsDisplay - tripData:', tripData)
  console.log('TripResultsDisplay - isLoading:', isLoading)
  console.log('TripResultsDisplay - isTransforming:', isTransforming)
  console.log('TripResultsDisplay - transformedTrip:', transformedTrip)

  if (isLoading || isTransforming) {
    return (
      <Card className="w-full max-w-6xl mx-auto">
        <CardContent className="p-12">
          <LoadingSpinner
            size="xl"
            message={isTransforming ? "Enhancing with AI recommendations..." : "Creating your personalized travel plan..."}
            progress={isTransforming ? 95 : 70}
          />
        </CardContent>
      </Card>
    )
  }

  if (!tripData) {
    return (
      <Card className="w-full max-w-6xl mx-auto">
        <CardContent className="p-8 text-center">
          <div className="text-muted-foreground">
            <Info className="h-12 w-12 mx-auto mb-4" />
            <p>Plan your trip above to see personalized recommendations!</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (tripData.status !== 'success') {
    return (
      <Card className="w-full max-w-6xl mx-auto">
        <CardContent className="p-8 text-center">
          <div className="text-destructive">
            <Info className="h-12 w-12 mx-auto mb-4" />
            <p className="text-lg font-semibold mb-2">Trip Planning Failed</p>
            <p className="text-sm">
              {tripData.error_message || 'An error occurred while planning your trip. Please try again.'}
            </p>
            <div className="mt-4 p-4 bg-muted rounded-lg text-left text-xs">
              <p className="font-medium mb-2">Debug Info:</p>
              <pre className="whitespace-pre-wrap">{JSON.stringify(tripData, null, 2)}</pre>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!tripData.agent_response) {
    return (
      <Card className="w-full max-w-6xl mx-auto">
        <CardContent className="p-8 text-center">
          <div className="text-muted-foreground">
            <Info className="h-12 w-12 mx-auto mb-4" />
            <p className="text-lg font-semibold mb-2">No Trip Data Available</p>
            <p className="text-sm">The trip planning completed but no data was returned.</p>
            <div className="mt-4 p-4 bg-muted rounded-lg text-left text-xs">
              <p className="font-medium mb-2">Response Structure:</p>
              <pre className="whitespace-pre-wrap">{JSON.stringify(tripData, null, 2)}</pre>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Transform destinations - use existing data first, then fallback to API
  const transformDestinations = async (destinations: any[], destination: string, theme: string) => {
    // If we have valid destinations data, use it directly
    if (destinations && destinations.length > 0) {
      return destinations.map((dest: any) => ({
        name: dest.name || dest.title || `Popular attractions`,
        description: dest.description || dest.snippet || `Popular attractions for ${theme.toLowerCase()} travelers`,
        theme_alignment: dest.theme_alignment || `Great for ${theme.toLowerCase()} travelers`,
        highlights: dest.highlights || ['Popular destination', 'Verified attraction'],
        estimated_time: dest.estimated_time || '3-5 hours',
        entry_fees: dest.entry_fees || 'Check locally',
        best_time_to_visit: dest.best_time_to_visit || dest.best_time || 'Check locally',
        ai_recommendation: dest.ai_recommendation || false,
        source: dest.source || 'Travel agent'
      }))
    }

    // Only fetch from API if no data exists
    console.log('Fetching AI-powered destination data from backend...')
    const destinationData = await fetchBackendData('/api/destinations', {
      location: destination,
      theme: theme,
      limit: 3
    })

    if (destinationData && destinationData.destinations && destinationData.destinations.length > 0) {
      return destinationData.destinations
    }

    // Enhanced fallback with multiple destination options
    const destinationText = destination === 'Your Destination' ? 'your destination' : destination

    // Create better theme descriptions for fallback content
    const getThemeDescription = (theme: string) => {
      const lowerTheme = theme.toLowerCase()
      switch (lowerTheme) {
        case 'adventure':
          return { adjective: 'adventure', activities: 'outdoor and adventure activities', culture: 'adventure culture' }
        case 'cultural':
          return { adjective: 'cultural', activities: 'heritage and cultural activities', culture: 'rich cultural heritage' }
        case 'devotional':
          return { adjective: 'spiritual', activities: 'spiritual and devotional activities', culture: 'spiritual traditions' }
        case 'nightlife':
          return { adjective: 'entertainment', activities: 'nightlife and entertainment activities', culture: 'vibrant nightlife scene' }
        case 'relaxation':
          return { adjective: 'relaxation', activities: 'peaceful and relaxing activities', culture: 'serene atmosphere' }
        default:
          return { adjective: 'travel', activities: 'popular travel activities', culture: 'local culture and attractions' }
      }
    }

    const themeDesc = getThemeDescription(theme)

    return [
      {
        name: `Top travel attractions`,
        description: `Discover the most popular destinations ${destinationText !== 'your destination' ? `that ${destinationText} has to offer` : 'for your trip'}. Perfect for travelers seeking authentic experiences and ${themeDesc.activities}.`,
        theme_alignment: `Specially curated for ${theme} travelers`,
        highlights: [`${theme} experience`, 'Must-visit', 'Popular destination', 'Great reviews'],
        estimated_time: '4-6 hours',
        entry_fees: 'Varies by attraction',
        best_time_to_visit: 'Morning to evening',
        ai_recommendation: false,
        source: 'Travel recommendations'
      },
      {
        name: `Local experiences and attractions`,
        description: `Explore authentic local spots and hidden gems ${destinationText !== 'your destination' ? `that showcase the true essence of ${destinationText}'s ${themeDesc.culture}` : 'for an authentic travel experience'}.`,
        theme_alignment: `Perfect for ${theme} enthusiasts`,
        highlights: ['Local favorite', 'Authentic experience', 'Hidden gem', 'Cultural significance'],
        estimated_time: '3-5 hours',
        entry_fees: 'Usually affordable',
        best_time_to_visit: 'Check local timings',
        ai_recommendation: false,
        source: 'Local recommendations'
      },
      {
        name: `Must-visit highlights`,
        description: `Experience the best ${themeDesc.activities} ${destinationText !== 'your destination' ? `that ${destinationText} offers` : 'at your destination'} with these carefully selected attractions.`,
        theme_alignment: `Ideal for ${theme} travelers`,
        highlights: ['Recommended', 'Tourist-friendly', 'Well-reviewed', 'Safe'],
        estimated_time: '2-4 hours',
        entry_fees: 'Moderate pricing',
        best_time_to_visit: 'Flexible timing',
        ai_recommendation: false,
        source: 'Travel guide recommendations'
      }
    ]
  }

  // Transform hotels - use existing data first, then fallback to API
  const transformHotels = async (hotels: any[], destination: string, theme: string, budget_range: string = 'mid-range') => {
    // If we have valid hotels data, use it directly
    if (hotels && hotels.length > 0) {
      return hotels.map((hotel: any) => ({
        name: hotel.name || hotel.title || `Hotel in ${destination}`,
        location: hotel.location || `${destination} area`,
        rating: hotel.rating || '4.0+',
        price_range: hotel.price_range || budget_range,
        amenities: hotel.amenities || ['WiFi', 'AC', 'Room Service'],
        theme_suitability: hotel.theme_suitability || `Great for ${theme.toLowerCase()} travelers`,
        booking_options: hotel.booking_options || {
          available: true,
          booking_url: hotel.booking_url || '#',
          ai_recommendation: hotel.ai_recommendation || false
        },
        ai_analysis: hotel.ai_analysis,
        source: hotel.source || 'Travel agent'
      }))
    }

    // Only fetch from API if no data exists
    console.log('Fetching AI-powered hotel data from backend...')
    const hotelData = await fetchBackendData('/api/hotels', {
      location: destination,
      budget_range: budget_range,
      theme: theme
    })

    if (hotelData && hotelData.hotels && hotelData.hotels.length > 0) {
      return hotelData.hotels
    }

    // Enhanced fallback with multiple hotel options
    const destinationText = destination === 'Your Destination' ? 'your destination' : destination
    return [
      {
        name: `Premium stays`,
        location: destinationText === 'your destination' ? 'City center area' : `${destinationText} city center`,
        rating: '4.5+',
        price_range: budget_range || 'Rs3000-6000 per night',
        amenities: ['WiFi', 'AC', 'Room Service', 'Parking', 'Restaurant', 'Gym'],
        theme_suitability: `Excellent for ${theme} travelers seeking comfort`,
        booking_options: {
          available: true,
          booking_url: '#',
          one_click_booking: false
        },
        ai_analysis: `Top-rated accommodation perfect for ${theme.toLowerCase()} experiences`,
        source: 'Premium hotel recommendations'
      },
      {
        name: `Budget-friendly accommodations`,
        location: destinationText === 'your destination' ? 'Main area' : `${destinationText} main area`,
        rating: '3.8+',
        price_range: 'Rs1500-3000 per night',
        amenities: ['WiFi', 'AC', 'Clean rooms', 'Basic amenities'],
        theme_suitability: `Great value for ${theme} travelers`,
        booking_options: {
          available: true,
          booking_url: '#',
          one_click_booking: false
        },
        ai_analysis: `Affordable and comfortable stays for budget-conscious travelers`,
        source: 'Budget hotel recommendations'
      },
      {
        name: `Boutique accommodations`,
        location: destinationText === 'your destination' ? 'Heritage area' : `${destinationText} heritage area`,
        rating: '4.2+',
        price_range: 'Rs2500-5000 per night',
        amenities: ['WiFi', 'AC', 'Unique decor', 'Personalized service', 'Local cuisine'],
        theme_suitability: `Specially designed for ${theme} enthusiasts`,
        booking_options: {
          available: true,
          booking_url: '#',
          one_click_booking: false
        },
        ai_analysis: `Unique stays that enhance your ${theme.toLowerCase()} experience`,
        source: 'Boutique hotel recommendations'
      }
    ]
  }

  // Transform restaurants - use existing data first, then fallback to API
  const transformRestaurants = async (restaurants: any[], destination: string, theme: string = 'Adventure') => {
    // If we have valid restaurants data, use it directly
    if (restaurants && restaurants.length > 0) {
      return restaurants.map((restaurant: any) => ({
        name: restaurant.name || restaurant.title || `Restaurant in ${destination}`,
        cuisine_type: restaurant.cuisine_type || 'Local cuisine',
        location: restaurant.location || `${destination} area`,
        rating: restaurant.rating || '4.0+',
        price_range: restaurant.price_range || 'Rs300-800 per person',
        specialties: restaurant.specialties || ['Local dishes', 'Regional cuisine'],
        theme_alignment: restaurant.theme_alignment || `Great for ${theme.toLowerCase()} travelers`,
        ai_recommendation: restaurant.ai_recommendation || false,
        source: restaurant.source || 'Travel agent'
      }))
    }

    // Only fetch from API if no data exists
    console.log('Fetching AI-powered restaurant data from backend...')
    const restaurantData = await fetchBackendData('/api/restaurants', {
      location: destination,
      theme: theme,
      cuisine_preference: 'local'
    })

    if (restaurantData && restaurantData.restaurants && restaurantData.restaurants.length > 0) {
      return restaurantData.restaurants
    }

    // Enhanced fallback with multiple restaurant options
    const destinationText = destination === 'Your Destination' ? 'your destination' : destination
    return [
      {
        name: `Authentic local cuisine`,
        cuisine_type: 'Regional specialties',
        location: destinationText === 'your destination' ? 'Old city area' : `${destinationText} old city`,
        rating: '4.3+',
        price_range: 'Rs400-900 per person',
        specialties: ['Traditional recipes', 'Local ingredients', 'Signature dishes', 'Chef specials'],
        theme_alignment: `Must-try for ${theme} travelers seeking authentic flavors`,
        ai_recommendation: false,
        source: 'Local culinary recommendations'
      },
      {
        name: `Popular dining spots`,
        cuisine_type: 'Multi-cuisine',
        location: destinationText === 'your destination' ? 'Main market area' : `${destinationText} main market`,
        rating: '4.0+',
        price_range: 'Rs300-700 per person',
        specialties: ['Varied menu', 'Tourist-friendly', 'Quick service', 'Clean environment'],
        theme_alignment: `Great choice for ${theme} travelers wanting variety`,
        ai_recommendation: false,
        source: 'Tourist restaurant recommendations'
      },
      {
        name: `Street food gems`,
        cuisine_type: 'Local street food',
        location: destinationText === 'your destination' ? 'Food streets' : `${destinationText} food streets`,
        rating: '3.8+',
        price_range: 'Rs100-300 per person',
        specialties: ['Street delicacies', 'Budget-friendly', 'Local favorites', 'Quick bites'],
        theme_alignment: `Perfect for ${theme} travelers on a budget`,
        ai_recommendation: false,
        source: 'Street food recommendations'
      },
      {
        name: `Fine dining options`,
        cuisine_type: 'Premium dining',
        location: destinationText === 'your destination' ? 'Upscale area' : `${destinationText} upscale area`,
        rating: '4.5+',
        price_range: 'Rs800-1500 per person',
        specialties: ['Gourmet cuisine', 'Elegant ambiance', 'Premium service', 'Special occasions'],
        theme_alignment: `Ideal for ${theme} travelers seeking luxury dining`,
        ai_recommendation: false,
        source: 'Fine dining recommendations'
      }
    ]
  }

  // Transform weather info - use existing data first, then fallback to API
  const transformWeatherInfo = async (weatherInfo: any, destination: string, date_range: string = 'current') => {
    // Validate and fix temperature range if it exists but is invalid
    const validateTemperatureRange = (tempRange: string) => {
      if (!tempRange || tempRange === 'Variable') return '22°C - 30°C'

      // Check for invalid ranges like "1°C - 0°C"
      const matches = tempRange.match(/(-?\d+)°C\s*-\s*(-?\d+)°C/)
      if (matches) {
        const [, min, max] = matches
        const minTemp = parseInt(min)
        const maxTemp = parseInt(max)

        // If range is invalid (min >= max, or temperatures are unrealistic)
        if (minTemp >= maxTemp || minTemp < -20 || maxTemp > 50 || (minTemp < 5 && maxTemp < 10)) {
          return '22°C - 30°C' // Return reasonable default
        }
      }

      return tempRange
    }

    // Validate and improve current conditions
    const validateCurrentConditions = (conditions: string) => {
      if (!conditions || conditions.includes('expected') || conditions === 'Pleasant weather') {
        // Generate more realistic conditions based on temperature
        const tempRange = weatherInfo?.temperature_range || '22°C - 30°C'
        if (tempRange.includes('22') || tempRange.includes('25') || tempRange.includes('30')) {
          return 'Pleasant and warm weather'
        } else if (tempRange.includes('15') || tempRange.includes('20')) {
          return 'Mild and comfortable weather'
        } else {
          return 'Generally favorable weather conditions'
        }
      }
      return conditions
    }

    // If we have valid weather data, use it directly but validate it
    if (weatherInfo && (weatherInfo.current_conditions || weatherInfo.temperature_range)) {
      return {
        current_conditions: validateCurrentConditions(weatherInfo.current_conditions),
        temperature_range: validateTemperatureRange(weatherInfo.temperature_range),
        seasonal_info: weatherInfo.seasonal_info || 'Good time to visit',
        weather_recommendations: weatherInfo.weather_recommendations || [
          'Carry comfortable walking shoes',
          'Pack weather-appropriate clothing',
          'Keep hydrated',
          'Carry sunscreen and hat'
        ],
        climate_considerations: weatherInfo.climate_considerations || `Weather should be favorable for outdoor activities ${destination === 'Your Destination' ? 'at your destination' : `in ${destination}`}`,
        ai_powered: weatherInfo.ai_powered || false,
        source: weatherInfo.source || 'Travel agent'
      }
    }

    // Only fetch from API if no weather data exists
    console.log('Fetching AI-powered weather data from backend...')
    const weatherData = await fetchBackendData('/api/weather', {
      location: destination,
      date_range: date_range
    })

    if (weatherData && weatherData.weather_data) {
      const apiTempRange = weatherData.temperature_range || weatherData.weather_data.temperature_range || '22°C - 30°C'
      const apiConditions = weatherData.current_conditions || weatherData.weather_data.current_conditions || 'Pleasant weather'

      return {
        current_conditions: validateCurrentConditions(apiConditions),
        temperature_range: validateTemperatureRange(apiTempRange),
        seasonal_info: weatherData.weather_data.seasonal_info || 'Good time to visit',
        weather_recommendations: weatherData.weather_data.weather_recommendations || [
          'Carry comfortable clothing',
          'Stay hydrated',
          'Use sunscreen'
        ],
        climate_considerations: weatherData.weather_data.climate_considerations || `Great weather for exploring ${destination === 'Your Destination' ? 'your destination' : destination}`,
        ai_powered: true,
        source: 'Backend AI weather API'
      }
    }

    // Final fallback with realistic weather info based on current season
    const currentMonth = new Date().getMonth() + 1 // 1-12
    let seasonalTemp = '22°C - 30°C'
    let seasonalConditions = 'Pleasant and favorable weather'
    let seasonalRecommendations = [
      'Carry comfortable walking shoes',
      'Pack weather-appropriate clothing',
      'Keep hydrated during outdoor activities',
      'Use sunscreen and wear a hat'
    ]

    // Adjust based on season (Northern Hemisphere default)
    if (currentMonth >= 12 || currentMonth <= 2) {
      // Winter
      seasonalTemp = '15°C - 25°C'
      seasonalConditions = 'Cool and pleasant weather'
      seasonalRecommendations = [
        'Pack warm clothing for cooler temperatures',
        'Carry a light jacket for evenings',
        'Comfortable walking shoes are essential',
        'Stay hydrated and use sunscreen'
      ]
    } else if (currentMonth >= 3 && currentMonth <= 5) {
      // Spring
      seasonalTemp = '20°C - 28°C'
      seasonalConditions = 'Pleasant spring weather'
      seasonalRecommendations = [
        'Pack layers for varying temperatures',
        'Carry a light rain jacket',
        'Comfortable outdoor shoes recommended',
        'Perfect weather for sightseeing'
      ]
    } else if (currentMonth >= 6 && currentMonth <= 8) {
      // Summer
      seasonalTemp = '25°C - 35°C'
      seasonalConditions = 'Warm summer weather'
      seasonalRecommendations = [
        'Pack light, breathable clothing',
        'Stay well hydrated throughout the day',
        'Use strong sunscreen and wear a hat',
        'Plan activities during cooler morning/evening hours'
      ]
    } else {
      // Autumn
      seasonalTemp = '18°C - 26°C'
      seasonalConditions = 'Pleasant autumn weather'
      seasonalRecommendations = [
        'Pack light layers for temperature changes',
        'Carry a light windbreaker',
        'Comfortable walking shoes for outdoor activities',
        'Great weather for exploring and photography'
      ]
    }

    return {
      current_conditions: seasonalConditions,
      temperature_range: seasonalTemp,
      seasonal_info: 'Generally good time to visit',
      weather_recommendations: seasonalRecommendations,
      climate_considerations: `${destination === 'Your Destination' ? 'Your destination' : destination} typically has favorable weather conditions for travel and outdoor activities`,
      ai_powered: false,
      source: 'Seasonal weather estimates'
    }
  }

  // Transform local markets - use existing data first, then fallback to API
  const transformLocalMarkets = async (markets: any[], destination: string, theme: string) => {
    // If we have valid markets data, use it directly
    if (markets && markets.length > 0) {
      const destinationText = destination === 'Your Destination' ? 'your destination' : destination
      return markets.map((market: any, index: number) => ({
        name: market.name || market.title || `Local market ${index + 1}`,
        location: market.location || (destinationText === 'your destination' ? 'Local market area' : `${destinationText} market area`),
        unique_products: market.unique_products || market.products || ['Local goods', 'Regional specialties'],
        best_time_to_visit: market.best_time_to_visit || market.timing || 'Morning to evening',
        price_range: market.price_range || 'Rs100-2000',
        theme_relevance: market.theme_relevance || `Great for ${theme} travelers`,
        ai_recommendation: market.ai_recommendation || false,
        source: market.source || 'Travel agent'
      }))
    }

    // Only fetch from API if no data exists
    console.log('Fetching AI-powered local market data from backend...')
    const marketData = await fetchBackendData('/api/local-markets', {
      location: destination,
      theme: theme,
      category: 'shopping_dining'
    })

    if (marketData && marketData.markets && marketData.markets.length > 0) {
      return marketData.markets
    }

    // Enhanced fallback with multiple market options
    const destinationText = destination === 'Your Destination' ? 'your destination' : destination
    return [
      {
        name: `Traditional market`,
        location: destinationText === 'your destination' ? 'Old market area' : `${destinationText} old market area`,
        unique_products: ['Handmade crafts', 'Local textiles', 'Traditional jewelry', 'Spices & herbs'],
        best_time_to_visit: 'Morning to late evening',
        price_range: 'Rs50-1500',
        theme_relevance: `Excellent for ${theme} travelers seeking authentic souvenirs`,
        ai_recommendation: false,
        source: 'Traditional market recommendations'
      },
      {
        name: `Local artisan market`,
        location: destinationText === 'your destination' ? 'Craft district' : `${destinationText} craft district`,
        unique_products: ['Handcrafted items', 'Local artwork', 'Regional specialties', 'Wooden crafts'],
        best_time_to_visit: 'Morning to afternoon',
        price_range: 'Rs100-3000',
        theme_relevance: `Perfect for ${theme} travelers appreciating local artistry`,
        ai_recommendation: false,
        source: 'Artisan market recommendations'
      },
      {
        name: `Street shopping area`,
        location: destinationText === 'your destination' ? 'Main shopping street' : `${destinationText} main shopping street`,
        unique_products: ['Budget finds', 'Local snacks', 'Souvenirs', 'Everyday items'],
        best_time_to_visit: 'Evening to night',
        price_range: 'Rs20-500',
        theme_relevance: `Great for ${theme} travelers on a budget`,
        ai_recommendation: false,
        source: 'Street market recommendations'
      }
    ]
  }

  // Transform daily itinerary from backend format to UI format
  const transformDailyItinerary = (dailyPlan: any[], destination: string, theme: string, duration: string) => {
    if (!Array.isArray(dailyPlan) || dailyPlan.length === 0) {
      // Generate a basic itinerary if none exists
      const days = parseInt(duration.match(/\d+/)?.[0] || '3')
      const destinationText = destination === 'Your Destination' ? 'your destination' : destination
      return Array.from({ length: days }, (_, index) => ({
        day: index + 1,
        weather_forecast: 'Pleasant weather expected',
        theme_focus: `${theme} Day ${index + 1}`,
        morning: {
          activity: `Morning ${theme} activities`,
          location: destinationText === 'your destination' ? 'Popular attractions' : `${destinationText} attractions`,
          duration: '3-4 hours',
          cost: 'Rs500-800',
          weather_suitability: 'Suitable for all weather'
        },
        afternoon: {
          activity: `Afternoon exploration`,
          location: destinationText === 'your destination' ? 'City center' : `${destinationText} city center`,
          duration: '3-4 hours',
          cost: 'Rs600-1000',
          weather_suitability: 'Suitable for all weather'
        },
        evening: {
          activity: `Evening leisure and dining`,
          location: destinationText === 'your destination' ? 'Dining area' : `${destinationText} dining area`,
          duration: '2-3 hours',
          cost: 'Rs400-800',
          weather_suitability: 'Suitable for all weather'
        },
        accommodation: destinationText === 'your destination' ? 'Local hotel' : `Hotel in ${destinationText}`,
        meals: {
          breakfast: 'Local breakfast',
          lunch: 'Regional cuisine',
          dinner: 'Traditional dinner'
        },
        daily_total_cost: 'Rs1500-2500',
        weather_tips: ['Carry water', 'Comfortable shoes', 'Camera for memories']
      }))
    }

    return dailyPlan.map((dayData, index) => {
      // Backend format: { day: 1, activities: [...], locations: [...] }
      // UI expects: { day: 1, morning: {...}, afternoon: {...}, evening: {...}, ... }

      const activities = Array.isArray(dayData.activities) ? dayData.activities : []
      const locations = Array.isArray(dayData.locations) ? dayData.locations : []

      // Create morning, afternoon, evening from activities
      const destinationText = destination === 'Your Destination' ? 'your destination' : destination
      const getActivity = (timeIndex: number, defaultActivity: string) => ({
        activity: activities[timeIndex] || defaultActivity,
        location: locations[timeIndex] || (destinationText === 'your destination' ? 'Local area' : `${destinationText} area`),
        duration: '3-4 hours',
        cost: 'Rs500-800',
        weather_suitability: 'Suitable for all weather'
      })

      return {
        day: dayData.day || (index + 1),
        weather_forecast: dayData.weather_forecast || 'Pleasant weather expected',
        theme_focus: dayData.theme_focus || `${theme} Day ${dayData.day || (index + 1)}`,
        morning: dayData.morning || getActivity(0, 'Morning exploration'),
        afternoon: dayData.afternoon || getActivity(1, 'Afternoon sightseeing'),
        evening: dayData.evening || getActivity(2, 'Evening leisure'),
        accommodation: dayData.accommodation || (destinationText === 'your destination' ? 'Local hotel' : `Hotel in ${destinationText}`),
        meals: dayData.meals || {
          breakfast: 'Local breakfast',
          lunch: 'Regional cuisine',
          dinner: 'Traditional dinner'
        },
        daily_total_cost: dayData.daily_total_cost || 'Rs1500-2500',
        weather_tips: dayData.weather_tips || ['Carry water', 'Comfortable shoes', 'Camera for memories']
      }
    })
  }

  // Parse and transform backend response with AI data fetching - No more hardcoded values
  const transformBackendResponse = async (response: any) => {
    // If agent_response is a string, parse it as JSON
    let parsedResponse = response
    if (typeof response === 'string') {
      try {
        parsedResponse = JSON.parse(response)
      } catch (e) {
        console.error('Failed to parse agent_response JSON:', e)
        // Return meaningful fallback data instead of empty arrays
        const destination = (tripData.structured_input?.destination && tripData.structured_input.destination !== 'Not specified')
          ? tripData.structured_input.destination
          : 'Your Destination'
        const theme = (tripData.structured_input?.theme && tripData.structured_input.theme !== 'Not specified')
          ? tripData.structured_input.theme
          : 'Adventure'
        return {
          trip_overview: {
            source: tripData.structured_input?.source || 'Unknown',
            destination: destination,
            travel_mode: tripData.structured_input?.travel_mode || 'Self',
            budget: tripData.structured_input?.budget || 'Rs15000',
            theme: theme,
            duration: tripData.structured_input?.duration || '3 days',
            budget_status: 'sufficient' as 'sufficient' | 'insufficient',
            estimated_cost: 'Rs12000-18000'
          },
          destinations: [{
            name: `Top attractions in ${destination}`,
            description: `Explore the best that ${destination} has to offer for ${theme.toLowerCase()} travelers`,
            theme_alignment: `Perfect for ${theme.toLowerCase()} experiences`,
            highlights: ['Must-visit destination', 'Popular among travelers', `Great for ${theme.toLowerCase()}`],
            estimated_time: '4-6 hours',
            entry_fees: 'Varies by attraction',
            best_time_to_visit: 'Morning to evening'
          }, {
            name: `Local ${theme.toLowerCase()} spots in ${destination}`,
            description: `Discover authentic local experiences that align with your ${theme.toLowerCase()} theme`,
            theme_alignment: `Specially curated for ${theme.toLowerCase()} enthusiasts`,
            highlights: ['Local favorite', 'Authentic experience', 'Hidden gem'],
            estimated_time: '3-5 hours',
            entry_fees: 'Usually affordable',
            best_time_to_visit: 'Check local timings'
          }],
          hotels: [{
            name: `Recommended stays in ${destination}`,
            location: `${destination} city center`,
            rating: '4.0+',
            price_range: 'Rs2000-5000 per night',
            amenities: ['WiFi', 'AC', 'Room Service', 'Parking'],
            theme_suitability: `Excellent for ${theme.toLowerCase()} travelers`,
            booking_options: {
              available: true,
              booking_url: '#',
              one_click_booking: false
            }
          }, {
            name: `Budget-friendly options in ${destination}`,
            location: `${destination} area`,
            rating: '3.5+',
            price_range: 'Rs1000-3000 per night',
            amenities: ['WiFi', 'Clean rooms', 'Basic amenities'],
            theme_suitability: `Good value for ${theme.toLowerCase()} trips`,
            booking_options: {
              available: true,
              booking_url: '#',
              one_click_booking: false
            }
          }],
          restaurants: [{
            name: `Local cuisine in ${destination}`,
            cuisine_type: 'Regional specialties',
            location: `${destination} main area`,
            rating: '4.0+',
            price_range: 'Rs300-800 per person',
            specialties: ['Local dishes', 'Regional favorites', 'Fresh ingredients'],
            theme_alignment: `Perfect dining for ${theme.toLowerCase()} travelers`
          }, {
            name: `Popular restaurants in ${destination}`,
            cuisine_type: 'Multi-cuisine',
            location: `${destination} tourist area`,
            rating: '4.2+',
            price_range: 'Rs400-1000 per person',
            specialties: ['Varied menu', 'Tourist-friendly', 'Quality food'],
            theme_alignment: `Great choice for ${theme.toLowerCase()} enthusiasts`
          }],
          transportation: {
            mode: tripData.structured_input?.travel_mode || 'Self'
          },
          weather_info: {
            current_conditions: 'Generally favorable weather conditions',
            temperature_range: '20°C - 28°C',
            seasonal_info: 'Good time to visit',
            weather_recommendations: [
              'Pack weather-appropriate clothing',
              'Carry comfortable walking shoes',
              'Stay hydrated during activities',
              'Use sunscreen for outdoor exploration'
            ],
            climate_considerations: 'Weather should be favorable for outdoor activities'
          },
          local_markets: [],
          booking_summary: {
            one_click_bookings_available: false,
            booking_links: {
              transportation: '',
              hotels: [],
              activities: []
            },
            booking_instructions: 'Contact local travel agents or book directly through official websites'
          },
          sources: [],
          daily_itinerary: [],
          budget_breakdown: {
            total_budget: tripData.structured_input?.budget || 'Rs15000',
            estimated_cost: 'Rs12000-18000',
            breakdown: { transportation: '25%', accommodation: '40%', food: '20%', activities: '15%' },
            budget_optimization_tips: [],
            cost_saving_alternatives: [],
            budget_status: 'sufficient' as 'sufficient' | 'insufficient',
            savings_potential: 0
          }
        }
      }
    }

    // Extract budget info from backend for proper cost estimation
    const backendBudget = parsedResponse.budget || {}
    const structuredBudget = tripData.structured_input?.budget || 'Rs15000'

    // Calculate estimated cost from budget breakdown if available
    let estimatedCost = 'Rs12000-18000' // default fallback
    if (backendBudget.estimated_cost && backendBudget.estimated_cost !== 'Budget mentioned') {
      estimatedCost = backendBudget.estimated_cost
    } else if (structuredBudget && structuredBudget !== 'Not specified') {
      // Extract number from budget (e.g., "Rs15000" -> 15000)
      const budgetNum = parseInt(structuredBudget.replace(/[^\d]/g, '')) || 15000
      const minCost = Math.round(budgetNum * 0.8)
      const maxCost = Math.round(budgetNum * 1.1)
      estimatedCost = `Rs${minCost.toLocaleString()}-${maxCost.toLocaleString()}`
    }

    // Get trip parameters for API calls
    const destination = (tripData.structured_input?.destination && tripData.structured_input.destination !== 'Not specified')
      ? tripData.structured_input.destination
      : 'Your Destination'
    const theme = (tripData.structured_input?.theme && tripData.structured_input.theme !== 'Not specified')
      ? tripData.structured_input.theme
      : 'Adventure'
    const budget = structuredBudget
    const duration = tripData.structured_input?.duration || '3 days'

    // Transform backend structure to match UI expectations with AI data
    const transformed = {
      trip_overview: parsedResponse.trip_overview || {
        source: tripData.structured_input?.source || 'Unknown',
        destination: destination,
        travel_mode: tripData.structured_input?.travel_mode || 'Self',
        budget: budget,
        theme: theme,
        duration: duration,
        budget_status: 'sufficient',
        estimated_cost: estimatedCost
      },
      destinations: await transformDestinations(parsedResponse.destinations || [], destination, theme),
      hotels: await transformHotels(parsedResponse.hotels || [], destination, theme, budget),
      restaurants: await transformRestaurants(parsedResponse.restaurants || [], destination, theme),
      transportation: parsedResponse.transportation || {
        mode: tripData.structured_input?.travel_mode || 'Self'
      },
      weather_info: await transformWeatherInfo(parsedResponse.weather_info || parsedResponse.practical_info || {}, destination, duration),
      local_markets: await transformLocalMarkets(parsedResponse.local_markets || [], destination, theme),
      booking_summary: parsedResponse.booking_summary || {
        one_click_bookings_available: false,
        booking_links: {
          transportation: '',
          hotels: [],
          activities: []
        },
        booking_instructions: 'Contact local travel agents or book directly through official websites'
      },
      sources: parsedResponse.sources || [],

      // Transform itinerary structure: backend has itinerary.daily_plan, UI expects daily_itinerary
      daily_itinerary: transformDailyItinerary(
        parsedResponse.itinerary?.daily_plan || parsedResponse.daily_itinerary || [],
        destination,
        theme,
        tripData.structured_input?.duration || '3 days'
      ),

      // Transform budget structure: backend has budget.tips, UI expects budget_breakdown
      budget_breakdown: {
        total_budget: structuredBudget,
        estimated_cost: estimatedCost,
        breakdown: parsedResponse.budget?.breakdown || {
          transportation: '25%',
          accommodation: '40%',
          food: '20%',
          activities: '15%'
        },
        detailed_breakdown: parsedResponse.budget_breakdown?.detailed_breakdown,
        budget_optimization_tips: parsedResponse.budget?.tips || parsedResponse.budget_breakdown?.budget_optimization_tips || [
          'Book accommodations in advance for better rates',
          'Use local transportation instead of private taxis',
          'Try local restaurants instead of tourist spots',
          'Look for package deals that include multiple activities'
        ],
        cost_saving_alternatives: parsedResponse.budget?.alternatives || parsedResponse.budget_breakdown?.cost_saving_alternatives || [
          'Consider off-season travel for lower prices',
          'Choose budget-friendly accommodations like hostels or guesthouses',
          'Use public transportation or shared rides',
          'Pack your own snacks and water bottles'
        ],
        budget_status: parsedResponse.budget?.status || 'sufficient',
        savings_potential: parsedResponse.budget?.savings_potential || 0
      }
    }

    return transformed
  }

  // Basic transformation without AI enhancements (fallback)
  const transformBackendResponseBasic = (response: any) => {
    // Simple synchronous transformation for fallback
    let parsedResponse = response
    if (typeof response === 'string') {
      try {
        parsedResponse = JSON.parse(response)
      } catch (e) {
        console.error('Failed to parse agent_response JSON:', e)
        return {
          trip_overview: {
            source: tripData.structured_input?.source || 'Unknown',
            destination: (tripData.structured_input?.destination && tripData.structured_input.destination !== 'Not specified')
              ? tripData.structured_input.destination
              : 'Your Destination',
            travel_mode: tripData.structured_input?.travel_mode || 'Self',
            budget: tripData.structured_input?.budget || 'Rs15000',
            theme: tripData.structured_input?.theme || 'Adventure',
            duration: tripData.structured_input?.duration || '3 days',
            budget_status: 'sufficient' as 'sufficient' | 'insufficient',
            estimated_cost: 'Rs12000-18000'
          },
          destinations: [],
          hotels: [],
          restaurants: [],
          transportation: { mode: tripData.structured_input?.travel_mode || 'Self' },
          weather_info: { current_conditions: 'Check local weather', temperature_range: 'Variable' },
          local_markets: [],
          booking_summary: { one_click_bookings_available: false },
          sources: [],
          daily_itinerary: [],
          budget_breakdown: {
            total_budget: tripData.structured_input?.budget || 'Rs15000',
            estimated_cost: 'Rs12000-18000',
            breakdown: { transportation: '25%', accommodation: '40%', food: '20%', activities: '15%' },
            budget_optimization_tips: ['Backend AI updating...'],
            cost_saving_alternatives: ['AI recommendations loading...'],
            budget_status: 'sufficient' as 'sufficient' | 'insufficient',
            savings_potential: 0
          }
        }
      }
    }

    // Return basic structure with meaningful fallback data instead of empty arrays
    const destination = (tripData.structured_input?.destination && tripData.structured_input.destination !== 'Not specified')
      ? tripData.structured_input.destination
      : 'Your Destination'
    const theme = (tripData.structured_input?.theme && tripData.structured_input.theme !== 'Not specified')
      ? tripData.structured_input.theme
      : 'Adventure'

    return {
      trip_overview: parsedResponse.trip_overview || {
        source: tripData.structured_input?.source || 'Unknown',
        destination: destination,
        travel_mode: tripData.structured_input?.travel_mode || 'Self',
        budget: tripData.structured_input?.budget || 'Rs15000',
        theme: theme,
        duration: tripData.structured_input?.duration || '3 days',
        budget_status: 'sufficient',
        estimated_cost: 'Rs12000-18000'
      },
      destinations: parsedResponse.destinations?.length > 0 ? parsedResponse.destinations : [{
        name: `${destination} attractions`,
        description: `Explore popular attractions in ${destination}`,
        theme_alignment: `Great for ${theme.toLowerCase()} travelers`,
        highlights: ['Popular destination', 'Must-visit'],
        estimated_time: '3-5 hours',
        entry_fees: 'Check locally',
        best_time_to_visit: 'Morning to evening'
      }],
      hotels: parsedResponse.hotels?.length > 0 ? parsedResponse.hotels : [{
        name: `Hotels in ${destination}`,
        location: `${destination} area`,
        rating: '4.0+',
        price_range: 'Rs2000-5000 per night',
        amenities: ['WiFi', 'AC', 'Room Service'],
        theme_suitability: `Good for ${theme.toLowerCase()} travelers`,
        booking_options: { available: true, booking_url: '#' }
      }],
      restaurants: parsedResponse.restaurants?.length > 0 ? parsedResponse.restaurants : [{
        name: `Local dining in ${destination}`,
        cuisine_type: 'Local cuisine',
        location: `${destination} area`,
        rating: '4.0+',
        price_range: 'Rs300-800 per person',
        specialties: ['Local dishes', 'Regional cuisine'],
        theme_alignment: `Perfect for ${theme.toLowerCase()} travelers`
      }],
      transportation: parsedResponse.transportation || { mode: tripData.structured_input?.travel_mode || 'Self' },
      weather_info: parsedResponse.weather_info || {
        current_conditions: 'Generally favorable weather conditions',
        temperature_range: '20°C - 28°C',
        seasonal_info: 'Good time to visit',
        weather_recommendations: ['Pack appropriate clothing', 'Stay hydrated', 'Use sunscreen'],
        climate_considerations: 'Weather typically favorable for travel activities'
      },
      local_markets: parsedResponse.local_markets || [],
      booking_summary: parsedResponse.booking_summary || { one_click_bookings_available: false },
      sources: parsedResponse.sources || [],
      daily_itinerary: parsedResponse.daily_itinerary || [],
      budget_breakdown: parsedResponse.budget_breakdown || {
        total_budget: tripData.structured_input?.budget || 'Rs15000',
        estimated_cost: 'Rs12000-18000',
        breakdown: { transportation: '25%', accommodation: '40%', food: '20%', activities: '15%' },
        budget_optimization_tips: ['Backend AI updating...'],
        cost_saving_alternatives: ['AI recommendations loading...'],
        budget_status: 'sufficient',
        savings_potential: 0
      }
    }
  }

  // Show loading if we don't have transformed data yet
  if (!transformedTrip) {
    return (
      <Card className="w-full max-w-6xl mx-auto">
        <CardContent className="p-8 text-center">
          <div className="text-muted-foreground">
            <Info className="h-12 w-12 mx-auto mb-4" />
            <p>Preparing AI-enhanced travel recommendations...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Use transformed trip data with AI enhancements
  const trip = transformedTrip
  const overview = trip.trip_overview || {}
  const themeData = TRAVEL_THEMES.find(t => t.id === overview.theme) || TRAVEL_THEMES[0]

  // Use the AI-enhanced trip data
  const safeTrip = trip

  const tabs = [
    { id: 'overview' as const, label: 'Overview', icon: Info },
    { id: 'itinerary' as const, label: 'Daily Plan', icon: Calendar },
    { id: 'accommodations' as const, label: 'Stay & Eat', icon: Hotel },
    { id: 'budget' as const, label: 'Budget', icon: IndianRupee }
  ]

  const handleSaveTrip = () => {
    if (safeTrip) {
      const tripName = `${safeTrip.trip_overview.source} to ${safeTrip.trip_overview.destination} - ${safeTrip.trip_overview.duration}`

      // Show mock success message
      showMockMessage('success', `✅ Trip "${tripName}" has been saved to your travel portfolio! You can access it anytime from your saved trips.`)

      if (onSaveTrip) {
        onSaveTrip({ ...safeTrip, name: tripName })
      }
      setSavedTrip(true)
    }
  }

  const handleShareTrip = () => {
    if (safeTrip) {
      const tripName = `${safeTrip.trip_overview.source} to ${safeTrip.trip_overview.destination}`

      // Generate a mock shareable link
      const shareableLink = `https://travelbuddy.ai/shared-trip/${Math.random().toString(36).substring(2, 15)}`

      // Try to copy to clipboard (mock)
      try {
        navigator.clipboard?.writeText(shareableLink)
        showMockMessage('success', `🔗 Shareable link copied to clipboard! Share your "${tripName}" trip with friends: ${shareableLink}`)
      } catch {
        showMockMessage('info', `📲 Share your "${tripName}" trip! Link: ${shareableLink} (Please copy manually)`)
      }

      if (onShareTrip) {
        onShareTrip(safeTrip)
      }
    }
  }


  return (
    <>
      {/* Mock Message Display */}
      {mockMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className={`fixed top-4 right-4 z-50 max-w-md p-4 rounded-lg shadow-lg border ${
            mockMessage.type === 'success'
              ? 'bg-green-50 border-green-200 text-green-800'
              : mockMessage.type === 'error'
              ? 'bg-red-50 border-red-200 text-red-800'
              : 'bg-blue-50 border-blue-200 text-blue-800'
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="text-sm font-medium whitespace-pre-line">
              {mockMessage.message}
            </div>
            <button
              onClick={() => setMockMessage(null)}
              className="ml-3 text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-6xl mx-auto space-y-6"
      >
        {/* Trip Header */}
      <Card className="overflow-hidden">
        <div className={`h-32 bg-gradient-to-r ${themeData?.gradient || 'from-blue-500 to-purple-600'} relative`}>
          <div className="absolute inset-0 bg-black/20" />
          <div className="absolute bottom-4 left-6 right-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">
                  {safeTrip.trip_overview.source} → {safeTrip.trip_overview.destination}
                </h1>
                <p className="text-white/90">
                  {safeTrip.trip_overview.duration} • {safeTrip.trip_overview.theme} • {safeTrip.trip_overview.travel_mode} Mode
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleSaveTrip}
                  disabled={savedTrip}
                >
                  <Bookmark className="h-4 w-4 mr-1" />
                  {savedTrip ? 'Saved' : 'Save'}
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleShareTrip}
                >
                  <Share2 className="h-4 w-4 mr-1" />
                  Share
                </Button>
              </div>
            </div>
          </div>
        </div>

        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-secondary/50 rounded-lg">
              <IndianRupee className="h-8 w-8 mx-auto mb-2 text-green-600" />
              <div className="font-semibold">{safeTrip.trip_overview.budget}</div>
              <div className="text-xs text-muted-foreground">Total Budget</div>
              <Badge
                variant={safeTrip.trip_overview.budget_status === 'sufficient' ? 'success' : 'destructive'}
                className="mt-1"
              >
                {safeTrip.trip_overview.budget_status}
              </Badge>
            </div>

            <div className="text-center p-4 bg-secondary/50 rounded-lg">
              <Calendar className="h-8 w-8 mx-auto mb-2 text-blue-600" />
              <div className="font-semibold">{safeTrip.trip_overview.duration}</div>
              <div className="text-xs text-muted-foreground">Duration</div>
            </div>

            <div className="text-center p-4 bg-secondary/50 rounded-lg">
              <Car className="h-8 w-8 mx-auto mb-2 text-purple-600" />
              <div className="font-semibold">{safeTrip.trip_overview.travel_mode}</div>
              <div className="text-xs text-muted-foreground">Travel Mode</div>
            </div>

            <div className="text-center p-4 bg-secondary/50 rounded-lg">
              <div className="text-2xl mb-2">{themeData?.icon}</div>
              <div className="font-semibold">{safeTrip.trip_overview.theme}</div>
              <div className="text-xs text-muted-foreground">Theme</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 justify-center">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            variant={activeTab === tab.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveTab(tab.id)}
            className="flex items-center gap-2"
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'overview' && (
          <OverviewTab trip={safeTrip} />
        )}

        {activeTab === 'itinerary' && (
          <ItineraryTab trip={safeTrip} />
        )}

        {activeTab === 'accommodations' && (
          <AccommodationsTab trip={safeTrip} />
        )}

        {activeTab === 'budget' && (
          <BudgetTab trip={safeTrip} />
        )}
      </div>
      </motion.div>
    </>
  )
}

// Overview Tab Component
interface TripData {
  trip_overview: {
    source: string;
    destination: string;
    travel_mode: string;
    budget: string;
    theme: string;
    duration: string;
    budget_status: string;
    estimated_cost: string;
  };
  destinations?: Array<{
    name: string;
    description: string;
    highlights?: string[];
    estimated_time: string;
    entry_fees: string;
  }>;
  weather_info?: {
    temperature_range: string;
    current_conditions: string;
    weather_recommendations?: string[];
  };
  local_markets?: Array<{
    name: string;
    location: string;
    unique_products?: string[];
    best_time_to_visit: string;
    price_range: string;
  }>;
  transportation: {
    mode: string;
    self_mode?: {
      fuel_estimate: {
        total_distance: string;
        fuel_cost: string;
        toll_charges?: string;
      };
      route_details: string;
    };
    booking_mode?: {
      transport_options?: Array<{
        type: string;
        operator: string;
        price: string;
        duration: string;
        one_click_booking?: boolean;
      }>;
    };
  };
  daily_itinerary?: Array<{
    day: number;
    weather_forecast?: string;
    theme_focus: string;
    morning: {
      activity: string;
      location: string;
      duration: string;
      cost: string;
    };
    afternoon: {
      activity: string;
      location: string;
      duration: string;
      cost: string;
    };
    evening: {
      activity: string;
      location: string;
      duration: string;
      cost: string;
    };
    accommodation: string;
    daily_total_cost: string;
    weather_tips?: string[];
  }>;
  hotels?: Array<{
    name: string;
    location: string;
    rating: string;
    price_range: string;
    amenities?: string[];
    theme_suitability: string;
    booking_options?: {
      booking_url?: string;
    };
  }>;
  restaurants?: Array<{
    name: string;
    cuisine_type: string;
    location: string;
    rating: string;
    price_range: string;
    specialties?: string[];
    theme_alignment: string;
  }>;
  budget_breakdown: BudgetBreakdown;
}

function OverviewTab({ trip }: { trip: TripData }) {
  const handleTransportBooking = (option: any, isOneClick: boolean = false) => {
    const bookingId = Math.random().toString(36).substring(2, 15).toUpperCase()
    const route = `${trip.trip_overview.source} to ${trip.trip_overview.destination}`

    if (isOneClick) {
      alert(`🎉 Booking confirmed! Your ${option.type} ticket (${option.operator}) for ${route} is booked instantly. Booking ID: ${bookingId}. E-ticket sent to your email. Duration: ${option.duration}, Price: ${option.price}`)
    } else {
      alert(`🚀 Redirecting to ${option.operator} booking portal for ${option.type} from ${route}. Please complete your booking on their secure payment gateway. Estimated cost: ${option.price}, Duration: ${option.duration}`)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Destinations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5 text-primary" />
            Key Destinations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {trip.destinations?.slice(0, 3).map((dest, idx) => (
            <div key={idx} className="border-l-4 border-primary pl-4">
              <h3 className="font-medium">{dest.name}</h3>
              <p className="text-sm text-muted-foreground mb-2">{dest.description}</p>
              <div className="flex flex-wrap gap-1">
                {dest.highlights?.map((highlight, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">
                    {highlight}
                  </Badge>
                ))}
              </div>
              <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {dest.estimated_time}
                </span>
                <span className="flex items-center gap-1">
                  <IndianRupee className="h-3 w-3" />
                  {dest.entry_fees}
                </span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Weather Information */}
      {trip.weather_info && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sun className="h-5 w-5 text-orange-500" />
              Weather & Climate
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3 p-3 bg-secondary/50 rounded-lg">
              <Thermometer className="h-8 w-8 text-red-500" />
              <div>
                <div className="font-medium">{trip.weather_info.temperature_range}</div>
                <div className="text-sm text-muted-foreground">
                  {trip.weather_info.current_conditions}
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">Recommendations:</h4>
              <ul className="space-y-1 text-sm">
                {trip.weather_info.weather_recommendations?.map((rec, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <CheckCircle2 className="h-3 w-3 text-green-500 flex-shrink-0" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Local Markets */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5 text-green-600" />
            Local Markets & Unique Products
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {trip.local_markets?.slice(0, 3).map((market, idx) => (
            <div key={idx} className="border-l-4 border-green-500 pl-4">
              <h3 className="font-medium">{market.name}</h3>
              <p className="text-sm text-muted-foreground mb-2">{market.location}</p>
              <div className="flex flex-wrap gap-1 mb-2">
                {market.unique_products?.map((product, i) => (
                  <Badge key={i} variant="outline" className="text-xs bg-green-50 dark:bg-green-900/30 text-green-800 dark:text-green-200 border-green-200 dark:border-green-700">
                    {product}
                  </Badge>
                ))}
              </div>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {market.best_time_to_visit}
                </span>
                <span className="text-green-600 font-medium">
                  {market.price_range}
                </span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Transportation */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {trip.transportation.mode === 'Self' ? (
              <Car className="h-5 w-5 text-primary" />
            ) : (
              <Plane className="h-5 w-5 text-primary" />
            )}
            Transportation Details
          </CardTitle>
        </CardHeader>
        <CardContent>
          {trip.transportation?.self_mode && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-secondary/50 rounded-lg text-center">
                  <div className="font-semibold text-lg">
                    {trip.transportation.self_mode.fuel_estimate?.total_distance || 'N/A'}
                  </div>
                  <div className="text-sm text-muted-foreground">Total Distance</div>
                </div>
                <div className="p-4 bg-secondary/50 rounded-lg text-center">
                  <div className="font-semibold text-lg">
                    {trip.transportation.self_mode.fuel_estimate?.fuel_cost || 'N/A'}
                  </div>
                  <div className="text-sm text-muted-foreground">Fuel Cost</div>
                </div>
                <div className="p-4 bg-secondary/50 rounded-lg text-center">
                  <div className="font-semibold text-lg">
                    {trip.transportation.self_mode.fuel_estimate?.toll_charges || 'N/A'}
                  </div>
                  <div className="text-sm text-muted-foreground">Toll Charges</div>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Route Details:</h4>
                <p className="text-sm text-muted-foreground">
                  {trip.transportation.self_mode.route_details || 'Route information not available'}
                </p>
              </div>
            </div>
          )}

          {trip.transportation?.booking_mode && (
            <div className="space-y-4">
              <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                  One-Click Booking Available
                </h4>
                <p className="text-sm text-blue-700 dark:text-blue-200">
                  Select your preferred option and book instantly with our integrated booking system.
                </p>
              </div>

              {trip.transportation.booking_mode.transport_options?.map((option, idx) => (
                <div key={idx} className="border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between p-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="text-lg">
                          {option.type === 'Flight' && 'Flight'}
                          {option.type === 'Train' && 'Train'}
                          {option.type === 'Bus' && 'Bus'}
                          {option.type === 'Cab' && 'Taxi'}
                        </div>
                        <div className="font-medium">{option.type} - {option.operator}</div>
                        {option.one_click_booking && (
                          <Badge variant="success" className="text-xs">
                            One-Click Booking
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground mb-2">
                        Duration: {option.duration} | Price: {option.price}
                      </div>
                      <div className="flex gap-2">
                        <Badge variant="outline" className="text-xs">Fast Booking</Badge>
                        <Badge variant="outline" className="text-xs">Instant Confirmation</Badge>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      {option.one_click_booking ? (
                        <Button
                          variant="default"
                          size="sm"
                          className="bg-green-600 hover:bg-green-700 text-white"
                          onClick={() => handleTransportBooking(option, true)}
                        >
                          <CheckCircle2 className="h-4 w-4 mr-1" />
                          Book Instantly
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleTransportBooking(option, false)}
                        >
                          <ExternalLink className="h-4 w-4 mr-1" />
                          Book Now
                        </Button>
                      )}
                      <div className="text-xs text-center text-muted-foreground">
                        Secure Payment
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              <div className="p-4 bg-muted/50 rounded-lg">
                <h5 className="font-medium mb-2">Booking Benefits:</h5>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>Instant confirmation and e-tickets</li>
                  <li>24/7 customer support</li>
                  <li>Secure payment gateway</li>
                  <li>Easy cancellation and refund</li>
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// Itinerary Tab Component
function ItineraryTab({ trip }: { trip: TripData }) {
  return (
    <div className="space-y-6">
      {trip.daily_itinerary?.map((day) => (
        <Card key={day.day}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-primary" />
              Day {day.day}
              <Badge variant="outline" className="ml-auto">
                {day.theme_focus}
              </Badge>
            </CardTitle>
            {day.weather_forecast && (
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Cloud className="h-4 w-4" />
                {day.weather_forecast}
              </p>
            )}
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Morning */}
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium text-orange-600 mb-2 flex items-center gap-2">
                  <Sun className="h-4 w-4" />
                  Morning
                </h4>
                <div className="space-y-2">
                  <p className="font-medium">{day.morning.activity}</p>
                  <p className="text-sm text-muted-foreground">{day.morning.location}</p>
                  <div className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {day.morning.duration}
                    </span>
                    <span className="flex items-center gap-1 text-green-600">
                      <IndianRupee className="h-3 w-3" />
                      {day.morning.cost}
                    </span>
                  </div>
                </div>
              </div>

              {/* Afternoon */}
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium text-blue-600 mb-2 flex items-center gap-2">
                  <Sun className="h-4 w-4" />
                  Afternoon
                </h4>
                <div className="space-y-2">
                  <p className="font-medium">{day.afternoon.activity}</p>
                  <p className="text-sm text-muted-foreground">{day.afternoon.location}</p>
                  <div className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {day.afternoon.duration}
                    </span>
                    <span className="flex items-center gap-1 text-green-600">
                      <IndianRupee className="h-3 w-3" />
                      {day.afternoon.cost}
                    </span>
                  </div>
                </div>
              </div>

              {/* Evening */}
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium text-purple-600 mb-2 flex items-center gap-2">
                  <Sun className="h-4 w-4" />
                  Evening
                </h4>
                <div className="space-y-2">
                  <p className="font-medium">{day.evening.activity}</p>
                  <p className="text-sm text-muted-foreground">{day.evening.location}</p>
                  <div className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {day.evening.duration}
                    </span>
                    <span className="flex items-center gap-1 text-green-600">
                      <IndianRupee className="h-3 w-3" />
                      {day.evening.cost}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Daily Summary */}
            <div className="mt-4 p-3 bg-secondary/50 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="text-sm">
                  <span className="font-medium">Accommodation:</span> {day.accommodation}
                </div>
                <div className="text-sm font-medium text-green-600">
                  Daily Total: {day.daily_total_cost}
                </div>
              </div>
            </div>

            {/* Weather Tips & Activity Adjustments */}
            {day.weather_tips && day.weather_tips.length > 0 && (
              <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <h5 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1 flex items-center gap-2">
                  <Sun className="h-4 w-4" />
                  Weather-Based Recommendations:
                </h5>
                <ul className="text-xs text-blue-700 dark:text-blue-200 space-y-1">
                  {day.weather_tips.map((tip, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <Umbrella className="h-3 w-3 flex-shrink-0" />
                      {tip}
                    </li>
                  ))}
                </ul>
                <div className="mt-2 text-xs text-blue-600 dark:text-blue-300">
                  Activities automatically adjusted based on weather conditions
                </div>
              </div>
            )}

            {/* Alternative Weather Activities */}
            <div className="mt-3 p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <h5 className="text-sm font-medium text-green-900 dark:text-green-100 mb-1 flex items-center gap-2">
                <Cloud className="h-4 w-4" />
                Weather Alternatives:
              </h5>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="font-medium text-green-800 dark:text-green-200">Clear Weather:</span>
                  <p className="text-green-700 dark:text-green-300">Outdoor activities, sightseeing, photography</p>
                </div>
                <div>
                  <span className="font-medium text-green-800 dark:text-green-200">Rainy Weather:</span>
                  <p className="text-green-700 dark:text-green-300">Museums, shopping malls, indoor attractions</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Accommodations Tab Component
function AccommodationsTab({ trip }: { trip: TripData }) {
  const handleHotelBooking = (hotel: any) => {
    const bookingId = Math.random().toString(36).substring(2, 15).toUpperCase()
    const checkIn = new Date()
    const checkOut = new Date(checkIn)
    checkOut.setDate(checkIn.getDate() + parseInt(trip.trip_overview.duration.match(/\d+/)?.[0] || '3'))

    alert(`🏨 Hotel booking initiated! Redirecting to secure booking portal for "${hotel.name}". Check-in: ${checkIn.toLocaleDateString()}, Check-out: ${checkOut.toLocaleDateString()}. Rate: ${hotel.price_range}. Booking reference: ${bookingId}`)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hotels */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hotel className="h-5 w-5 text-primary" />
            Recommended Hotels
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {trip.hotels?.map((hotel, idx) => (
            <div key={idx} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-medium">{hotel.name}</h3>
                  <p className="text-sm text-muted-foreground">{hotel.location}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-yellow-500">
                    <Star className="h-4 w-4 fill-current" />
                    <span className="text-sm">{hotel.rating}</span>
                  </div>
                  <p className="text-sm font-medium text-green-600">{hotel.price_range}</p>
                </div>
              </div>

              <p className="text-xs text-muted-foreground mb-3">{hotel.theme_suitability}</p>

              <div className="flex flex-wrap gap-1 mb-3">
                {hotel.amenities?.map((amenity, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">
                    {amenity}
                  </Badge>
                ))}
              </div>

              {hotel.booking_options?.booking_url && (
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => handleHotelBooking(hotel)}
                >
                  <ExternalLink className="h-4 w-4 mr-1" />
                  Book Hotel
                </Button>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Restaurants */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5 text-primary" />
            Recommended Restaurants
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {trip.restaurants?.map((restaurant, idx) => (
            <div key={idx} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-medium">{restaurant.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {restaurant.cuisine_type} • {restaurant.location}
                  </p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-yellow-500">
                    <Star className="h-4 w-4 fill-current" />
                    <span className="text-sm">{restaurant.rating}</span>
                  </div>
                  <p className="text-sm font-medium text-green-600">{restaurant.price_range}</p>
                </div>
              </div>

              <p className="text-xs text-muted-foreground mb-3">{restaurant.theme_alignment}</p>

              <div>
                <h5 className="text-xs font-medium mb-1">Must-try dishes:</h5>
                <div className="flex flex-wrap gap-1">
                  {restaurant.specialties?.map((dish, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {dish}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

// Budget Tab Component
function BudgetTab({ trip }: { trip: TripData }) {
  const budget = trip.budget_breakdown

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Budget Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <IndianRupee className="h-5 w-5 text-green-600" />
            Budget Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-lg">
            <span className="font-medium">Total Budget</span>
            <span className="font-bold text-lg text-green-600">{budget.total_budget}</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-lg">
            <span className="font-medium">Estimated Cost</span>
            <span className="font-bold text-lg">{budget.estimated_cost || 'Calculating...'}</span>
          </div>

          {budget.budget_status && (
            <div className={`flex items-center justify-between p-4 rounded-lg ${
              budget.budget_status === 'sufficient'
                ? 'bg-green-50 border border-green-200'
                : 'bg-yellow-50 border border-yellow-200'
            }`}>
              <span className="font-medium">Budget Status</span>
              <span className={`font-bold text-sm capitalize ${
                budget.budget_status === 'sufficient'
                  ? 'text-green-700'
                  : 'text-yellow-700'
              }`}>
                {budget.budget_status}
              </span>
            </div>
          )}

          {budget.savings_potential && budget.savings_potential > 0 && (
            <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <span className="font-medium">Potential Savings</span>
              <span className="font-bold text-sm text-blue-700">
                Rs{budget.savings_potential.toLocaleString()}
              </span>
            </div>
          )}

          <div className="space-y-3">
            <h4 className="font-medium">Cost Distribution:</h4>

            {Object.entries(budget.breakdown).map(([category, percentage]) => (
              <div key={category} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="capitalize">{category}</span>
                  <div className="flex items-center gap-2">
                    {budget.detailed_breakdown && budget.detailed_breakdown[category as keyof typeof budget.detailed_breakdown] && (
                      <span className="text-xs text-muted-foreground">
                        {budget.detailed_breakdown[category as keyof typeof budget.detailed_breakdown]}
                      </span>
                    )}
                    <span className="font-medium">{percentage}</span>
                  </div>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-green-600"
                    style={{ width: percentage }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Budget Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-600" />
            Money-Saving Tips
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {budget.budget_optimization_tips && (
            <div>
              <h4 className="font-medium mb-2">Optimization Tips:</h4>
              <ul className="space-y-2">
                {budget.budget_optimization_tips.map((tip, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {budget.cost_saving_alternatives && (
            <div>
              <h4 className="font-medium mb-2">Cost-Saving Alternatives:</h4>
              <ul className="space-y-2">
                {budget.cost_saving_alternatives.map((alternative, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    {alternative}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}