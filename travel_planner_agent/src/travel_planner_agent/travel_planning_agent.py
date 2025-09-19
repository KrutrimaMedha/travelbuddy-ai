#!/usr/bin/env python3
"""
Personalized Trip Planner with AI
A comprehensive travel planning agent that creates personalized itineraries based on user preferences.

Features:
- Budget validation with minimum requirements alert
- Travel mode support (Self/Booking)
- Theme-based planning (devotional, adventurous, nightlife, cultural)
- Weather-based recommendations
- Duration validation
- Hotel, restaurant, and local market recommendations
- Fuel cost estimation for Self mode
- Booking options for public transport mode
"""

import os
import json
import asyncio
import re
from typing import Dict, Any, List, Union, Optional
from datetime import datetime, timedelta

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    print("Google Generative AI not available. Install with: pip install google-generativeai")
    genai = None

try:
    from .travel_planning_tool import TravelPlanningTool, travel_planning
except ImportError:
    print("TravelPlanningTool not available")
    travel_planning = None


class PersonalizedTripPlanner:
    """
    Personalized Trip Planner with AI

    Creates comprehensive travel itineraries based on:
    - Source and destination
    - Travel mode (Self or Booking)
    - Budget with validation
    - Theme preferences
    - Duration validation
    - Weather conditions
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Personalized Trip Planner"""
        self.api_key = 'AIzaSyDmd6RTgWWBFebqL1wjX-_hx6J0zziSESc' or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be provided")

        # Configure Google Generative AI
        genai.configure(api_key=self.api_key)

        # Initialize the model with function calling
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            tools=[
                genai.protos.Tool(
                    function_declarations=[
                        self._create_weather_function(),
                        self._create_hotels_function(),
                        self._create_restaurants_function(),
                        self._create_activities_function(),
                        self._create_markets_function(),
                        self._create_route_function(),
                        self._create_search_function(),
                    ]
                )
            ]
        )

        # Initialize travel planning tool
        self.travel_tool = travel_planning if travel_planning else None

    def _create_weather_function(self):
        """Create weather information function declaration"""
        return genai.protos.FunctionDeclaration(
            name="get_weather_info",
            description="Get weather information for a destination to recommend appropriate activities",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "location": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Location to get weather for"
                    ),
                    "duration": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Trip duration to get weather forecast"
                    )
                },
                required=["location"]
            )
        )

    def _create_hotels_function(self):
        """Create hotels search function declaration"""
        return genai.protos.FunctionDeclaration(
            name="get_hotels",
            description="Find hotels based on theme, budget, and location",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "location": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Location to find hotels"
                    ),
                    "theme": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Travel theme (devotional, adventurous, nightlife, cultural)"
                    ),
                    "budget_range": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Budget range for accommodation"
                    )
                },
                required=["location", "theme"]
            )
        )

    def _create_restaurants_function(self):
        """Create restaurants search function declaration"""
        return genai.protos.FunctionDeclaration(
            name="get_restaurants",
            description="Find restaurants aligned with travel theme and budget",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "location": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Location to find restaurants"
                    ),
                    "theme": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Travel theme for restaurant recommendations"
                    ),
                    "cuisine_type": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Preferred cuisine type"
                    )
                },
                required=["location", "theme"]
            )
        )

    def _create_activities_function(self):
        """Create activities search function declaration"""
        return genai.protos.FunctionDeclaration(
            name="get_activities",
            description="Find activities and attractions based on theme and weather",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "location": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Location to find activities"
                    ),
                    "theme": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Travel theme for activity recommendations"
                    ),
                    "weather_condition": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Current weather condition"
                    )
                },
                required=["location", "theme"]
            )
        )

    def _create_markets_function(self):
        """Create local markets search function declaration"""
        return genai.protos.FunctionDeclaration(
            name="get_local_markets",
            description="Find local markets for unique products and shopping",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "location": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Location to find local markets"
                    ),
                    "product_type": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Type of products to look for"
                    )
                },
                required=["location"]
            )
        )

    def _create_route_function(self):
        """Create route planning function declaration"""
        return genai.protos.FunctionDeclaration(
            name="get_route_info",
            description="Get route information including distance, time, and fuel costs",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "source": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Starting location"
                    ),
                    "destination": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Destination location"
                    ),
                    "travel_mode": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Travel mode (Self or Booking)"
                    ),
                    "vehicle_type": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Vehicle type for Self mode (car, bike, etc.)"
                    )
                },
                required=["source", "destination", "travel_mode"]
            )
        )

    def _create_search_function(self):
        """Create general search function declaration"""
        return genai.protos.FunctionDeclaration(
            name="search_travel_info",
            description="Search for general travel information using SERP API",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "query": genai.protos.Schema(
                        type=genai.protos.Type.STRING,
                        description="Search query for travel information"
                    )
                },
                required=["query"]
            )
        )

    def validate_budget(self, travel_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if the provided budget is sufficient for the trip.
        Returns budget validation with minimum required amount if insufficient.
        """
        try:
            budget_str = str(travel_input.get('budget', '0'))
            # Remove currency symbols, commas, and spaces, then extract numbers
            cleaned_budget = re.sub(r'[₹Rs,\s]', '', budget_str)
            budget_numbers = re.findall(r'\d+', cleaned_budget)
            budget = int(''.join(budget_numbers)) if budget_numbers else 0

            travel_mode = travel_input.get('travel_mode', 'Self')
            theme = travel_input.get('theme', 'cultural').lower()
            duration_str = str(travel_input.get('duration', '1'))
            duration_numbers = re.findall(r'\d+', duration_str)
            duration = int(duration_numbers[0]) if duration_numbers else 1

            # Base daily costs (in INR)
            base_daily_cost = 2500

            # Theme-based multipliers
            theme_multipliers = {
                'devotional': 1.0,
                'cultural': 1.2,
                'adventurous': 1.5,
                'nightlife': 2.0,
                'luxury': 3.0
            }

            theme_multiplier = theme_multipliers.get(theme, 1.2)

            # Calculate costs
            if travel_mode.lower() == 'self':
                transport_cost = duration * 1500  # Fuel and vehicle costs
            else:  # Booking mode
                transport_cost = duration * 3500  # Public transport costs

            accommodation_cost = duration * base_daily_cost * 0.4 * theme_multiplier
            food_cost = duration * base_daily_cost * 0.3
            activities_cost = duration * base_daily_cost * 0.3 * theme_multiplier

            minimum_budget = int(transport_cost + accommodation_cost + food_cost + activities_cost)

            if budget >= minimum_budget:
                return {
                    "status": "sufficient",
                    "provided_budget": budget,
                    "minimum_required": minimum_budget,
                    "buffer_amount": budget - minimum_budget,
                    "message": f"Budget is sufficient! You have ¹{budget - minimum_budget:,} buffer amount."
                }
            else:
                return {
                    "status": "insufficient",
                    "provided_budget": budget,
                    "minimum_required": minimum_budget,
                    "shortfall": minimum_budget - budget,
                    "alert_message": f"  Budget Alert: Minimum required budget is ¹{minimum_budget:,}. You provided ¹{budget:,}. Please increase budget by ¹{minimum_budget - budget:,}."
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Budget validation failed: {str(e)}",
                "minimum_required": 10000
            }

    def validate_duration(self, duration: str) -> Dict[str, Any]:
        """Validate trip duration and provide recommendations"""
        try:
            duration_numbers = re.findall(r'\d+', str(duration))
            days = int(duration_numbers[0]) if duration_numbers else 1

            if days < 1:
                return {
                    "status": "invalid",
                    "message": "Duration must be at least 1 day",
                    "recommended_duration": 2
                }
            elif days > 30:
                return {
                    "status": "warning",
                    "message": "Long trip detected. Consider breaking into multiple shorter trips.",
                    "validated_duration": days
                }
            else:
                return {
                    "status": "valid",
                    "validated_duration": days,
                    "message": f"Duration of {days} days is optimal for trip planning."
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Duration validation failed: {str(e)}",
                "recommended_duration": 3
            }

    async def generate_personalized_itinerary(self, travel_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized travel itinerary based on user input.

        Args:
            travel_input: Dictionary containing:
                - source: Starting location
                - destination: Destination location
                - travel_mode: 'Self' or 'Booking'
                - budget: Budget amount
                - theme: Travel theme (devotional, adventurous, nightlife, cultural)
                - duration: Trip duration
                - vehicle_type: For Self mode (car, bike, etc.)

        Returns:
            Comprehensive itinerary with budget validation and recommendations
        """

        # Extract and validate inputs
        source = travel_input.get('source', '')
        destination = travel_input.get('destination', '')
        travel_mode = travel_input.get('travel_mode', 'Self')
        budget = travel_input.get('budget', '')
        theme = travel_input.get('theme', 'cultural')
        duration = travel_input.get('duration', '3 days')
        vehicle_type = travel_input.get('vehicle_type', 'car')

        # Validate budget and duration
        budget_validation = self.validate_budget(travel_input)
        duration_validation = self.validate_duration(duration)

        # If budget is insufficient, return early with alert
        if budget_validation['status'] == 'insufficient':
            return {
                "status": "budget_insufficient",
                "budget_validation": budget_validation,
                "duration_validation": duration_validation,
                "alert": budget_validation['alert_message'],
                "recommendations": {
                    "minimum_budget": budget_validation['minimum_required'],
                    "cost_saving_tips": self._get_cost_saving_tips(travel_mode, theme)
                }
            }

        try:
            # Start conversation with AI
            chat = self.model.start_chat()

            # Create comprehensive prompt
            prompt = self._create_personalized_prompt(
                source, destination, travel_mode, budget, theme,
                duration, vehicle_type, budget_validation, duration_validation
            )

            # Send initial request
            response = await self._send_message_with_functions(chat, prompt)

            # Process the response and enhance with mode-specific features
            final_itinerary = await self._process_ai_response(
                response, travel_input, budget_validation, duration_validation
            )

            return final_itinerary

        except Exception as e:
            print(f"Error generating itinerary: {str(e)}")
            return self._create_fallback_itinerary(travel_input, budget_validation, duration_validation)

    def _create_personalized_prompt(self, source, destination, travel_mode, budget, theme,
                                  duration, vehicle_type, budget_validation, duration_validation):
        """Create a comprehensive prompt for the AI"""

        weather_instruction = "IMPORTANT: Call get_weather_info() first to understand weather conditions."

        if travel_mode.lower() == 'self':
            mode_instructions = f"""
SELF MODE REQUIREMENTS (Own Vehicle - {vehicle_type}):
- Call get_route_info() to calculate distance, time, and fuel costs
- Focus on route planning and vehicle-friendly stops
- Include highly rated hotels and restaurants along the route
- Provide fuel cost estimates based on {vehicle_type}
- Suggest scenic stops and safe parking areas
- Include rest stops and fuel stations
- Provide driving safety tips
"""
        else:
            mode_instructions = """
BOOKING MODE REQUIREMENTS (Public Transport):
- Provide seamless booking options for flights, trains, buses, cabs
- Include one-click booking confirmation links where possible
- Show transport schedules and connection information
- Include transport hubs and connectivity details
- Provide backup transport options
- Compare prices between different transport modes
"""

        theme_instructions = self._get_theme_instructions(theme)

        prompt = f"""You are a Personalized Trip Planner with AI. Create a perfect travel itinerary based on these user preferences:

TRIP DETAILS:
- Source: {source}
- Destination: {destination}
- Travel Mode: {travel_mode}
- Budget: {budget}
- Theme: {theme}
- Duration: {duration}
- Vehicle Type: {vehicle_type if travel_mode.lower() == 'self' else 'N/A'}

BUDGET STATUS: {budget_validation['status'].upper()}
Budget Details: {json.dumps(budget_validation, indent=2)}

DURATION STATUS: {duration_validation['status'].upper()}
Duration Details: {json.dumps(duration_validation, indent=2)}

STEP-BY-STEP REQUIREMENTS:

1. WEATHER ANALYSIS:
{weather_instruction}
Use weather data to recommend appropriate activities and suggest weather-specific packing.

2. COMPREHENSIVE DATA GATHERING:
Call ALL these functions to create complete itinerary:
- get_hotels() - Find accommodations matching theme and budget
- get_restaurants() - Find dining options aligned with theme
- get_activities() - Find attractions and activities for the theme
- get_local_markets() - Find shopping areas and unique local products

3. TRAVEL MODE SPECIFIC PLANNING:
{mode_instructions}

4. THEME-BASED RECOMMENDATIONS:
{theme_instructions}

5. CREATE DETAILED ITINERARY:
Generate a day-by-day itinerary including:
- Best destinations highlighted for {theme} theme
- Recommended hotels at each stop with ratings and prices
- Local markets for unique products and shopping
- Top restaurants matching theme and budget
- Weather-appropriate activities for each day
- Theme-specific recommendations
- Time allocations and logistics

RESPONSE FORMAT:
Return a comprehensive JSON response with:
- Trip overview and validation results
- Day-by-day detailed itinerary
- Budget breakdown with actual costs
- Weather considerations and packing list
- Mode-specific enhancements (fuel costs for Self, booking links for Booking)
- Emergency contacts and travel tips

Make this truly personalized to their {theme} theme, {budget} budget, and {travel_mode} travel mode!"""

        return prompt

    def _get_theme_instructions(self, theme: str) -> str:
        """Get theme-specific instructions"""
        theme_guides = {
            'devotional': """
DEVOTIONAL THEME FOCUS:
- Prioritize temples, spiritual sites, and pilgrimage routes
- Include early morning and evening prayer times
- Suggest vegetarian food options and pure cuisine
- Recommend modest accommodation near religious sites
- Include spiritual activities, rituals, and ceremonies
- Provide information about religious festivals and events
- Include meditation and yoga centers
""",
            'adventurous': """
ADVENTUROUS THEME FOCUS:
- Focus on outdoor activities, extreme sports, and trekking
- Include adventure parks, water sports, and mountain activities
- Suggest gear rental locations and safety equipment
- Recommend adventure-friendly accommodation
- Include fitness requirements and skill level assessments
- Provide safety guidelines and emergency contacts
- Include wildlife sanctuaries and nature reserves
""",
            'nightlife': """
NIGHTLIFE THEME FOCUS:
- Focus on clubs, bars, pubs, and night markets
- Include late-night dining and 24-hour establishments
- Suggest party-friendly accommodation with good connectivity
- Recommend safe transport options for night travel
- Include dress codes, entry requirements, and cover charges
- Provide information about local nightlife culture and etiquette
- Include rooftop bars and night view points
""",
            'cultural': """
CULTURAL THEME FOCUS:
- Focus on museums, heritage sites, and historical monuments
- Include cultural performances, festivals, and local traditions
- Suggest authentic local cuisine and traditional cooking experiences
- Recommend heritage hotels and culturally significant stays
- Include guided tour options and cultural workshops
- Provide historical context and cultural significance
- Include art galleries, craft centers, and cultural villages
"""
        }

        return theme_guides.get(theme.lower(), theme_guides['cultural'])

    def _get_cost_saving_tips(self, travel_mode: str, theme: str) -> List[str]:
        """Generate cost-saving tips based on travel mode and theme"""
        tips = [
            "Book accommodations in advance for better rates",
            "Travel during off-peak seasons for lower costs",
            "Use local public transport within cities",
            "Eat at local restaurants instead of hotel dining"
        ]

        if travel_mode.lower() == 'self':
            tips.extend([
                "Plan fuel-efficient routes to save on fuel costs",
                "Share fuel costs if traveling with others",
                "Choose accommodation with free parking"
            ])
        else:
            tips.extend([
                "Book transport tickets in advance for discounts",
                "Compare prices across different booking platforms",
                "Consider train travel for longer distances to save costs"
            ])

        if theme.lower() == 'devotional':
            tips.extend([
                "Many temples provide free accommodation",
                "Look for community kitchens for free meals",
                "Choose simple, modest accommodations"
            ])
        elif theme.lower() == 'adventurous':
            tips.extend([
                "Book activity packages for group discounts",
                "Rent equipment locally instead of buying",
                "Choose adventure hostels for budget accommodation"
            ])

        return tips

    async def _send_message_with_functions(self, chat, prompt):
        """Send message and handle function calls"""
        response = chat.send_message(prompt)

        # Process function calls if any
        if response.parts:
            for part in response.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_result = await self._execute_function_call(part.function_call)

                    # Send function result back to continue conversation
                    function_response = genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=part.function_call.name,
                            response={"result": function_result}
                        )
                    )
                    response = chat.send_message([function_response])

        return response

    async def _execute_function_call(self, function_call):
        """Execute the function call and return result"""
        function_name = function_call.name
        function_args = dict(function_call.args)

        try:
            if self.travel_tool:
                if function_name == "get_weather_info":
                    return await self.travel_tool.get_weather_info(**function_args)
                elif function_name == "get_hotels":
                    return await self.travel_tool.get_hotels(**function_args)
                elif function_name == "get_restaurants":
                    return await self.travel_tool.get_restaurants(**function_args)
                elif function_name == "get_activities":
                    return await self.travel_tool.get_events_activities(**function_args)
                elif function_name == "get_local_markets":
                    return await self.travel_tool.get_local_markets(**function_args)
                elif function_name == "get_route_info":
                    return await self.travel_tool.get_route_distance(**function_args)
                elif function_name == "search_travel_info":
                    return await self.travel_tool.google_search(**function_args)

            # Fallback responses if travel_tool not available
            return self._get_fallback_function_result(function_name, function_args)

        except Exception as e:
            return {"error": f"Function execution failed: {str(e)}"}

    def _get_fallback_function_result(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback results when travel tool is not available"""
        location = args.get('location', 'destination')

        fallback_results = {
            "get_weather_info": {
                "location": location,
                "temperature": "25°C",
                "condition": "Pleasant",
                "forecast": "Suitable for outdoor activities",
                "recommendation": "Pack light cotton clothes and carry an umbrella"
            },
            "get_hotels": {
                "hotels": [
                    {
                        "name": f"Hotel Paradise {location}",
                        "rating": "4.2/5",
                        "price": "¹2,500/night",
                        "amenities": ["Free WiFi", "Restaurant", "Parking"]
                    },
                    {
                        "name": f"Budget Stay {location}",
                        "rating": "3.8/5",
                        "price": "¹1,200/night",
                        "amenities": ["Free WiFi", "AC", "Room Service"]
                    }
                ]
            },
            "get_restaurants": {
                "restaurants": [
                    {
                        "name": f"Local Delights {location}",
                        "cuisine": "Local",
                        "rating": "4.5/5",
                        "price_range": "¹300-600 per person"
                    },
                    {
                        "name": f"Spice Garden {location}",
                        "cuisine": "Multi-cuisine",
                        "rating": "4.0/5",
                        "price_range": "¹400-800 per person"
                    }
                ]
            },
            "get_activities": {
                "activities": [
                    {
                        "name": f"Sightseeing Tour {location}",
                        "type": "Cultural",
                        "duration": "4 hours",
                        "price": "¹500 per person"
                    },
                    {
                        "name": f"Adventure Sports {location}",
                        "type": "Adventure",
                        "duration": "6 hours",
                        "price": "¹1,200 per person"
                    }
                ]
            },
            "get_local_markets": {
                "markets": [
                    {
                        "name": f"Main Bazaar {location}",
                        "speciality": "Local handicrafts and souvenirs",
                        "timings": "9 AM - 9 PM",
                        "products": ["Textiles", "Handicrafts", "Spices"]
                    }
                ]
            },
            "get_route_info": {
                "distance": "250 km",
                "duration": "4 hours",
                "fuel_cost": "¹1,500",
                "route": "Well-connected highways"
            }
        }

        return fallback_results.get(function_name, {"message": "Information not available"})

    async def _process_ai_response(self, response, travel_input, budget_validation, duration_validation):
        """Process AI response and create final itinerary"""
        try:
            # Handle case where response might contain function calls
            try:
                response_text = response.text if response.text else "No response generated"
            except Exception as e:
                print(f"Error processing AI response: {e}")
                # If we can't get response.text, create a fallback response
                return self._create_fallback_itinerary(travel_input, budget_validation, duration_validation)

            # Try to parse JSON response
            if response_text.strip().startswith('{'):
                try:
                    itinerary = json.loads(response_text)
                except json.JSONDecodeError:
                    itinerary = self._create_structured_response(response_text, travel_input)
            else:
                itinerary = self._create_structured_response(response_text, travel_input)

            # Add validation results
            itinerary['budget_validation'] = budget_validation
            itinerary['duration_validation'] = duration_validation

            # Add mode-specific enhancements
            travel_mode = travel_input.get('travel_mode', 'Self')
            if travel_mode.lower() == 'self':
                itinerary = await self._enhance_self_mode(itinerary, travel_input)
            else:
                itinerary = await self._enhance_booking_mode(itinerary, travel_input)

            return itinerary

        except Exception as e:
            print(f"Error processing AI response: {str(e)}")
            return self._create_fallback_itinerary(travel_input, budget_validation, duration_validation)

    def _create_structured_response(self, response_text: str, travel_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured response from text"""
        return {
            "status": "success",
            "trip_overview": {
                "source": travel_input.get('source', ''),
                "destination": travel_input.get('destination', ''),
                "travel_mode": travel_input.get('travel_mode', ''),
                "theme": travel_input.get('theme', ''),
                "duration": travel_input.get('duration', ''),
                "budget": travel_input.get('budget', '')
            },
            "ai_response": response_text,
            "itinerary": [],
            "recommendations": {
                "hotels": [],
                "restaurants": [],
                "activities": [],
                "local_markets": []
            },
            "travel_info": {},
            "weather_info": {},
            "generated_at": datetime.now().isoformat()
        }

    async def _enhance_self_mode(self, itinerary: Dict[str, Any], travel_input: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance itinerary with Self mode specific features"""
        vehicle_type = travel_input.get('vehicle_type', 'car')
        source = travel_input.get('source', '')
        destination = travel_input.get('destination', '')

        # Calculate fuel costs
        fuel_info = self._calculate_fuel_costs(source, destination, vehicle_type)

        # Add Self mode enhancements
        itinerary['self_mode_features'] = {
            "vehicle_type": vehicle_type,
            "fuel_costs": fuel_info,
            "route_recommendations": [
                "Take NH highways for better road conditions",
                "Plan rest stops every 2-3 hours",
                "Check vehicle condition before departure",
                "Keep emergency contact numbers handy"
            ],
            "packing_list": [
                "Vehicle documents and insurance",
                "First aid kit",
                "Tool kit for minor repairs",
                "Extra fuel canister (if allowed)",
                "Phone charger and power bank"
            ]
        }

        return itinerary

    async def _enhance_booking_mode(self, itinerary: Dict[str, Any], travel_input: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance itinerary with Booking mode specific features"""
        source = travel_input.get('source', '')
        destination = travel_input.get('destination', '')

        # Add booking mode enhancements
        itinerary['booking_mode_features'] = {
            "transport_options": [
                {
                    "type": "Flight",
                    "duration": "2 hours",
                    "price_range": "¹3,000 - ¹8,000",
                    "booking_tips": "Book 2-3 weeks in advance for better rates"
                },
                {
                    "type": "Train",
                    "duration": "6-8 hours",
                    "price_range": "¹500 - ¹2,000",
                    "booking_tips": "Book through IRCTC for confirmed tickets"
                },
                {
                    "type": "Bus",
                    "duration": "8-10 hours",
                    "price_range": "¹800 - ¹1,500",
                    "booking_tips": "Choose reputable operators for safety"
                }
            ],
            "booking_links": {
                "flights": "https://www.easemytrip.com",
                "trains": "https://www.irctc.co.in",
                "buses": "https://www.redbus.in"
            },
            "travel_tips": [
                "Arrive at station/airport 2 hours early",
                "Keep ID proof for ticket verification",
                "Download offline maps for local transport",
                "Keep transport booking confirmations handy"
            ]
        }

        return itinerary

    def _calculate_fuel_costs(self, source: str, destination: str, vehicle_type: str) -> Dict[str, Any]:
        """Calculate fuel costs for Self mode"""
        # Default distance - in real implementation, this would come from route API
        estimated_distance = 300  # km

        # Fuel efficiency by vehicle type
        fuel_efficiency = {
            'car': 15,      # km/l
            'bike': 40,     # km/l
            'suv': 12,      # km/l
            'motorcycle': 45  # km/l
        }

        efficiency = fuel_efficiency.get(vehicle_type.lower(), 15)
        fuel_price = 100  # INR per liter

        fuel_needed = estimated_distance / efficiency
        fuel_cost = fuel_needed * fuel_price

        return {
            "estimated_distance": f"{estimated_distance} km",
            "fuel_efficiency": f"{efficiency} km/l",
            "fuel_needed": f"{fuel_needed:.1f} liters",
            "fuel_cost": f"¹{fuel_cost:.0f}",
            "total_cost_with_return": f"¹{fuel_cost * 2:.0f}"
        }

    def _create_fallback_itinerary(self, travel_input: Dict[str, Any],
                                 budget_validation: Dict[str, Any],
                                 duration_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback itinerary when AI fails"""

        destination = travel_input.get('destination', 'Destination')
        theme = travel_input.get('theme', 'cultural')
        duration = travel_input.get('duration', '3 days')

        return {
            "status": "fallback",
            "message": "AI-generated itinerary not available. Using fallback plan.",
            "trip_overview": {
                "source": travel_input.get('source', ''),
                "destination": destination,
                "travel_mode": travel_input.get('travel_mode', ''),
                "theme": theme,
                "duration": duration,
                "budget": travel_input.get('budget', '')
            },
            "budget_validation": budget_validation,
            "duration_validation": duration_validation,
            "itinerary": [
                {
                    "day": 1,
                    "title": f"Arrival and {destination} Exploration",
                    "activities": [
                        f"Arrive at {destination}",
                        f"Check into hotel",
                        f"Local {theme} site visit",
                        f"Dinner at local restaurant"
                    ]
                },
                {
                    "day": 2,
                    "title": f"Full Day {theme.title()} Experience",
                    "activities": [
                        f"Morning {theme} activity",
                        f"Local market visit",
                        f"Afternoon sightseeing",
                        f"Evening leisure time"
                    ]
                }
            ],
            "recommendations": {
                "hotels": [f"Recommended hotels in {destination}"],
                "restaurants": [f"Local {theme}-themed restaurants"],
                "activities": [f"{theme.title()} activities and attractions"],
                "local_markets": [f"Popular markets in {destination}"]
            },
            "generated_at": datetime.now().isoformat()
        }


# Alias for backward compatibility
GeminiTravelPlanningAgent = PersonalizedTripPlanner

# For easy import (keep the original search_and_respond method)
class GeminiTravelPlanningAgent(PersonalizedTripPlanner):
    """Backward compatibility class with search_and_respond method"""

    async def search_and_respond(self, user_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main method for generating personalized trip plans (backward compatibility)
        """
        # If string input, convert to structured format
        if isinstance(user_input, str):
            # Simple parsing for string inputs
            travel_input = {
                "source": "Mumbai",  # Default values - in real app, parse from string
                "destination": "Goa",
                "travel_mode": "Self",
                "budget": "20000",
                "theme": "cultural",
                "duration": "3 days",
                "vehicle_type": "car"
            }
        else:
            travel_input = user_input

        return await self.generate_personalized_itinerary(travel_input)


# Create default instance for easy import
def create_trip_planner(api_key: Optional[str] = None) -> PersonalizedTripPlanner:
    """Create a new PersonalizedTripPlanner instance"""
    return PersonalizedTripPlanner(api_key)


# Example usage function
async def example_usage():
    """Example of how to use the Personalized Trip Planner"""

    # Initialize the planner
    planner = PersonalizedTripPlanner()

    # Define trip parameters
    trip_request = {
        "source": "Mumbai",
        "destination": "Goa",
        "travel_mode": "Self",  # or "Booking"
        "budget": "25000",
        "theme": "adventurous",  # devotional, adventurous, nightlife, cultural
        "duration": "4 days",
        "vehicle_type": "car"  # for Self mode
    }

    # Generate personalized itinerary
    result = await planner.generate_personalized_itinerary(trip_request)

    # Print results
    print("=== PERSONALIZED TRIP PLANNER RESULTS ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return result


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
