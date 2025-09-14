"""
Personalized Travel Planning Agent

A production-ready AI agent that creates personalized trip plans using Google Genai
with function calling capabilities. Supports both Self (own vehicle) and Booking 
(public transport) travel modes with theme-based recommendations.

Features:
- Real-time search integration via SERP API
- Budget validation and optimization
- Theme-based personalization (Adventure, Devotional, Nightlife, Cultural)
- Structured JSON responses matching UI wireframes
- Fuel cost estimation for Self mode
- Booking integration for public transport mode
"""

import os
import sys
from typing import Dict, Any, Union
from dotenv import load_dotenv
import google.generativeai as genai

# Import the travel planning tool
try:
    from .travel_planning_tool import travel_planning
except ImportError:
    from travel_planning_tool import travel_planning

load_dotenv()

class GeminiTravelPlanningAgent:
    """
    Personalized Travel Planning Agent with AI-powered recommendations
    
    Usage:
        agent = GeminiTravelPlanningAgent()
        
        # String input
        result = await agent.search_and_respond("Plan 3-day Goa trip with ₹15000 budget")
        
        # Structured input (matches UI wireframes)
        trip_request = {
            "source": "Mumbai",
            "destination": "Goa", 
            "travel_mode": "Self",
            "budget": "₹15000",
            "theme": "Adventure",
            "duration": "3 days"
        }
        result = await agent.search_and_respond(trip_request)
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")
        
        self.setup_agent()

    def setup_agent(self):
        """Setup direct genai agent with function calling"""
        # Configure genai
        genai.configure(api_key=self.api_key)
        
        # Create model with specialized function calling
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash',
            tools=[self._create_search_functions()]
        )

    def _create_search_functions(self):
        """Create function declarations for specialized travel searches"""
        return genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name="get_weather_info",
                    description="Get weather information and climate data for a location to plan weather-appropriate activities",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "location": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Location name for weather information"
                            ),
                            "date_range": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Date range: current, weekly, or monthly"
                            )
                        },
                        required=["location"]
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="get_hotels",
                    description="Get hotel recommendations based on location, budget, and theme",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "location": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Destination location"
                            ),
                            "budget_range": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Budget category: budget, mid-range, or luxury"
                            ),
                            "theme": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Travel theme for hotel selection"
                            )
                        },
                        required=["location"]
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="get_restaurants",
                    description="Get restaurant recommendations based on location, cuisine, and theme",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "location": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Destination location"
                            ),
                            "cuisine_type": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Type of cuisine preferred"
                            ),
                            "theme": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Travel theme for restaurant selection"
                            )
                        },
                        required=["location"]
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="get_events_activities",
                    description="Get events, activities, and attractions for a location based on theme",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "location": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Destination location"
                            ),
                            "theme": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Travel theme: adventure, cultural, nightlife, devotional"
                            ),
                            "date_range": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="When visiting"
                            )
                        },
                        required=["location"]
                    )
                ),
                genai.protos.FunctionDeclaration(
                    name="google_search",
                    description="Fallback general search for any travel information when specialized functions fail",
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
            ]
        )

    async def search_and_respond(self, user_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Direct genai function calling approach with hybrid fallback
        Handles both string queries and structured input objects
        """
        
        # Handle both string and structured input
        if isinstance(user_input, str):
            user_query = user_input
            structured_input = self._parse_query_to_structure(user_input)
        else:
            structured_input = user_input
            user_query = self._structure_to_query(user_input)
        
        try:
            # Start chat with function calling enabled
            chat = self.model.start_chat()
            
            # Create a comprehensive prompt for personalized trip planning
            enhanced_query = f"""You are a Personalized Trip Planner AI. Use the google_search function to get current, accurate information for this travel request.

TRIP DETAILS:
- Source: {structured_input.get('source', 'Not specified')}
- Destination: {structured_input.get('destination', 'Not specified')}
- Travel Mode: {structured_input.get('travel_mode', 'Not specified')}
- Budget: {structured_input.get('budget', 'Not specified')}
- Theme: {structured_input.get('theme', 'Not specified')}
- Duration: {structured_input.get('duration', 'Not specified')}

Original Query: {user_query}

After getting the search results, analyze the user's requirements and provide a comprehensive personalized trip plan in the following JSON format:

{{
    "trip_overview": {{
        "source": "Source location",
        "destination": "Destination location", 
        "travel_mode": "Self/Booking",
        "budget": "Total budget",
        "theme": "Travel theme (devotional/adventurous/nightlife/cultural/relaxation)",
        "duration": "Trip duration",
        "budget_status": "sufficient/insufficient",
        "minimum_budget_required": "Amount if budget insufficient"
    }},
    "destinations": [
        {{
            "name": "Destination name",
            "description": "Detailed description",
            "theme_alignment": "How it fits the selected theme",
            "highlights": ["attraction1", "attraction2"],
            "estimated_time": "Time to spend here",
            "entry_fees": "Cost information",
            "best_time_to_visit": "Optimal timing",
            "booking_options": {{
                "available": true/false,
                "booking_url": "Direct booking link if available"
            }}
        }}
    ],
    "hotels": [
        {{
            "name": "Hotel name",
            "location": "Hotel location",
            "rating": "Star rating",
            "price_range": "Price per night",
            "amenities": ["amenity1", "amenity2"],
            "distance_from_attractions": "Distance info",
            "theme_suitability": "How it fits travel theme",
            "booking_options": {{
                "available": true/false,
                "booking_url": "Direct booking link",
                "one_click_booking": true/false
            }}
        }}
    ],
    "restaurants": [
        {{
            "name": "Restaurant name",
            "cuisine_type": "Type of cuisine",
            "location": "Restaurant location", 
            "rating": "Rating",
            "price_range": "Budget category",
            "specialties": ["dish1", "dish2"],
            "theme_alignment": "How it fits travel theme",
            "distance_from_hotels": "Distance info"
        }}
    ],
    "local_markets": [
        {{
            "name": "Market name",
            "location": "Market location",
            "unique_products": ["product1", "product2"],
            "best_time_to_visit": "Optimal timing",
            "price_range": "Budget category",
            "theme_relevance": "Connection to travel theme"
        }}
    ],
    "transportation": {{
        "mode": "Selected travel mode",
        "self_mode": {{
            "route_details": "Best route information",
            "fuel_estimate": {{
                "vehicle_type": "Car/Bike/etc",
                "total_distance": "Distance in km",
                "fuel_cost": "Estimated fuel charges",
                "toll_charges": "Toll costs if any"
            }},
            "route_hotels": ["Hotels along the route"],
            "route_restaurants": ["Restaurants along the route"]
        }},
        "booking_mode": {{
            "transport_options": [
                {{
                    "type": "Bus/Train/Flight/Cab",
                    "operator": "Service provider",
                    "price": "Cost",
                    "duration": "Travel time",
                    "booking_url": "Direct booking link",
                    "one_click_booking": true/false
                }}
            ]
        }}
    }},
    "budget_breakdown": {{
        "total_budget": "User's budget",
        "estimated_cost": "Calculated total cost",
        "breakdown": {{
            "transportation": "Transport costs",
            "accommodation": "Hotel costs", 
            "food": "Meal costs",
            "activities": "Attraction/activity costs",
            "shopping": "Market/shopping budget",
            "miscellaneous": "Other expenses"
        }},
        "budget_optimization_tips": ["tip1", "tip2"],
        "cost_saving_alternatives": ["alternative1", "alternative2"]
    }},
    "weather_info": {{
        "current_conditions": "Current weather description",
        "temperature_range": "Min-Max temperature",
        "seasonal_info": "Best time to visit information",
        "weather_recommendations": ["clothing suggestions", "activity recommendations"],
        "climate_considerations": "Weather impact on travel plans"
    }},
    "daily_itinerary": [
        {{
            "day": 1,
            "weather_forecast": "Expected weather for the day",
            "theme_focus": "Day's theme alignment",
            "morning": {{
                "activity": "Morning activity (weather-appropriate)",
                "location": "Location",
                "duration": "Time needed",
                "cost": "Estimated cost",
                "weather_suitability": "Indoor/Outdoor based on weather"
            }},
            "afternoon": {{
                "activity": "Afternoon activity (weather-appropriate)", 
                "location": "Location",
                "duration": "Time needed",
                "cost": "Estimated cost",
                "weather_suitability": "Indoor/Outdoor based on weather"
            }},
            "evening": {{
                "activity": "Evening activity (weather-appropriate)",
                "location": "Location", 
                "duration": "Time needed",
                "cost": "Estimated cost",
                "weather_suitability": "Indoor/Outdoor based on weather"
            }},
            "accommodation": "Where to stay",
            "meals": {{
                "breakfast": "Restaurant recommendation",
                "lunch": "Restaurant recommendation", 
                "dinner": "Restaurant recommendation"
            }},
            "daily_total_cost": "Day's total expense",
            "weather_tips": ["Daily weather-specific tips"]
        }}
    ],
    "booking_summary": {{
        "one_click_bookings_available": true/false,
        "booking_links": {{
            "transportation": "Transport booking URL",
            "hotels": ["Hotel booking URLs"],
            "activities": ["Activity booking URLs"]
        }},
        "booking_instructions": "Step-by-step booking guide"
    }},
    "sources": ["source1", "source2"]
}}

IMPORTANT INSTRUCTIONS:
1. ALWAYS start by calling get_weather_info() to understand the climate and weather conditions
2. Use specialized functions for better results:
   - get_hotels() for accommodation recommendations
   - get_restaurants() for dining suggestions  
   - get_events_activities() for attractions and activities
   - Use google_search() only as fallback when specialized functions fail
3. Consider weather when planning daily activities (indoor vs outdoor)
4. Align all recommendations with the selected travel theme
5. Validate if the budget is sufficient for the trip
6. Include route-specific information for Self mode
7. Provide booking options for Booking mode
8. Create weather-appropriate day-by-day itinerary
9. Suggest seasonal clothing and preparation tips"""
            
            # Send message with tools
            response = chat.send_message(
                enhanced_query,
                tools=[self._create_search_functions()]
            )
            
            # Handle multiple specialized function calls
            function_calls_made = []
            all_search_data = {}
            
            # Process all function calls in the response
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    # Execute the appropriate function
                    search_result = await self._execute_function(function_name, function_args)
                    
                    if search_result['status'] == 'success':
                        function_calls_made.append(f"{function_name}({function_args})")
                        all_search_data[function_name] = search_result
                        
                        # Send function response back to model
                        function_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": search_result}
                            )
                        )
                        
                        # Continue the conversation with function result
                        response = chat.send_message(function_response)
            
            if function_calls_made:
                # Get final response after all function calls
                final_text = response.text if hasattr(response, 'text') else str(response)
                parsed_response = self._parse_and_validate_json(final_text)
                
                return {
                    "status": "success",
                    "query": user_query,
                    "structured_input": structured_input,
                    "agent_response": parsed_response,
                    "method": "specialized_function_calling",
                    "functions_called": function_calls_made,
                    "search_data": all_search_data
                }
            else:
                # Fall back to hybrid approach if no function calls were made
                return await self._hybrid_fallback(user_query)
                
        except Exception as e:
            # Fall back to hybrid approach
            return await self._hybrid_fallback(user_query)

    async def _hybrid_fallback(self, user_query: str) -> Dict[str, Any]:
        """Fallback to direct search + intelligent formatting"""
        try:
            search_result = await travel_planning.google_search(user_query)
            
            if search_result['status'] == 'success':
                # Check if user wants itinerary generation
                needs_itinerary = self._needs_itinerary_generation(user_query)
                
                if needs_itinerary:
                    formatted_response = self._create_intelligent_itinerary(user_query, search_result)
                    method = "hybrid_intelligent_fallback"
                else:
                    formatted_response = self._format_search_results(user_query, search_result)
                    method = "hybrid_search_fallback"
                
                return {
                    "status": "success",
                    "query": user_query,
                    "agent_response": formatted_response,
                    "method": method,
                    "search_data": search_result
                }
            else:
                return {
                    "status": "error",
                    "query": user_query,
                    "error_message": search_result.get('message', 'Search failed')
                }
        except Exception as e:
            return {
                "status": "error",
                "query": user_query,
                "error_message": str(e)
            }



    def _needs_itinerary_generation(self, query: str) -> bool:
        """Determine if the query needs intelligent itinerary generation"""
        itinerary_keywords = [
            'itinerary', 'plan', 'trip', 'visit', 'travel plan', 'schedule',
            'day', 'days', 'budget', 'things to do', 'activities', 'places to visit'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in itinerary_keywords)



    def _create_intelligent_itinerary(self, query: str, search_result: dict) -> str:
        """Create an intelligent itinerary structure from search results in JSON format"""
        import json
        
        # Extract key information from search results
        destinations = []
        budget_info = []
        activities = []
        sources = []
        
        for result in search_result.get('organic_results', [])[:8]:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            link = result.get('link', '')
            
            sources.append(link)
            
            # Extract destinations
            if any(word in title for word in ['places', 'destinations', 'visit']):
                destinations.append({
                    'name': result.get('title', '').replace(' - ', ' '),
                    'description': result.get('snippet', '')[:200],
                    'highlights': self._extract_highlights(result.get('snippet', '')),
                    'source': link
                })
            
            # Extract budget information
            if any(word in title + snippet for word in ['budget', 'cost', 'price', 'rupees', 'inr']):
                budget_info.append({
                    'info': result.get('snippet', ''),
                    'source': link
                })
            
            # Extract activities
            if any(word in title + snippet for word in ['things to do', 'activities', 'attractions']):
                activities.append({
                    'activity': result.get('title', ''),
                    'description': result.get('snippet', '')[:150],
                    'source': link
                })
        
        # Build JSON response
        json_response = {
            "summary": self._generate_summary(query, search_result),
            "destinations": destinations[:5] if destinations else [],
            "practical_info": {
                "transportation": "Check local transportation options",
                "accommodation": "Book accommodations in advance",
                "local_tips": [
                    "Carry necessary documents",
                    "Check weather conditions",
                    "Research local customs"
                ],
                "weather": "Check current weather conditions"
            },
            "sources": sources[:5]
        }
        
        # Add itinerary section if days mentioned
        days_match = self._extract_days(query)
        if days_match:
            daily_plan = []
            for day in range(1, days_match + 1):
                if day == 1:
                    activities_list = ["Arrival and check-in", "Explore nearby attractions", "Local cuisine experience"]
                elif day == days_match:
                    activities_list = ["Final sightseeing", "Shopping for souvenirs", "Departure"]
                else:
                    activities_list = ["Major attractions visit", "Cultural experiences", "Local activities"]
                
                daily_plan.append({
                    "day": day,
                    "activities": activities_list,
                    "locations": ["To be determined based on preferences"]
                })
            
            json_response["itinerary"] = {
                "duration": f"{days_match} days",
                "daily_plan": daily_plan
            }
        
        # Add budget section if budget mentioned
        if any(word in query.lower() for word in ['budget', 'cost', 'rupees', 'price']) and budget_info:
            budget_amount = self._extract_budget(query)
            json_response["budget"] = {
                "total_budget": budget_amount,
                "breakdown": {
                    "accommodation": "40-50% of budget",
                    "transportation": "20-25% of budget",
                    "food": "20-25% of budget",
                    "activities": "10-15% of budget"
                },
                "tips": [
                    "Book in advance for better rates",
                    "Consider local transportation",
                    "Try local street food for budget meals"
                ]
            }
        
        return json.dumps(json_response, indent=2, ensure_ascii=False)

    def _generate_summary(self, query: str, search_result: dict) -> str:
        """Generate a summary from search results"""
        if search_result.get('featured_snippet'):
            return search_result['featured_snippet'].get('snippet', '')[:200]
        elif search_result.get('organic_results'):
            return search_result['organic_results'][0].get('snippet', '')[:200]
        else:
            return f"Travel information for {query}"

    def _extract_highlights(self, text: str) -> list:
        """Extract highlights from text"""
        highlights = []
        # Simple extraction based on common patterns
        if 'beach' in text.lower():
            highlights.append('Beautiful beaches')
        if 'mountain' in text.lower() or 'hill' in text.lower():
            highlights.append('Mountain views')
        if 'temple' in text.lower() or 'heritage' in text.lower():
            highlights.append('Cultural heritage')
        if 'food' in text.lower() or 'cuisine' in text.lower():
            highlights.append('Local cuisine')
        
        return highlights[:3] if highlights else ['Popular destination']

    def _extract_days(self, query: str) -> int:
        """Extract number of days from query"""
        for word in query.lower().split():
            if word.isdigit() and int(word) <= 10:
                return int(word)
            elif '-day' in word:
                try:
                    return int(word.split('-')[0])
                except:
                    continue
        return 0

    def _extract_budget(self, query: str) -> str:
        """Extract budget amount from query"""
        words = query.lower().split()
        for i, word in enumerate(words):
            if word.isdigit() and i < len(words) - 1:
                next_word = words[i + 1]
                if 'rupee' in next_word or 'inr' in next_word:
                    return f"₹{word}"
                elif 'dollar' in next_word or 'usd' in next_word:
                    return f"${word}"
        return "Budget mentioned"

    def _extract_search_data(self, search_result: dict) -> str:
        """Extract and format search data for LLM processing"""
        data = ""
        
        # Add featured snippet
        if search_result.get('featured_snippet'):
            snippet = search_result['featured_snippet']
            data += f"FEATURED ANSWER:\n{snippet.get('snippet', 'N/A')}\nSource: {snippet.get('link', 'N/A')}\n\n"
        
        # Add organic results
        data += "TOP SEARCH RESULTS:\n"
        for i, result in enumerate(search_result.get('organic_results', [])[:8], 1):
            data += f"{i}. {result.get('title', 'No title')}\n"
            data += f"   {result.get('snippet', 'No description')}\n"
            data += f"   Source: {result.get('link', 'No link')}\n\n"
        
        # Add related questions
        if search_result.get('related_questions'):
            data += "RELATED QUESTIONS:\n"
            for q in search_result['related_questions'][:5]:
                data += f"• {q.get('question', 'N/A')}\n"
        
        return data

    def _format_search_results(self, query: str, search_result: dict) -> str:
        """Format search results into JSON response"""
        import json
        
        # Extract destinations and information
        destinations = []
        sources = []
        
        for result in search_result.get('organic_results', [])[:5]:
            destinations.append({
                'name': result.get('title', 'No title'),
                'description': result.get('snippet', 'No description'),
                'highlights': self._extract_highlights(result.get('snippet', '')),
                'source': result.get('link', 'No link')
            })
            sources.append(result.get('link', ''))
        
        json_response = {
            "summary": self._generate_summary(query, search_result),
            "destinations": destinations,
            "practical_info": {
                "transportation": "Research local transportation options",
                "accommodation": "Check accommodation availability",
                "local_tips": [
                    "Check visa requirements",
                    "Research local customs",
                    "Check weather conditions"
                ],
                "weather": "Check current weather and seasonal conditions"
            },
            "sources": sources
        }
        
        # Add featured snippet as quick answer
        if search_result.get('featured_snippet'):
            json_response["quick_answer"] = {
                "text": search_result['featured_snippet'].get('snippet', 'N/A'),
                "source": search_result['featured_snippet'].get('link', 'N/A')
            }
        
        # Add related questions
        if search_result.get('related_questions'):
            json_response["related_questions"] = [
                q.get('question', 'N/A') for q in search_result['related_questions'][:5]
            ]
        
        json_response["metadata"] = {
            "total_results": search_result.get('total_results', 0),
            "search_query": query
        }
        
        return json.dumps(json_response, indent=2, ensure_ascii=False)

    def _parse_and_validate_json(self, response_text: str) -> str:
        """Parse and validate JSON response from LLM"""
        import json
        import re
        
        try:
            # Try to extract JSON from the response
            # Look for JSON block in the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Look for JSON object starting with {
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    # If no JSON found, create a simple JSON wrapper
                    return json.dumps({
                        "summary": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                        "full_response": response_text,
                        "format": "text"
                    }, indent=2, ensure_ascii=False)
            
            # Try to parse the JSON
            parsed_json = json.loads(json_text)
            
            # Validate required fields and add defaults if missing
            if not isinstance(parsed_json, dict):
                raise ValueError("Response is not a JSON object")
            
            # Ensure required fields exist
            if 'summary' not in parsed_json:
                parsed_json['summary'] = "Travel information provided"
            
            if 'sources' not in parsed_json:
                parsed_json['sources'] = []
            
            return json.dumps(parsed_json, indent=2, ensure_ascii=False)
            
        except (json.JSONDecodeError, ValueError) as e:
            # Return a structured JSON response even if parsing fails
            return json.dumps({
                "summary": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "full_response": response_text,
                "format": "text",
                "parsing_error": str(e)
            }, indent=2, ensure_ascii=False)

    def _parse_query_to_structure(self, query: str) -> dict:
        """Parse a natural language query into structured input"""
        # Simple parsing logic - can be enhanced with NLP
        structure = {
            'source': 'Not specified',
            'destination': 'Not specified', 
            'travel_mode': 'Not specified',
            'budget': 'Not specified',
            'theme': 'Not specified',
            'duration': 'Not specified'
        }
        
        query_lower = query.lower()
        
        # Extract travel mode
        if any(word in query_lower for word in ['flight', 'train', 'bus', 'cab', 'booking']):
            structure['travel_mode'] = 'Booking'
        elif any(word in query_lower for word in ['car', 'bike', 'drive', 'self']):
            structure['travel_mode'] = 'Self'
        
        # Extract theme
        if any(word in query_lower for word in ['temple', 'devotional', 'religious', 'spiritual']):
            structure['theme'] = 'Devotional'
        elif any(word in query_lower for word in ['adventure', 'trekking', 'hiking', 'sports']):
            structure['theme'] = 'Adventurous'
        elif any(word in query_lower for word in ['nightlife', 'party', 'club', 'bar']):
            structure['theme'] = 'Nightlife'
        elif any(word in query_lower for word in ['culture', 'heritage', 'museum', 'history']):
            structure['theme'] = 'Cultural'
        else:
            structure['theme'] = 'General'
        
        # Extract budget
        import re
        budget_match = re.search(r'(\d+)\s*(?:rupees?|inr|₹)', query_lower)
        if budget_match:
            structure['budget'] = f"₹{budget_match.group(1)}"
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*days?', query_lower)
        if duration_match:
            structure['duration'] = f"{duration_match.group(1)} days"
        
        return structure

    def _structure_to_query(self, structure: dict) -> str:
        """Convert structured input to natural language query"""
        parts = []
        
        if structure.get('source') and structure.get('destination'):
            parts.append(f"Plan a trip from {structure['source']} to {structure['destination']}")
        elif structure.get('destination'):
            parts.append(f"Plan a trip to {structure['destination']}")
        
        if structure.get('budget'):
            parts.append(f"with budget {structure['budget']}")
        
        if structure.get('duration'):
            parts.append(f"for {structure['duration']}")
        
        if structure.get('theme'):
            parts.append(f"focusing on {structure['theme'].lower()} theme")
        
        if structure.get('travel_mode'):
            if structure['travel_mode'] == 'Self':
                parts.append("using own vehicle")
            else:
                parts.append("using public transport/booking")
        
        return " ".join(parts) if parts else "Plan a personalized trip"

    async def _execute_function(self, function_name: str, function_args: dict) -> Dict[str, Any]:
        """Execute the appropriate specialized function"""
        try:
            if function_name == "get_weather_info":
                location = function_args.get("location", "")
                date_range = function_args.get("date_range", "current")
                return await travel_planning.get_weather_info(location, date_range)
            
            elif function_name == "get_hotels":
                location = function_args.get("location", "")
                budget_range = function_args.get("budget_range", "")
                theme = function_args.get("theme", "")
                return await travel_planning.get_hotels(location, budget_range, theme)
            
            elif function_name == "get_restaurants":
                location = function_args.get("location", "")
                cuisine_type = function_args.get("cuisine_type", "")
                theme = function_args.get("theme", "")
                return await travel_planning.get_restaurants(location, cuisine_type, theme)
            
            elif function_name == "get_events_activities":
                location = function_args.get("location", "")
                theme = function_args.get("theme", "")
                date_range = function_args.get("date_range", "")
                return await travel_planning.get_events_activities(location, theme, date_range)
            
            elif function_name == "google_search":
                query = function_args.get("query", "")
                return await travel_planning.google_search(query)
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown function: {function_name}"
                }
                
        except Exception as e:
            # Fallback to general search if specialized function fails
            fallback_query = f"{function_name} {' '.join(str(v) for v in function_args.values())}"
            return await travel_planning.google_search(fallback_query)

    def validate_budget(self, source: str, destination: str, travel_mode: str, duration: str, budget: str) -> dict:
        """Validate if budget is sufficient for the trip"""
        
        # Extract numeric budget
        import re
        budget_match = re.search(r'(\d+)', budget)
        if not budget_match:
            return {"valid": False, "message": "Invalid budget format"}
        
        budget_amount = int(budget_match.group(1))
        
        # Simple budget validation logic (can be enhanced with real data)
        base_costs = {
            "Self": {
                "per_day": 2000,  # Base cost per day for self travel
                "fuel_multiplier": 0.1  # 10% of budget for fuel
            },
            "Booking": {
                "per_day": 3000,  # Base cost per day for booking mode
                "transport_base": 2000  # Base transport cost
            }
        }
        
        # Extract duration
        duration_match = re.search(r'(\d+)', duration)
        days = int(duration_match.group(1)) if duration_match else 3
        
        # Calculate minimum required budget
        if travel_mode == "Self":
            min_budget = (base_costs["Self"]["per_day"] * days) + (budget_amount * base_costs["Self"]["fuel_multiplier"])
        else:
            min_budget = (base_costs["Booking"]["per_day"] * days) + base_costs["Booking"]["transport_base"]
        
        if budget_amount >= min_budget:
            return {
                "valid": True, 
                "message": "Budget is sufficient",
                "minimum_required": min_budget,
                "user_budget": budget_amount
            }
        else:
            return {
                "valid": False,
                "message": f"Budget insufficient. Minimum required: ₹{min_budget}",
                "minimum_required": min_budget,
                "user_budget": budget_amount,
                "shortfall": min_budget - budget_amount
            }

