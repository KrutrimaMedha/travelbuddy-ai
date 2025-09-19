export const TRAVEL_THEMES = [
  {
    id: 'Adventure',
    label: 'Adventure',
    icon: '🏔️',
    description: 'Water sports, trekking, paragliding, outdoor activities',
    color: 'bg-travel-adventure',
    gradient: 'from-orange-500 to-red-500'
  },
  {
    id: 'Cultural',
    label: 'Cultural',
    icon: '🏛️',
    description: 'Museums, heritage sites, festivals, art galleries',
    color: 'bg-travel-cultural',
    gradient: 'from-purple-500 to-indigo-500'
  },
  {
    id: 'Devotional',
    label: 'Devotional',
    icon: '🕉️',
    description: 'Temple visits, meditation, spiritual experiences',
    color: 'bg-travel-devotional',
    gradient: 'from-amber-500 to-orange-500'
  },
  {
    id: 'Nightlife',
    label: 'Nightlife',
    icon: '🌃',
    description: 'Clubs, bars, entertainment venues, night markets',
    color: 'bg-travel-nightlife',
    gradient: 'from-violet-500 to-purple-500'
  },
  {
    id: 'Relaxation',
    label: 'Relaxation',
    icon: '🏖️',
    description: 'Beach resorts, spas, peaceful getaways',
    color: 'bg-blue-500',
    gradient: 'from-blue-500 to-teal-500'
  }
] as const

export const TRAVEL_MODES = [
  {
    id: 'Self',
    label: 'Self Drive',
    icon: '🚗',
    description: 'Own vehicle with fuel cost calculations',
    benefits: ['Complete flexibility', 'Cost-effective for groups', 'Explore at your own pace']
  },
  {
    id: 'Booking',
    label: 'Public Transport',
    icon: '🚌',
    description: 'Flights, trains, buses with booking integration',
    benefits: ['No driving stress', 'Professional service', 'Fixed schedules']
  }
] as const

export const VEHICLE_TYPES = [
  {
    id: 'car',
    label: 'Car',
    icon: '🚗',
    fuelEfficiency: 15, // km/l
    description: 'Comfortable for 4-5 people'
  },
  {
    id: 'suv',
    label: 'SUV',
    icon: '🚙',
    fuelEfficiency: 12, // km/l
    description: 'Spacious for 6-7 people'
  },
  {
    id: 'bike',
    label: 'Motorcycle',
    icon: '🏍️',
    fuelEfficiency: 45, // km/l
    description: 'Economical for 1-2 people'
  },
  {
    id: 'hatchback',
    label: 'Hatchback',
    icon: '🚗',
    fuelEfficiency: 18, // km/l
    description: 'Compact and efficient for 4 people'
  }
] as const

export const TRANSPORT_OPTIONS = [
  {
    id: 'flight',
    label: 'Flight',
    icon: '✈️',
    description: 'Fastest option for long distances'
  },
  {
    id: 'train',
    label: 'Train',
    icon: '🚄',
    description: 'Comfortable and scenic journey'
  },
  {
    id: 'bus',
    label: 'Bus',
    icon: '🚌',
    description: 'Most economical option'
  },
  {
    id: 'cab',
    label: 'Cab/Taxi',
    icon: '🚕',
    description: 'Door-to-door convenience'
  }
] as const

export const POPULAR_DESTINATIONS = [
  'Goa', 'Kerala', 'Rajasthan', 'Kashmir', 'Himachal Pradesh', 'Uttarakhand',
  'Tamil Nadu', 'Karnataka', 'Maharashtra', 'Gujarat', 'Andhra Pradesh',
  'West Bengal', 'Assam', 'Meghalaya', 'Sikkim', 'Arunachal Pradesh'
]

export const BUDGET_RANGES = [
  { label: 'Budget (Rs5,000 - Rs15,000)', min: 5000, max: 15000 },
  { label: 'Mid-range (Rs15,000 - Rs35,000)', min: 15000, max: 35000 },
  { label: 'Premium (Rs35,000 - Rs75,000)', min: 35000, max: 75000 },
  { label: 'Luxury (Rs75,000+)', min: 75000, max: 200000 }
]

export const DURATION_OPTIONS = [
  { label: '1-2 days', value: '2 days' },
  { label: '3-4 days', value: '3 days' },
  { label: '5-7 days', value: '7 days' },
  { label: '1 week+', value: '10 days' },
  { label: 'More than 15 days', value: '15+ days' }
]

export const API_ENDPOINTS = {
  PLAN_TRIP: '/api/plan-trip',
  VALIDATE_BUDGET: '/api/validate-budget',
  SEARCH: '/api/search'
} as const

export const STORAGE_KEYS = {
  TRIP_HISTORY: 'travel_trip_history',
  USER_PREFERENCES: 'travel_user_preferences',
  RECENT_SEARCHES: 'travel_recent_searches'
} as const