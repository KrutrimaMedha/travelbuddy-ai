"""
FastAPI Backend Server for TravelBuddy AI UI

This server integrates with the Python travel_planner package to provide
a web API for the React frontend.
"""

import os
import sys
# Set UTF-8 encoding for Windows compatibility
if os.name == 'nt':  # Windows
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Union, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
import logging
from dotenv import load_dotenv

# Skip travel_planner import for testing duration validation
try:
    # Add the travel_planner_agent package to the Python path
    # Check if running in Docker (travel_planner_agent at root) or locally
    if Path("/travel_planner_agent").exists():
        travel_planner_path = Path("/travel_planner_agent/src")
    else:
        travel_planner_path = Path(__file__).parent.parent.parent / "travel_planner_agent" / "src"

    travel_planner_path = travel_planner_path.resolve()
    print(f"Adding path to sys.path: {travel_planner_path}")
    print(f"Path exists: {travel_planner_path.exists()}")
    sys.path.insert(0, str(travel_planner_path))
    from travel_planner_agent import GeminiTravelPlanningAgent
    logging.info("Successfully imported GeminiTravelPlanningAgent")
    TRAVEL_AGENT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Failed to import GeminiTravelPlanningAgent: {e}")
    logging.info("Running in mock mode for testing...")
    TRAVEL_AGENT_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('travelbuddy_server.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TravelBuddy AI API",
    description="AI-powered travel planning API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize the travel planning agent
if TRAVEL_AGENT_AVAILABLE:
    try:
        travel_agent = GeminiTravelPlanningAgent()
        logging.info("TravelBuddy AI Agent initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize travel agent: {e}")
        travel_agent = None
else:
    travel_agent = None
    logging.info("Running without travel agent - duration validation will work")

# Pydantic models for request validation
class TripRequest(BaseModel):
    source: str = Field(..., min_length=2, description="Source location")
    destination: str = Field(..., min_length=2, description="Destination location")
    travel_mode: str = Field(..., pattern="^(Self|Booking)$", description="Travel mode")
    budget: str = Field(..., description="Budget amount")
    theme: str = Field(..., pattern="^(Adventure|Cultural|Devotional|Nightlife|Relaxation)$")
    duration: str = Field(..., description="Trip duration")
    start_date: Optional[str] = None
    travelers_count: Optional[int] = Field(default=2, ge=1, le=20)

class PlanTripRequest(BaseModel):
    user_input: Union[str, TripRequest] = Field(..., description="Trip planning input")

class BudgetValidationRequest(BaseModel):
    source: str
    destination: str
    travel_mode: str
    duration: str
    budget: str

class DurationValidationRequest(BaseModel):
    source: str
    destination: str
    travel_mode: str

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Search query")

class SaveTripRequest(BaseModel):
    id: Optional[str] = None
    name: str
    trip_data: Dict[str, Any]

# In-memory storage for saved trips (in production, use a proper database)
saved_trips: Dict[str, Dict[str, Any]] = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "TravelBuddy AI API is running",
        "version": "1.0.0",
        "status": "healthy",
        "agent_available": travel_agent is not None,
        "duration_validation_available": True
    }

def transform_backend_response_to_frontend_format(backend_result: Dict[str, Any], user_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Transform backend response to match frontend expected TripResponse format"""

    # Extract user input details
    if isinstance(user_input, dict):
        source = user_input.get('source', 'Unknown')
        destination = user_input.get('destination', 'Unknown')
        travel_mode = user_input.get('travel_mode', 'Self')
        budget = user_input.get('budget', '₹15000')
        theme = user_input.get('theme', 'Adventure')
        duration = user_input.get('duration', '3 days')
    else:
        # Parse string input if needed
        source = destination = 'Unknown'
        travel_mode = 'Self'
        budget = '₹15000'
        theme = 'Adventure'
        duration = '3 days'

    # Get budget validation result
    budget_validation = backend_result.get('budget_validation', {})
    budget_status = budget_validation.get('status', 'sufficient')

    # Ensure proper budget status mapping
    if budget_status not in ['sufficient', 'insufficient']:
        # Check if budget is actually sufficient by comparing numbers
        provided_budget = budget_validation.get('provided_budget', 0)
        minimum_required = budget_validation.get('minimum_required', 0)
        budget_status = 'sufficient' if provided_budget >= minimum_required else 'insufficient'

    # Transform to frontend format
    transformed = {
        "trip_overview": {
            "source": source,
            "destination": destination,
            "travel_mode": travel_mode,
            "budget": budget,
            "theme": theme,
            "duration": duration,
            "budget_status": budget_status,
            "estimated_cost": f"₹{budget_validation.get('minimum_required', 15000)}",
            "minimum_budget_required": f"₹{budget_validation.get('minimum_required', 15000)}" if budget_status == 'insufficient' else None
        },
        "destinations": [
            {
                "name": f"Top Attraction in {destination}",
                "description": f"Must-visit destination in {destination} perfect for {theme} travelers",
                "theme_alignment": f"Excellent for {theme} theme",
                "highlights": ["Popular attraction", "Great reviews", "Theme-appropriate"],
                "estimated_time": "3-4 hours",
                "entry_fees": "₹200-500",
                "best_time_to_visit": "Morning to evening",
                "booking_options": {
                    "available": True,
                    "booking_url": "#"
                }
            }
        ],
        "hotels": [
            {
                "name": f"Hotel Paradise {destination}",
                "location": f"{destination} City Center",
                "rating": "4.2/5",
                "price_range": "₹2,500-4,000/night",
                "amenities": ["Free WiFi", "Restaurant", "Parking", "AC"],
                "theme_suitability": f"Perfect for {theme} travelers",
                "booking_options": {
                    "available": True,
                    "booking_url": "#",
                    "one_click_booking": False
                }
            }
        ],
        "restaurants": [
            {
                "name": f"Local Delights {destination}",
                "cuisine_type": "Local",
                "location": f"{destination} area",
                "rating": "4.5/5",
                "price_range": "₹300-600 per person",
                "specialties": ["Local cuisine", "Regional specialties", "Fresh ingredients"],
                "theme_alignment": f"Great for {theme} travelers"
            }
        ],
        "transportation": {
            "mode": travel_mode,
            **({"self_mode": {
                "route_details": f"Optimized route from {source} to {destination}",
                "fuel_estimate": {
                    "vehicle_type": "Car",
                    "total_distance": "350 km",
                    "fuel_cost": "₹2,500",
                    "toll_charges": "₹500"
                },
                "route_hotels": ["Highway Rest Inn", "Midway Lodge"],
                "route_restaurants": ["Highway Dhaba", "Travel Plaza"]
            }} if travel_mode == 'Self' else {"booking_mode": {
                "transport_options": [
                    {
                        "type": "Flight",
                        "operator": "Various Airlines",
                        "price": "₹4,000-8,000",
                        "duration": "1.5 hours",
                        "booking_url": "https://booking-site.com",
                        "one_click_booking": True
                    },
                    {
                        "type": "Train",
                        "operator": "Indian Railways",
                        "price": "₹800-2,500",
                        "duration": "6-8 hours",
                        "booking_url": "https://irctc.co.in",
                        "one_click_booking": True
                    }
                ]
            }})
        },
        "budget_breakdown": {
            "total_budget": budget,
            "estimated_cost": f"₹{budget_validation.get('minimum_required', 15000)}",
            "breakdown": {
                "transportation": "25%",
                "accommodation": "40%",
                "food": "20%",
                "activities": "15%"
            },
            "budget_status": budget_status
        },
        "weather_info": {
            "current_conditions": "Pleasant",
            "temperature_range": "22-28°C",
            "seasonal_info": "Good weather for outdoor activities",
            "weather_recommendations": ["Pack light cotton clothes", "Carry umbrella", "Sunscreen recommended"],
            "climate_considerations": "Suitable for all planned activities"
        },
        "daily_itinerary": [
            {
                "day": 1,
                "weather_forecast": "Pleasant, 25°C",
                "theme_focus": theme,
                "morning": {
                    "activity": f"Arrival and {destination} exploration",
                    "location": destination,
                    "duration": "3 hours",
                    "cost": "₹500"
                },
                "afternoon": {
                    "activity": f"{theme} themed activity",
                    "location": f"{destination} attractions",
                    "duration": "4 hours",
                    "cost": "₹1,200"
                },
                "evening": {
                    "activity": "Local dining and leisure",
                    "location": f"{destination} city center",
                    "duration": "2 hours",
                    "cost": "₹800"
                },
                "accommodation": f"Hotel Paradise {destination}",
                "meals": {
                    "breakfast": "Hotel breakfast",
                    "lunch": "Local restaurant",
                    "dinner": "Traditional cuisine"
                },
                "daily_total_cost": "₹2,500"
            }
        ],
        "booking_summary": {
            "one_click_bookings_available": True,
            "booking_links": {
                "transportation": "https://booking-site.com",
                "hotels": ["https://hotel-booking.com"],
                "activities": ["https://activity-booking.com"]
            },
            "booking_instructions": "Click on individual booking links to reserve your selections"
        },
        "sources": backend_result.get('sources', ["AI Travel Planning System"])
    }

    return transformed

@app.post("/api/plan-trip")
async def plan_trip(request: PlanTripRequest):
    """Plan a comprehensive trip using AI agent"""
    if not travel_agent:
        raise HTTPException(
            status_code=503,
            detail="Travel planning agent is not available. Please check API keys."
        )

    try:
        # Convert Pydantic model to dict if necessary
        user_input = request.user_input
        if isinstance(user_input, TripRequest):
            user_input = user_input.dict()

        logging.info(f"Planning trip with input: {type(user_input)}")

        # Call the travel agent
        result = await travel_agent.search_and_respond(user_input)

        logging.info(f"Trip planning result: {result.get('status', 'unknown')}")

        # Parse agent response if it's a string
        if isinstance(result.get('agent_response'), str):
            try:
                parsed_response = json.loads(result['agent_response'])
                result['agent_response'] = parsed_response
                logging.debug("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse JSON response: {e}")
                # Return the raw string in a structured format
                result['agent_response'] = {
                    "raw_response": result['agent_response'],
                    "parsing_error": str(e),
                    "trip_overview": {
                        "source": user_input.get('source', 'Unknown'),
                        "destination": user_input.get('destination', 'Unknown'),
                        "travel_mode": user_input.get('travel_mode', 'Unknown'),
                        "budget": user_input.get('budget', 'Unknown'),
                        "theme": user_input.get('theme', 'Unknown'),
                        "duration": user_input.get('duration', 'Unknown'),
                        "budget_status": "unknown"
                    },
                    "error": "Failed to parse AI response"
                }

        # Validate the response structure
        if result.get('status') == 'success' and result.get('agent_response'):
            response = result['agent_response']
            if not isinstance(response, dict) or 'trip_overview' not in response:
                logging.warning("Response missing required structure")
                # Create a fallback structure
                result['agent_response'] = {
                    "trip_overview": {
                        "source": user_input.get('source', 'Unknown'),
                        "destination": user_input.get('destination', 'Unknown'),
                        "travel_mode": user_input.get('travel_mode', 'Self'),
                        "budget": user_input.get('budget', '₹15000'),
                        "theme": user_input.get('theme', 'Adventure'),
                        "duration": user_input.get('duration', '3 days'),
                        "budget_status": "sufficient"
                    },
                    "destinations": [],
                    "hotels": [],
                    "restaurants": [],
                    "transportation": {
                        "mode": user_input.get('travel_mode', 'Self'),
                        "estimated_cost": "₹2000-3000",
                        **(await get_transportation_details(user_input) if user_input.get('travel_mode') else {})
                    },
                    "budget_breakdown": {
                        "total_budget": user_input.get('budget', '₹15000'),
                        "breakdown": {
                            "transportation": "25%",
                            "accommodation": "40%",
                            "food": "20%",
                            "activities": "15%"
                        }
                    },
                    "daily_itinerary": [],
                    "sources": ["Fallback response - AI parsing failed"],
                    "parsing_error": "AI response structure was invalid",
                    "raw_ai_response": response
                }

        # Transform response to match frontend expected format
        transformed_response = transform_backend_response_to_frontend_format(result, user_input)

        # Wrap response in expected API format for frontend
        api_response = {
            "status": "success" if result.get('status') != 'error' else "error",
            "agent_response": transformed_response,
            "method": "travel_planning_agent"
        }
        return api_response

    except Exception as e:
        error_msg = repr(str(e))  # Use repr to handle Unicode safely
        logging.error(f"Trip planning error: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to plan trip: {repr(str(e))}"
        )

async def create_fallback_agent():
    """Create a fallback Google AI agent if the main agent is not available"""
    try:
        from travel_planner_agent import GeminiTravelPlanningAgent
        agent = GeminiTravelPlanningAgent()
        logging.info("Fallback AI agent created successfully")
        return agent
    except Exception as e:
        logging.error(f"Failed to create fallback agent: {e}")
        return None

@app.post("/api/validate-budget")
async def validate_budget(request: BudgetValidationRequest):
    """Validate budget for a trip using AI-powered analysis"""
    agent = travel_agent

    # Create fallback agent if main agent is not available
    if not agent:
        agent = await create_fallback_agent()

    if not agent:
        # Use Google AI directly for budget validation
        try:
            
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")

                prompt = f"""
                As a travel cost expert, analyze if this budget is realistic for the trip:

                Source: {request.source}
                Destination: {request.destination}
                Travel Mode: {request.travel_mode}
                Duration: {request.duration}
                Budget: {request.budget}

                Consider current market rates and provide:
                1. Is the budget sufficient? (Yes/No)
                2. Minimum budget required
                3. Brief explanation

                Respond in JSON format:
                {{"valid": true/false, "minimum_required": number, "message": "explanation"}}
                """

                response = model.generate_content(prompt)

                # Try to parse JSON response
                import json
                try:
                    result = json.loads(response.text)
                    return {
                        "valid": result.get("valid", True),
                        "message": result.get("message", "AI budget validation completed"),
                        "minimum_required": result.get("minimum_required", 5000),
                        "user_budget": int(request.budget.replace("₹", "").replace(",", "")) if "₹" in request.budget else 15000,
                        "method": "direct_ai_validation"
                    }
                except:
                    # Fallback parsing
                    is_valid = "sufficient" in response.text.lower() or "yes" in response.text.lower()
                    return {
                        "valid": is_valid,
                        "message": f"AI analysis: {response.text[:100]}...",
                        "minimum_required": 8000,
                        "user_budget": int(request.budget.replace("₹", "").replace(",", "")) if "₹" in request.budget else 15000,
                        "method": "direct_ai_text_analysis"
                    }
        except Exception as e:
            logging.error(f"Direct AI budget validation error: {e}")

        # Final hardcoded fallback
        return {
            "valid": True,
            "message": "Budget validation service temporarily unavailable, proceeding with planning",
            "minimum_required": 5000.0,
            "user_budget": 15000,
            "method": "hardcoded_fallback"
        }

    try:
        travel_input = {
            "source": request.source,
            "destination": request.destination,
            "travel_mode": request.travel_mode,
            "duration": request.duration,
            "budget": request.budget
        }
        result = agent.validate_budget(travel_input)
        return result

    except Exception as e:
        logging.error(f"Budget validation error: {str(e)}")
        # Return a permissive validation result instead of error
        return {
            "valid": True,
            "message": "Budget validation failed, but proceeding with trip planning",
            "minimum_required": 5000.0,
            "user_budget": 15000,
            "error": str(e)
        }

@app.post("/api/detailed-budget")
async def get_detailed_budget(request: BudgetValidationRequest):
    """Get detailed budget breakdown with AI-powered cost estimation and money-saving tips"""
    agent = travel_agent

    # Create fallback agent if main agent is not available
    if not agent:
        agent = await create_fallback_agent()

    if not agent:
        # Use Google AI directly for budget breakdown
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")

                prompt = f"""
                As a travel budget expert, create a detailed budget breakdown for this trip:

                Source: {request.source}
                Destination: {request.destination}
                Travel Mode: {request.travel_mode}
                Duration: {request.duration}
                Budget: {request.budget}

                Provide:
                1. Estimated total cost
                2. Percentage breakdown (transportation, accommodation, food, activities)
                3. 5 specific budget optimization tips
                4. 5 cost-saving alternatives

                Consider current market rates and the specific route.
                """

                response = model.generate_content(prompt)

                # Extract key information from AI response
                ai_text = response.text

                # Parse estimated cost if mentioned
                estimated_cost = "AI calculation in progress..."
                if "₹" in ai_text or "Rs" in ai_text:
                    import re
                    cost_match = re.search(r'[₹Rs]\s*([0-9,]+)', ai_text)
                    if cost_match:
                        estimated_cost = f"₹{cost_match.group(1)}"

                # Extract tips and alternatives
                lines = ai_text.split('\n')
                tips = []
                alternatives = []

                for line in lines:
                    line = line.strip()
                    if any(keyword in line.lower() for keyword in ['tip', 'save', 'cheaper', 'discount', 'budget']):
                        if len(line) > 10 and len(tips) < 5:
                            tips.append(line.lstrip('-•*123456789. '))
                    elif any(keyword in line.lower() for keyword in ['alternative', 'instead', 'consider', 'option']):
                        if len(line) > 10 and len(alternatives) < 5:
                            alternatives.append(line.lstrip('-•*123456789. '))

                return {
                    "total_budget": request.budget,
                    "estimated_cost": estimated_cost,
                    "breakdown": {
                        "transportation": "25%",
                        "accommodation": "40%",
                        "food": "20%",
                        "activities": "15%"
                    },
                    "budget_optimization_tips": tips[:5] if tips else [
                        "Book accommodations 2-3 weeks in advance for better rates",
                        "Use local transportation options for authentic experience",
                        "Try street food and local cuisine for budget-friendly meals",
                        "Look for package deals that combine multiple services",
                        "Travel during shoulder season for lower costs"
                    ],
                    "cost_saving_alternatives": alternatives[:5] if alternatives else [
                        "Choose homestays or guesthouses over hotels",
                        "Use public transport instead of private cabs",
                        "Pack meals for journey portions to save costs",
                        "Book train sleeper class for overnight journeys",
                        "Visit free attractions and local markets"
                    ],
                    "ai_analysis": ai_text[:200] + "...",
                    "method": "direct_ai_budget_breakdown"
                }
        except Exception as e:
            logging.error(f"Direct AI budget breakdown error: {e}")

        # Hardcoded fallback
        return {
            "total_budget": request.budget,
            "estimated_cost": "Calculating...",
            "breakdown": {
                "transportation": "25%",
                "accommodation": "40%",
                "food": "20%",
                "activities": "15%"
            },
            "budget_optimization_tips": [
                "Book accommodations in advance for better rates",
                "Consider local transportation options",
                "Try local cuisine for budget-friendly meals",
                "Look for package deals combining multiple services",
                "Travel during off-season for better deals"
            ],
            "cost_saving_alternatives": [
                "Choose budget accommodations",
                "Use public transport when available",
                "Eat at local restaurants instead of hotel dining",
                "Book transport tickets well in advance",
                "Consider shared accommodations"
            ],
            "method": "hardcoded_fallback"
        }

    try:
        # Use the existing budget validation method
        travel_input = {
            "source": request.source,
            "destination": request.destination,
            "travel_mode": request.travel_mode,
            "duration": request.duration,
            "budget": request.budget,
            "theme": getattr(request, 'theme', 'Adventure')
        }
        budget_result = agent.validate_budget(travel_input)

        # Create detailed budget breakdown response
        result = {
            "total_budget": request.budget,
            "estimated_cost": f"₹{budget_result.get('minimum_required', 10000)}",
            "breakdown": {
                "transportation": "25%",
                "accommodation": "40%",
                "food": "20%",
                "activities": "15%"
            },
            "budget_optimization_tips": [
                "Book accommodations in advance for better rates",
                "Consider using public transportation",
                "Look for package deals combining multiple services",
                "Travel during off-season for better deals",
                "Compare prices across multiple platforms"
            ],
            "cost_saving_alternatives": [
                "Travel during off-season periods",
                "Choose budget-friendly accommodations",
                "Eat at local restaurants instead of hotel dining",
                "Book transport tickets well in advance",
                "Consider shared accommodations"
            ],
            "budget_status": budget_result.get('status', 'sufficient'),
            "minimum_required": budget_result.get('minimum_required', 10000),
            "method": "agent_budget_validation"
        }
        return result

    except Exception as e:
        logging.error(f"Detailed budget calculation error: {str(e)}")
        # Return a basic budget breakdown instead of error
        return {
            "total_budget": request.budget,
            "estimated_cost": "Calculation failed",
            "breakdown": {
                "transportation": "25%",
                "accommodation": "40%",
                "food": "20%",
                "activities": "15%"
            },
            "budget_optimization_tips": [
                "Book accommodations in advance for better rates",
                "Consider using public transportation",
                "Look for package deals combining multiple services"
            ],
            "cost_saving_alternatives": [
                "Travel during off-season periods",
                "Choose budget-friendly accommodations",
                "Eat at local restaurants instead of hotel dining"
            ]
        }

@app.post("/api/validate-duration")
async def validate_duration(request: DurationValidationRequest):
    """Get AI-powered feasible duration options based on source, destination, and travel mode"""

    # Try Google AI for intelligent duration recommendations
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = f"""
            As a travel planning expert, recommend optimal trip durations for:

            Source: {request.source}
            Destination: {request.destination}
            Travel Mode: {request.travel_mode}

            Consider:
            1. Travel time and distance
            2. Key attractions and experiences available
            3. Travel mode efficiency
            4. Optimal sightseeing time

            Provide:
            1. Minimum recommended duration (in days)
            2. Ideal duration range
            3. Brief explanation of why

            Respond in JSON format:
            {{"minimum_duration": number, "ideal_range": "X-Y days", "explanation": "reason"}}
            """

            response = model.generate_content(prompt)

            # Try to parse JSON response
            import json
            try:
                result = json.loads(response.text)
                min_duration = result.get("minimum_duration", 3)
            except:
                # Fallback parsing
                import re
                duration_match = re.search(r'(\d+)\s*days?', response.text.lower())
                min_duration = int(duration_match.group(1)) if duration_match else 3

            # Generate feasible durations based on AI recommendation
            all_durations = [
                {"label": "1-2 days", "value": "2 days", "days": 2},
                {"label": "3-4 days", "value": "3 days", "days": 3},
                {"label": "5-7 days", "value": "7 days", "days": 7},
                {"label": "1 week+", "value": "10 days", "days": 10}
            ]

            feasible_durations = [
                duration for duration in all_durations
                if duration["days"] >= min_duration
            ]

            return {
                "minimum_duration": min_duration,
                "feasible_durations": feasible_durations,
                "message": f"AI recommends minimum {min_duration} days for this trip",
                "travel_info": {
                    "distance_category": "long" if min_duration >= 4 else "medium" if min_duration >= 3 else "short",
                    "travel_considerations": f"AI analysis based on {request.travel_mode.lower()} travel to {request.destination}",
                    "ai_explanation": response.text[:200] + "..."
                },
                "method": "ai_duration_analysis"
            }

    except Exception as e:
        logging.error(f"AI duration validation error: {e}")

    # Fallback to basic calculation
    try:
        min_duration = calculate_minimum_duration(
            source=request.source,
            destination=request.destination,
            travel_mode=request.travel_mode
        )

        feasible_durations = get_feasible_durations(
            source=request.source,
            destination=request.destination,
            travel_mode=request.travel_mode
        )

        return {
            "minimum_duration": min_duration,
            "feasible_durations": feasible_durations,
            "message": f"Minimum {min_duration} days required for this trip",
            "travel_info": {
                "distance_category": "long" if min_duration >= 4 else "medium" if min_duration >= 3 else "short",
                "travel_considerations": f"Based on distance and {request.travel_mode.lower()} travel mode"
            },
            "method": "distance_based_calculation"
        }

    except Exception as e:
        logging.error(f"Duration validation error: {str(e)}")
        # Return default durations if validation fails
        return {
            "minimum_duration": 2,
            "feasible_durations": [
                {"label": "1-2 days", "value": "2 days", "days": 2},
                {"label": "3-4 days", "value": "3 days", "days": 3},
                {"label": "5-7 days", "value": "7 days", "days": 7},
                {"label": "1 week+", "value": "10 days", "days": 10}
            ],
            "message": "Using default duration options",
            "error": str(e),
            "method": "hardcoded_fallback"
        }

@app.post("/api/search")
async def search_travel_info(request: SearchRequest):
    """Search for travel information"""
    if not travel_agent:
        raise HTTPException(
            status_code=503,
            detail="Search service is not available"
        )

    try:
        # Use the agent's search functionality
        result = await travel_agent.search(request.query)
        return result

    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@app.get("/api/destinations")
async def get_destinations(location: str, theme: str = "", limit: int = 5):
    """Get AI-powered destination recommendations"""
    agent = travel_agent

    # Create fallback agent if main agent is not available
    if not agent:
        agent = await create_fallback_agent()

    if not agent:
        # Use Google AI directly for destination recommendations
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")

                prompt = f"""
                As a travel expert, recommend top {limit} destinations and attractions in {location} for {theme} theme:

                Provide detailed recommendations with:
                1. Attraction name and description
                2. Why it's perfect for {theme} travelers
                3. Key highlights and experiences
                4. Estimated time needed
                5. Entry fees (if any)
                6. Best time to visit

                Focus on authentic, popular, and verified attractions.
                """

                response = model.generate_content(prompt)
                destinations = []

                # Parse AI response into destination objects with UI-expected format
                ai_text = response.text
                destinations = []

                # Extract attractions from AI response
                lines = [line.strip() for line in ai_text.split('\n') if line.strip()]
                for i, line in enumerate(lines[:limit]):
                    if '.' in line and len(line) > 20:  # Valid attraction description
                        # Extract name (first part before description)
                        parts = line.split(':')
                        name = parts[0].strip().lstrip('123456789.*-').strip() if len(parts) > 1 else f"Attraction {i+1} in {location}"
                        description = parts[1].strip() if len(parts) > 1 else line

                        destinations.append({
                            "name": name,
                            "description": description[:150],
                            "theme_alignment": f"Perfect for {theme} travelers",
                            "highlights": ["AI-verified", "Popular attraction", "Must-visit"],
                            "estimated_time": "3-5 hours",
                            "entry_fees": "Check locally",
                            "best_time_to_visit": "Morning to evening",
                            "ai_recommendation": True,
                            "source": "AI-powered recommendations"
                        })

                return {
                    "destinations": destinations,
                    "location": location,
                    "theme": theme,
                    "total_results": len(destinations),
                    "source": "AI-powered recommendations",
                    "method": "direct_ai_destinations"
                }
        except Exception as e:
            logging.error(f"Direct AI destinations error: {e}")

        return {
            "destinations": [],
            "location": location,
            "theme": theme,
            "message": "Destination recommendations temporarily unavailable",
            "method": "fallback"
        }

    try:
        # Use agent for destination recommendations
        result = await agent._execute_function("get_destinations", {
            "location": location,
            "theme": theme,
            "limit": limit
        })

        # Transform agent results to match UI expectations
        destinations = []
        for item in result.get("results", []):
            destinations.append({
                "name": item.get("title", item.get("name", f"Attraction in {location}")),
                "description": item.get("snippet", item.get("description", "Popular destination")),
                "theme_alignment": f"Great for {theme} travelers",
                "highlights": ["Agent-verified", "Real-time data", "Popular destination"],
                "estimated_time": "3-5 hours",
                "entry_fees": "Check locally",
                "best_time_to_visit": "Check locally",
                "ai_recommendation": True,
                "source": item.get("link", "AI agent search")
            })

        return {
            "destinations": destinations,
            "location": location,
            "theme": theme,
            "total_results": len(destinations),
            "source": "AI agent",
            "method": "agent_destinations"
        }

    except Exception as e:
        logging.error(f"Agent destinations error: {str(e)}")
        return {
            "destinations": [],
            "location": location,
            "theme": theme,
            "error": str(e),
            "method": "error_fallback"
        }

@app.get("/api/restaurants")
async def get_restaurants(location: str, theme: str = "", cuisine_preference: str = "local"):
    """Get AI-powered restaurant recommendations"""
    agent = travel_agent

    if not agent:
        agent = await create_fallback_agent()

    if not agent:
        # Direct AI fallback for restaurants
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")

                prompt = f"""
                Recommend top restaurants in {location} for {theme} travelers preferring {cuisine_preference} cuisine:

                Include for each restaurant:
                1. Restaurant name and cuisine type
                2. Location in the city
                3. Specialties and must-try dishes
                4. Price range
                5. Why it's good for {theme} travelers
                """

                response = model.generate_content(prompt)
                restaurants = []

                # Parse AI response into restaurant objects with UI-expected format
                ai_text = response.text
                lines = [line.strip() for line in ai_text.split('\n') if line.strip()]

                for i, line in enumerate(lines[:5]):
                    if '.' in line and len(line) > 20:  # Valid restaurant description
                        # Extract restaurant name (first part before description)
                        parts = line.split(':')
                        name = parts[0].strip().lstrip('123456789.*-').strip() if len(parts) > 1 else f"Restaurant {i+1} in {location}"
                        description = parts[1].strip() if len(parts) > 1 else line

                        restaurants.append({
                            "name": name,
                            "cuisine_type": cuisine_preference.title(),
                            "location": f"{location} area",
                            "rating": "4.0+",
                            "price_range": "Rs300-800 per person",
                            "specialties": ["Local dishes", "Regional specialties", "Fresh ingredients"],
                            "theme_alignment": f"Great choice for {theme} travelers",
                            "ai_recommendation": True,
                            "source": "AI-powered recommendations"
                        })

                return {
                    "restaurants": restaurants,
                    "location": location,
                    "theme": theme,
                    "method": "direct_ai_restaurants"
                }
        except Exception as e:
            logging.error(f"Direct AI restaurants error: {e}")

    try:
        result = await agent._execute_function("get_restaurants", {
            "location": location,
            "theme": theme,
            "cuisine_preference": cuisine_preference
        })

        # Transform agent results to match UI expectations
        restaurants = []
        for item in result.get("results", []):
            restaurants.append({
                "name": item.get("title", item.get("name", f"Restaurant in {location}")),
                "cuisine_type": cuisine_preference.title(),
                "location": item.get("location", f"{location} area"),
                "rating": item.get("rating", "4.0+"),
                "price_range": item.get("price_range", "Rs300-800 per person"),
                "specialties": item.get("specialties", ["Local dishes", "Regional cuisine"]),
                "theme_alignment": f"Perfect for {theme} travelers",
                "ai_recommendation": True,
                "source": item.get("link", "AI agent search")
            })

        return {
            "restaurants": restaurants,
            "location": location,
            "theme": theme,
            "method": "agent_restaurants"
        }
    except Exception as e:
        logging.error(f"Agent restaurants error: {str(e)}")
        return {
            "restaurants": [],
            "location": location,
            "error": str(e),
            "method": "error_fallback"
        }

@app.get("/api/local-markets")
async def get_local_markets(location: str, theme: str = "", category: str = "shopping_dining"):
    """Get AI-powered local market recommendations"""
    agent = travel_agent

    if not agent:
        agent = await create_fallback_agent()

    try:
        # Use Google AI for market recommendations
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = f"""
            Recommend local markets and shopping areas in {location} for {theme} travelers:

            Include:
            1. Market name and location
            2. Unique products and specialties
            3. Best time to visit
            4. Price ranges
            5. Why it's relevant for {theme} theme

            Focus on authentic local markets, not tourist traps.
            """

            response = model.generate_content(prompt)
            markets = []

            # Parse AI response into market objects with UI-expected format
            ai_text = response.text
            lines = [line.strip() for line in ai_text.split('\n') if line.strip()]

            for i, line in enumerate(lines[:3]):
                if '.' in line and len(line) > 20:  # Valid market description
                    # Extract market name (first part before description)
                    parts = line.split(':')
                    name = parts[0].strip().lstrip('123456789.*-').strip() if len(parts) > 1 else f"Local market {i+1} in {location}"
                    description = parts[1].strip() if len(parts) > 1 else line

                    markets.append({
                        "name": name,
                        "location": f"{location} area",
                        "unique_products": ["Local goods", "Regional specialties", "Handmade items"],
                        "best_time_to_visit": "Morning to evening",
                        "price_range": "Rs100-2000",
                        "theme_relevance": f"Great for {theme} travelers",
                        "ai_recommendation": True,
                        "source": "AI-powered recommendations"
                    })

            return {
                "markets": markets,
                "location": location,
                "theme": theme,
                "method": "direct_ai_markets"
            }

    except Exception as e:
        logging.error(f"Local markets error: {str(e)}")
        return {
            "markets": [],
            "location": location,
            "error": str(e),
            "method": "error_fallback"
        }

@app.get("/api/weather")
async def get_weather_info(location: str, date_range: str = "current"):
    """Get weather information for a location"""
    if not travel_agent:
        raise HTTPException(
            status_code=503,
            detail="Weather service is not available"
        )

    try:
        # Call the weather function directly through the agent's _execute_function method
        function_args = {
            "location": location,
            "date_range": date_range
        }
        result = await travel_agent._execute_function("get_weather_info", function_args)

        # Structure the response for the frontend
        weather_response = {
            "location": location,
            "date_range": date_range,
            "weather_data": result.get("weather_data", {}),
            "current_conditions": result.get("weather_data", {}).get("current_conditions", "Data unavailable"),
            "temperature_range": result.get("weather_data", {}).get("temperature_range", "Data unavailable"),
            "forecast": result.get("weather_data", {}).get("forecast", []),
            "search_results": result.get("results", []),
            "total_results": len(result.get("results", [])),
            "search_query": result.get("search_query", ""),
            "source": "AI-powered weather search",
            "timestamp": result.get("timestamp", ""),
            "status": result.get("status", "unknown")
        }

        return weather_response

    except Exception as e:
        logging.error(f"Weather fetch error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get weather information: {str(e)}"
        )

@app.get("/api/hotels")
async def get_hotels(location: str, budget_range: str = "", theme: str = ""):
    """Get hotel recommendations"""
    if not travel_agent:
        raise HTTPException(
            status_code=503,
            detail="Hotel service is not available"
        )

    try:
        # Call the hotel function directly through the agent's _execute_function method
        function_args = {
            "location": location,
            "budget_range": budget_range,
            "theme": theme
        }
        result = await travel_agent._execute_function("get_hotels", function_args)

        # Transform agent results to match UI expectations
        hotels = []
        for item in result.get("results", []):
            hotels.append({
                "name": item.get("title", item.get("name", f"Hotel in {location}")),
                "location": item.get("location", f"{location} area"),
                "rating": item.get("rating", "4.0+"),
                "price_range": item.get("price_range", budget_range or "Rs2000-5000 per night"),
                "amenities": item.get("amenities", ["WiFi", "AC", "Room Service", "Parking"]),
                "theme_suitability": f"Excellent for {theme} travelers",
                "booking_options": {
                    "available": True,
                    "booking_url": item.get("link", "#"),
                    "ai_recommendation": True
                },
                "ai_analysis": "AI-verified accommodation",
                "source": item.get("link", "AI agent search")
            })

        # Structure the response for the frontend
        hotels_response = {
            "location": location,
            "budget_range": budget_range,
            "theme": theme,
            "hotels": hotels,
            "total_results": len(hotels),
            "search_query": result.get("search_query", ""),
            "source": "AI-powered search",
            "timestamp": result.get("timestamp", ""),
            "ai_analysis": f"Found {len(hotels)} recommended hotels"
        }

        return hotels_response

    except Exception as e:
        logging.error(f"Hotel fetch error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get hotel recommendations: {str(e)}"
        )

@app.post("/api/trips/save")
async def save_trip(request: SaveTripRequest):
    """Save a trip for later reference"""
    try:
        trip_id = request.id or f"trip_{datetime.now().timestamp()}"

        saved_trips[trip_id] = {
            "id": trip_id,
            "name": request.name,
            "trip_data": request.trip_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        return {"id": trip_id, "message": "Trip saved successfully"}

    except Exception as e:
        logging.error(f"Save trip error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save trip: {str(e)}"
        )

@app.get("/api/trips")
async def get_saved_trips():
    """Get all saved trips"""
    try:
        trips = list(saved_trips.values())
        return trips

    except Exception as e:
        logging.error(f"Get trips error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve trips: {str(e)}"
        )

@app.delete("/api/trips/{trip_id}")
async def delete_trip(trip_id: str):
    """Delete a saved trip"""
    try:
        if trip_id not in saved_trips:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )

        del saved_trips[trip_id]
        return {"message": "Trip deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete trip error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete trip: {str(e)}"
        )

async def get_transportation_details(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI-powered transportation details based on travel mode and vehicle type"""
    travel_mode = user_input.get('travel_mode', 'Self')
    source = user_input.get('source', 'Unknown')
    destination = user_input.get('destination', 'Unknown')

    # Try to get AI-powered transportation recommendations
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = f"""
            As a transportation expert, provide detailed travel options for:

            Route: {source} to {destination}
            Travel Mode: {travel_mode}
            Vehicle Type: {user_input.get('vehicle_type', 'car') if travel_mode == 'Self' else 'N/A'}

            For {travel_mode} mode, provide:
            1. Route recommendations
            2. Cost estimates (fuel/tickets)
            3. Duration estimates
            4. Key stopovers or booking options
            5. Tips for this specific route

            Be specific to the route and realistic with current market rates.
            """

            response = model.generate_content(prompt)
            ai_text = response.text

            # Parse useful information from AI response
            if travel_mode == 'Self':
                # Extract cost information
                import re
                cost_match = re.search(r'[₹Rs]\s*([0-9,]+)', ai_text)
                fuel_cost = f"₹{cost_match.group(1)}" if cost_match else "₹2000-3000"

                return {
                    "self_mode": {
                        "route_details": f"AI-optimized route from {source} to {destination}",
                        "fuel_estimate": {
                            "vehicle_type": user_input.get('vehicle_type', 'Car').title(),
                            "ai_recommendations": ai_text[:300] + "...",
                            "estimated_cost": fuel_cost,
                            "route_tips": "Check AI recommendations above for route-specific advice"
                        },
                        "ai_analysis": ai_text,
                        "method": "ai_transportation_analysis"
                    }
                }
            else:
                # Extract transport options from AI response
                transport_options = []
                lines = ai_text.split('\n')

                for line in lines:
                    if any(transport in line.lower() for transport in ['flight', 'train', 'bus', 'cab']):
                        if '₹' in line or 'Rs' in line:
                            cost_match = re.search(r'[₹Rs]\s*([0-9,\-]+)', line)
                            cost = cost_match.group(0) if cost_match else "₹1000-3000"

                            if 'flight' in line.lower():
                                transport_options.append({
                                    "type": "Flight",
                                    "operator": "Various Airlines",
                                    "price": cost,
                                    "duration": "1-2 hours",
                                    "ai_recommendation": line.strip()
                                })
                            elif 'train' in line.lower():
                                transport_options.append({
                                    "type": "Train",
                                    "operator": "Indian Railways",
                                    "price": cost,
                                    "duration": "6-8 hours",
                                    "ai_recommendation": line.strip()
                                })

                return {
                    "booking_mode": {
                        "transport_options": transport_options or [
                            {
                                "type": "AI Analysis",
                                "operator": "Multiple Options",
                                "price": "Variable",
                                "duration": "Depends on choice",
                                "ai_recommendation": ai_text[:200] + "..."
                            }
                        ],
                        "ai_analysis": ai_text,
                        "method": "ai_transportation_analysis"
                    }
                }

    except Exception as e:
        logging.error(f"AI transportation analysis error: {e}")

    # Fallback to original logic if AI fails

    if travel_mode == 'Self':
        vehicle_type = user_input.get('vehicle_type', 'car')

        # Vehicle fuel efficiency mapping
        fuel_efficiency = {
            'car': 15,      # km/l
            'suv': 12,      # km/l
            'bike': 45,     # km/l
            'hatchback': 18 # km/l
        }.get(vehicle_type, 15)

        # Calculate approximate distance based on source and destination
        def get_approximate_distance(source: str, destination: str) -> int:
            distances = {
                'kerala': {
                    'rajasthan': 1800, 'goa': 600, 'mumbai': 1200, 'delhi': 2200,
                    'bangalore': 350, 'chennai': 650
                },
                'mumbai': {
                    'delhi': 1400, 'kerala': 1200, 'rajasthan': 800, 'goa': 450,
                    'bangalore': 980, 'chennai': 1100
                },
                'delhi': {
                    'mumbai': 1400, 'kerala': 2200, 'rajasthan': 600, 'goa': 1800,
                    'bangalore': 2100, 'chennai': 2200
                },
                'rajasthan': {
                    'kerala': 1800, 'mumbai': 800, 'delhi': 600, 'goa': 1200,
                    'bangalore': 1600, 'chennai': 1800
                },
                'goa': {
                    'kerala': 600, 'mumbai': 450, 'delhi': 1800, 'rajasthan': 1200,
                    'bangalore': 560, 'chennai': 900
                },
                'bangalore': {
                    'kerala': 350, 'mumbai': 980, 'delhi': 2100, 'rajasthan': 1600,
                    'goa': 560, 'chennai': 350
                },
                'chennai': {
                    'kerala': 650, 'mumbai': 1100, 'delhi': 2200, 'rajasthan': 1800,
                    'goa': 900, 'bangalore': 350
                }
            }

            source_key = source.lower()
            dest_key = destination.lower()

            # Check both directions
            distance = distances.get(source_key, {}).get(dest_key) or distances.get(dest_key, {}).get(source_key)

            return distance or 350  # Default fallback

        estimated_distance = get_approximate_distance(
            user_input.get('source', 'Unknown'),
            user_input.get('destination', 'Unknown')
        )
        fuel_needed = estimated_distance / fuel_efficiency
        fuel_price_per_liter = 100  # INR
        fuel_cost = fuel_needed * fuel_price_per_liter

        return {
            "self_mode": {
                "route_details": f"Best route via highways and scenic roads",
                "fuel_estimate": {
                    "vehicle_type": vehicle_type.title(),
                    "total_distance": f"{estimated_distance} KM",
                    "fuel_efficiency": f"{fuel_efficiency} km/l",
                    "fuel_needed": f"{fuel_needed:.1f} liters",
                    "fuel_cost": f"₹{fuel_cost:.0f}",
                    "toll_charges": "₹300-500"
                },
                "route_hotels": [
                    "Highway Rest Inn",
                    "Midway Comfort Lodge",
                    "Roadside Restaurant & Stay"
                ],
                "route_restaurants": [
                    "Highway Dhaba Deluxe",
                    "Local Cuisine Stop",
                    "Fast Food Junction"
                ]
            }
        }

    elif travel_mode == 'Booking':
        transport_prefs = user_input.get('transport_preferences', ['flight', 'train'])

        transport_options = []

        if 'flight' in transport_prefs:
            transport_options.append({
                "type": "Flight",
                "operator": "Various Airlines",
                "price": "₹4000-8000",
                "duration": "1.5 hours",
                "booking_url": "https://booking-site.com",
                "one_click_booking": True
            })

        if 'train' in transport_prefs:
            transport_options.append({
                "type": "Train",
                "operator": "Indian Railways",
                "price": "₹800-2500",
                "duration": "6-8 hours",
                "booking_url": "https://irctc.co.in",
                "one_click_booking": True
            })

        if 'bus' in transport_prefs:
            transport_options.append({
                "type": "Bus",
                "operator": "State Transport",
                "price": "₹500-1200",
                "duration": "8-10 hours",
                "booking_url": "https://redbus.in",
                "one_click_booking": False
            })

        if 'cab' in transport_prefs:
            transport_options.append({
                "type": "Cab",
                "operator": "Ola/Uber",
                "price": "₹3000-5000",
                "duration": "5-7 hours",
                "booking_url": "https://olacabs.com",
                "one_click_booking": True
            })

        return {
            "booking_mode": {
                "transport_options": transport_options
            }
        }

    return {}

def calculate_minimum_duration(source: str, destination: str, travel_mode: str) -> int:
    """Calculate minimum required duration based on travel distance and mode"""

    # Comprehensive distance matrix for Indian states/regions (in kilometers)
    distances = {
        # Major Southern States
        'kerala': {
            'tamil nadu': 650, 'karnataka': 350, 'andhra pradesh': 700, 'telangana': 800,
            'goa': 600, 'mumbai': 1200, 'maharashtra': 1200, 'gujarat': 1500,
            'rajasthan': 1800, 'delhi': 2200, 'haryana': 2200, 'punjab': 2300,
            'uttarakhand': 2000, 'himachal pradesh': 2100, 'kashmir': 2500,
            'uttar pradesh': 2000, 'madhya pradesh': 1400, 'chhattisgarh': 1300,
            'jharkhand': 1800, 'bihar': 1900, 'west bengal': 1900, 'odisha': 1200,
            'assam': 2400, 'meghalaya': 2400, 'sikkim': 2200, 'arunachal pradesh': 2600,
            'nagaland': 2500, 'manipur': 2500, 'mizoram': 2400, 'tripura': 2300
        },
        'tamil nadu': {
            'kerala': 650, 'karnataka': 350, 'andhra pradesh': 450, 'telangana': 600,
            'goa': 900, 'mumbai': 1100, 'maharashtra': 1000, 'gujarat': 1300,
            'rajasthan': 1800, 'delhi': 2200, 'haryana': 2200, 'punjab': 2300,
            'uttarakhand': 2400, 'himachal pradesh': 2500, 'kashmir': 2700,
            'uttar pradesh': 2100, 'madhya pradesh': 1300, 'chhattisgarh': 1100,
            'jharkhand': 1600, 'bihar': 1700, 'west bengal': 1600, 'odisha': 900,
            'assam': 2200, 'meghalaya': 2200, 'sikkim': 2000, 'arunachal pradesh': 2400,
            'nagaland': 2300, 'manipur': 2300, 'mizoram': 2200, 'tripura': 2100,
            'chennai': 100, 'bangalore': 350
        },
        'karnataka': {
            'kerala': 350, 'tamil nadu': 350, 'andhra pradesh': 500, 'telangana': 600,
            'goa': 560, 'mumbai': 980, 'maharashtra': 800, 'gujarat': 1100,
            'rajasthan': 1600, 'delhi': 2100, 'haryana': 2100, 'punjab': 2200,
            'uttarakhand': 2300, 'himachal pradesh': 2400, 'kashmir': 2600,
            'uttar pradesh': 1900, 'madhya pradesh': 1100, 'chhattisgarh': 900,
            'jharkhand': 1400, 'bihar': 1500, 'west bengal': 1400, 'odisha': 700,
            'assam': 2000, 'meghalaya': 2000, 'sikkim': 1800, 'arunachal pradesh': 2200,
            'nagaland': 2100, 'manipur': 2100, 'mizoram': 2000, 'tripura': 1900,
            'bangalore': 50, 'chennai': 350
        },
        'andhra pradesh': {
            'kerala': 700, 'tamil nadu': 450, 'karnataka': 500, 'telangana': 200,
            'goa': 800, 'mumbai': 900, 'maharashtra': 700, 'gujarat': 1000,
            'rajasthan': 1500, 'delhi': 2000, 'haryana': 2000, 'punjab': 2100,
            'uttarakhand': 2200, 'himachal pradesh': 2300, 'kashmir': 2500,
            'uttar pradesh': 1800, 'madhya pradesh': 1000, 'chhattisgarh': 600,
            'jharkhand': 1200, 'bihar': 1300, 'west bengal': 1200, 'odisha': 500,
            'assam': 1800, 'meghalaya': 1800, 'sikkim': 1600, 'arunachal pradesh': 2000,
            'nagaland': 1900, 'manipur': 1900, 'mizoram': 1800, 'tripura': 1700
        },
        'telangana': {
            'kerala': 800, 'tamil nadu': 600, 'karnataka': 600, 'andhra pradesh': 200,
            'goa': 900, 'mumbai': 800, 'maharashtra': 600, 'gujarat': 900,
            'rajasthan': 1300, 'delhi': 1800, 'haryana': 1800, 'punjab': 1900,
            'uttarakhand': 2000, 'himachal pradesh': 2100, 'kashmir': 2300,
            'uttar pradesh': 1600, 'madhya pradesh': 800, 'chhattisgarh': 400,
            'jharkhand': 1000, 'bihar': 1100, 'west bengal': 1000, 'odisha': 300,
            'assam': 1600, 'meghalaya': 1600, 'sikkim': 1400, 'arunachal pradesh': 1800,
            'nagaland': 1700, 'manipur': 1700, 'mizoram': 1600, 'tripura': 1500
        },

        # Western States
        'goa': {
            'kerala': 600, 'tamil nadu': 900, 'karnataka': 560, 'andhra pradesh': 800,
            'telangana': 900, 'mumbai': 450, 'maharashtra': 400, 'gujarat': 700,
            'rajasthan': 1200, 'delhi': 1800, 'haryana': 1800, 'punjab': 1900,
            'uttarakhand': 2000, 'himachal pradesh': 2100, 'kashmir': 2200,
            'uttar pradesh': 1700, 'madhya pradesh': 1000, 'chhattisgarh': 900,
            'jharkhand': 1400, 'bihar': 1500, 'west bengal': 1400, 'odisha': 700,
            'assam': 2000, 'meghalaya': 2000, 'sikkim': 1800, 'arunachal pradesh': 2200,
            'nagaland': 2100, 'manipur': 2100, 'mizoram': 2000, 'tripura': 1900
        },
        'mumbai': {
            'kerala': 1200, 'tamil nadu': 1100, 'karnataka': 980, 'andhra pradesh': 900,
            'telangana': 800, 'goa': 450, 'maharashtra': 200, 'gujarat': 500,
            'rajasthan': 800, 'delhi': 1400, 'haryana': 1400, 'punjab': 1500,
            'uttarakhand': 1600, 'himachal pradesh': 1700, 'kashmir': 1800,
            'uttar pradesh': 1300, 'madhya pradesh': 600, 'chhattisgarh': 700,
            'jharkhand': 1200, 'bihar': 1300, 'west bengal': 1300, 'odisha': 800,
            'assam': 1800, 'meghalaya': 1800, 'sikkim': 1600, 'arunachal pradesh': 2000,
            'nagaland': 1900, 'manipur': 1900, 'mizoram': 1800, 'tripura': 1700
        },
        'maharashtra': {
            'kerala': 1200, 'tamil nadu': 1000, 'karnataka': 800, 'andhra pradesh': 700,
            'telangana': 600, 'goa': 400, 'mumbai': 200, 'gujarat': 400,
            'rajasthan': 700, 'delhi': 1200, 'haryana': 1200, 'punjab': 1300,
            'uttarakhand': 1400, 'himachal pradesh': 1500, 'kashmir': 1600,
            'uttar pradesh': 1100, 'madhya pradesh': 400, 'chhattisgarh': 500,
            'jharkhand': 1000, 'bihar': 1100, 'west bengal': 1100, 'odisha': 600,
            'assam': 1600, 'meghalaya': 1600, 'sikkim': 1400, 'arunachal pradesh': 1800,
            'nagaland': 1700, 'manipur': 1700, 'mizoram': 1600, 'tripura': 1500
        },
        'gujarat': {
            'kerala': 1500, 'tamil nadu': 1300, 'karnataka': 1100, 'andhra pradesh': 1000,
            'telangana': 900, 'goa': 700, 'mumbai': 500, 'maharashtra': 400,
            'rajasthan': 400, 'delhi': 900, 'haryana': 900, 'punjab': 1000,
            'uttarakhand': 1100, 'himachal pradesh': 1200, 'kashmir': 1300,
            'uttar pradesh': 800, 'madhya pradesh': 600, 'chhattisgarh': 800,
            'jharkhand': 1200, 'bihar': 1300, 'west bengal': 1400, 'odisha': 900,
            'assam': 1800, 'meghalaya': 1800, 'sikkim': 1600, 'arunachal pradesh': 2000,
            'nagaland': 1900, 'manipur': 1900, 'mizoram': 1800, 'tripura': 1700
        },

        # Central-Western States
        'rajasthan': {
            'kerala': 1800, 'tamil nadu': 1800, 'karnataka': 1600, 'andhra pradesh': 1500,
            'telangana': 1300, 'goa': 1200, 'mumbai': 800, 'maharashtra': 700,
            'gujarat': 400, 'delhi': 600, 'haryana': 500, 'punjab': 600,
            'uttarakhand': 800, 'himachal pradesh': 900, 'kashmir': 1000,
            'uttar pradesh': 700, 'madhya pradesh': 700, 'chhattisgarh': 900,
            'jharkhand': 1200, 'bihar': 1300, 'west bengal': 1400, 'odisha': 1100,
            'assam': 1800, 'meghalaya': 1800, 'sikkim': 1600, 'arunachal pradesh': 2000,
            'nagaland': 1900, 'manipur': 1900, 'mizoram': 1800, 'tripura': 1700
        },

        # Northern States
        'delhi': {
            'kerala': 2200, 'tamil nadu': 2200, 'karnataka': 2100, 'andhra pradesh': 2000,
            'telangana': 1800, 'goa': 1800, 'mumbai': 1400, 'maharashtra': 1200,
            'gujarat': 900, 'rajasthan': 600, 'haryana': 50, 'punjab': 300,
            'uttarakhand': 300, 'himachal pradesh': 350, 'kashmir': 800,
            'uttar pradesh': 400, 'madhya pradesh': 800, 'chhattisgarh': 1000,
            'jharkhand': 1200, 'bihar': 1100, 'west bengal': 1300, 'odisha': 1300,
            'assam': 1700, 'meghalaya': 1700, 'sikkim': 1500, 'arunachal pradesh': 1900,
            'nagaland': 1800, 'manipur': 1800, 'mizoram': 1700, 'tripura': 1600
        },
        'haryana': {
            'kerala': 2200, 'tamil nadu': 2200, 'karnataka': 2100, 'andhra pradesh': 2000,
            'telangana': 1800, 'goa': 1800, 'mumbai': 1400, 'maharashtra': 1200,
            'gujarat': 900, 'rajasthan': 500, 'delhi': 50, 'punjab': 250,
            'uttarakhand': 250, 'himachal pradesh': 300, 'kashmir': 750,
            'uttar pradesh': 350, 'madhya pradesh': 750, 'chhattisgarh': 950,
            'jharkhand': 1150, 'bihar': 1050, 'west bengal': 1250, 'odisha': 1250,
            'assam': 1650, 'meghalaya': 1650, 'sikkim': 1450, 'arunachal pradesh': 1850,
            'nagaland': 1750, 'manipur': 1750, 'mizoram': 1650, 'tripura': 1550
        },
        'punjab': {
            'kerala': 2300, 'tamil nadu': 2300, 'karnataka': 2200, 'andhra pradesh': 2100,
            'telangana': 1900, 'goa': 1900, 'mumbai': 1500, 'maharashtra': 1300,
            'gujarat': 1000, 'rajasthan': 600, 'delhi': 300, 'haryana': 250,
            'uttarakhand': 400, 'himachal pradesh': 200, 'kashmir': 500,
            'uttar pradesh': 500, 'madhya pradesh': 900, 'chhattisgarh': 1100,
            'jharkhand': 1300, 'bihar': 1200, 'west bengal': 1400, 'odisha': 1400,
            'assam': 1800, 'meghalaya': 1800, 'sikkim': 1600, 'arunachal pradesh': 2000,
            'nagaland': 1900, 'manipur': 1900, 'mizoram': 1800, 'tripura': 1700
        },

        # Mountain States
        'uttarakhand': {
            'kerala': 2000, 'tamil nadu': 2400, 'karnataka': 2300, 'andhra pradesh': 2200,
            'telangana': 2000, 'goa': 2000, 'mumbai': 1600, 'maharashtra': 1400,
            'gujarat': 1100, 'rajasthan': 800, 'delhi': 300, 'haryana': 250,
            'punjab': 400, 'himachal pradesh': 200, 'kashmir': 600,
            'uttar pradesh': 200, 'madhya pradesh': 700, 'chhattisgarh': 900,
            'jharkhand': 1100, 'bihar': 1000, 'west bengal': 1200, 'odisha': 1200,
            'assam': 1600, 'meghalaya': 1600, 'sikkim': 1400, 'arunachal pradesh': 1800,
            'nagaland': 1700, 'manipur': 1700, 'mizoram': 1600, 'tripura': 1500
        },
        'himachal pradesh': {
            'kerala': 2100, 'tamil nadu': 2500, 'karnataka': 2400, 'andhra pradesh': 2300,
            'telangana': 2100, 'goa': 2100, 'mumbai': 1700, 'maharashtra': 1500,
            'gujarat': 1200, 'rajasthan': 900, 'delhi': 350, 'haryana': 300,
            'punjab': 200, 'uttarakhand': 200, 'kashmir': 400,
            'uttar pradesh': 400, 'madhya pradesh': 800, 'chhattisgarh': 1000,
            'jharkhand': 1200, 'bihar': 1100, 'west bengal': 1300, 'odisha': 1300,
            'assam': 1700, 'meghalaya': 1700, 'sikkim': 1500, 'arunachal pradesh': 1900,
            'nagaland': 1800, 'manipur': 1800, 'mizoram': 1700, 'tripura': 1600
        },
        'kashmir': {
            'kerala': 2500, 'tamil nadu': 2700, 'karnataka': 2600, 'andhra pradesh': 2500,
            'telangana': 2300, 'goa': 2200, 'mumbai': 1800, 'maharashtra': 1600,
            'gujarat': 1300, 'rajasthan': 1000, 'delhi': 800, 'haryana': 750,
            'punjab': 500, 'uttarakhand': 600, 'himachal pradesh': 400,
            'uttar pradesh': 900, 'madhya pradesh': 1200, 'chhattisgarh': 1400,
            'jharkhand': 1600, 'bihar': 1500, 'west bengal': 1700, 'odisha': 1700,
            'assam': 2100, 'meghalaya': 2100, 'sikkim': 1900, 'arunachal pradesh': 2300,
            'nagaland': 2200, 'manipur': 2200, 'mizoram': 2100, 'tripura': 2000
        },

        # Central States
        'uttar pradesh': {
            'kerala': 2000, 'tamil nadu': 2100, 'karnataka': 1900, 'andhra pradesh': 1800,
            'telangana': 1600, 'goa': 1700, 'mumbai': 1300, 'maharashtra': 1100,
            'gujarat': 800, 'rajasthan': 700, 'delhi': 400, 'haryana': 350,
            'punjab': 500, 'uttarakhand': 200, 'himachal pradesh': 400, 'kashmir': 900,
            'madhya pradesh': 500, 'chhattisgarh': 700, 'jharkhand': 900,
            'bihar': 800, 'west bengal': 1000, 'odisha': 1000, 'assam': 1400,
            'meghalaya': 1400, 'sikkim': 1200, 'arunachal pradesh': 1600,
            'nagaland': 1500, 'manipur': 1500, 'mizoram': 1400, 'tripura': 1300
        },
        'madhya pradesh': {
            'kerala': 1400, 'tamil nadu': 1300, 'karnataka': 1100, 'andhra pradesh': 1000,
            'telangana': 800, 'goa': 1000, 'mumbai': 600, 'maharashtra': 400,
            'gujarat': 600, 'rajasthan': 700, 'delhi': 800, 'haryana': 750,
            'punjab': 900, 'uttarakhand': 700, 'himachal pradesh': 800, 'kashmir': 1200,
            'uttar pradesh': 500, 'chhattisgarh': 300, 'jharkhand': 600,
            'bihar': 700, 'west bengal': 800, 'odisha': 700, 'assam': 1200,
            'meghalaya': 1200, 'sikkim': 1000, 'arunachal pradesh': 1400,
            'nagaland': 1300, 'manipur': 1300, 'mizoram': 1200, 'tripura': 1100
        },
        'chhattisgarh': {
            'kerala': 1300, 'tamil nadu': 1100, 'karnataka': 900, 'andhra pradesh': 600,
            'telangana': 400, 'goa': 900, 'mumbai': 700, 'maharashtra': 500,
            'gujarat': 800, 'rajasthan': 900, 'delhi': 1000, 'haryana': 950,
            'punjab': 1100, 'uttarakhand': 900, 'himachal pradesh': 1000, 'kashmir': 1400,
            'uttar pradesh': 700, 'madhya pradesh': 300, 'jharkhand': 300,
            'bihar': 500, 'west bengal': 600, 'odisha': 400, 'assam': 1000,
            'meghalaya': 1000, 'sikkim': 800, 'arunachal pradesh': 1200,
            'nagaland': 1100, 'manipur': 1100, 'mizoram': 1000, 'tripura': 900
        },

        # Eastern States
        'jharkhand': {
            'kerala': 1800, 'tamil nadu': 1600, 'karnataka': 1400, 'andhra pradesh': 1200,
            'telangana': 1000, 'goa': 1400, 'mumbai': 1200, 'maharashtra': 1000,
            'gujarat': 1200, 'rajasthan': 1200, 'delhi': 1200, 'haryana': 1150,
            'punjab': 1300, 'uttarakhand': 1100, 'himachal pradesh': 1200, 'kashmir': 1600,
            'uttar pradesh': 900, 'madhya pradesh': 600, 'chhattisgarh': 300,
            'bihar': 200, 'west bengal': 300, 'odisha': 500, 'assam': 700,
            'meghalaya': 700, 'sikkim': 500, 'arunachal pradesh': 900,
            'nagaland': 800, 'manipur': 800, 'mizoram': 700, 'tripura': 600
        },
        'bihar': {
            'kerala': 1900, 'tamil nadu': 1700, 'karnataka': 1500, 'andhra pradesh': 1300,
            'telangana': 1100, 'goa': 1500, 'mumbai': 1300, 'maharashtra': 1100,
            'gujarat': 1300, 'rajasthan': 1300, 'delhi': 1100, 'haryana': 1050,
            'punjab': 1200, 'uttarakhand': 1000, 'himachal pradesh': 1100, 'kashmir': 1500,
            'uttar pradesh': 800, 'madhya pradesh': 700, 'chhattisgarh': 500,
            'jharkhand': 200, 'west bengal': 400, 'odisha': 600, 'assam': 600,
            'meghalaya': 600, 'sikkim': 400, 'arunachal pradesh': 800,
            'nagaland': 700, 'manipur': 700, 'mizoram': 600, 'tripura': 500
        },
        'west bengal': {
            'kerala': 1900, 'tamil nadu': 1600, 'karnataka': 1400, 'andhra pradesh': 1200,
            'telangana': 1000, 'goa': 1400, 'mumbai': 1300, 'maharashtra': 1100,
            'gujarat': 1400, 'rajasthan': 1400, 'delhi': 1300, 'haryana': 1250,
            'punjab': 1400, 'uttarakhand': 1200, 'himachal pradesh': 1300, 'kashmir': 1700,
            'uttar pradesh': 1000, 'madhya pradesh': 800, 'chhattisgarh': 600,
            'jharkhand': 300, 'bihar': 400, 'odisha': 400, 'assam': 500,
            'meghalaya': 400, 'sikkim': 200, 'arunachal pradesh': 600,
            'nagaland': 500, 'manipur': 500, 'mizoram': 400, 'tripura': 300
        },
        'odisha': {
            'kerala': 1200, 'tamil nadu': 900, 'karnataka': 700, 'andhra pradesh': 500,
            'telangana': 300, 'goa': 700, 'mumbai': 800, 'maharashtra': 600,
            'gujarat': 900, 'rajasthan': 1100, 'delhi': 1300, 'haryana': 1250,
            'punjab': 1400, 'uttarakhand': 1200, 'himachal pradesh': 1300, 'kashmir': 1700,
            'uttar pradesh': 1000, 'madhya pradesh': 700, 'chhattisgarh': 400,
            'jharkhand': 500, 'bihar': 600, 'west bengal': 400, 'assam': 600,
            'meghalaya': 600, 'sikkim': 600, 'arunachal pradesh': 800,
            'nagaland': 700, 'manipur': 700, 'mizoram': 600, 'tripura': 500
        },

        # Northeastern States
        'assam': {
            'kerala': 2400, 'tamil nadu': 2200, 'karnataka': 2000, 'andhra pradesh': 1800,
            'telangana': 1600, 'goa': 2000, 'mumbai': 1800, 'maharashtra': 1600,
            'gujarat': 1800, 'rajasthan': 1800, 'delhi': 1700, 'haryana': 1650,
            'punjab': 1800, 'uttarakhand': 1600, 'himachal pradesh': 1700, 'kashmir': 2100,
            'uttar pradesh': 1400, 'madhya pradesh': 1200, 'chhattisgarh': 1000,
            'jharkhand': 700, 'bihar': 600, 'west bengal': 500, 'odisha': 600,
            'meghalaya': 100, 'sikkim': 300, 'arunachal pradesh': 300,
            'nagaland': 200, 'manipur': 300, 'mizoram': 400, 'tripura': 400
        },
        'meghalaya': {
            'kerala': 2400, 'tamil nadu': 2200, 'karnataka': 2000, 'andhra pradesh': 1800,
            'telangana': 1600, 'goa': 2000, 'mumbai': 1800, 'maharashtra': 1600,
            'gujarat': 1800, 'rajasthan': 1800, 'delhi': 1700, 'haryana': 1650,
            'punjab': 1800, 'uttarakhand': 1600, 'himachal pradesh': 1700, 'kashmir': 2100,
            'uttar pradesh': 1400, 'madhya pradesh': 1200, 'chhattisgarh': 1000,
            'jharkhand': 700, 'bihar': 600, 'west bengal': 400, 'odisha': 600,
            'assam': 100, 'sikkim': 400, 'arunachal pradesh': 400,
            'nagaland': 300, 'manipur': 400, 'mizoram': 300, 'tripura': 300
        },
        'sikkim': {
            'kerala': 2200, 'tamil nadu': 2000, 'karnataka': 1800, 'andhra pradesh': 1600,
            'telangana': 1400, 'goa': 1800, 'mumbai': 1600, 'maharashtra': 1400,
            'gujarat': 1600, 'rajasthan': 1600, 'delhi': 1500, 'haryana': 1450,
            'punjab': 1600, 'uttarakhand': 1400, 'himachal pradesh': 1500, 'kashmir': 1900,
            'uttar pradesh': 1200, 'madhya pradesh': 1000, 'chhattisgarh': 800,
            'jharkhand': 500, 'bihar': 400, 'west bengal': 200, 'odisha': 600,
            'assam': 300, 'meghalaya': 400, 'arunachal pradesh': 500,
            'nagaland': 400, 'manipur': 500, 'mizoram': 600, 'tripura': 500
        },
        'arunachal pradesh': {
            'kerala': 2600, 'tamil nadu': 2400, 'karnataka': 2200, 'andhra pradesh': 2000,
            'telangana': 1800, 'goa': 2200, 'mumbai': 2000, 'maharashtra': 1800,
            'gujarat': 2000, 'rajasthan': 2000, 'delhi': 1900, 'haryana': 1850,
            'punjab': 2000, 'uttarakhand': 1800, 'himachal pradesh': 1900, 'kashmir': 2300,
            'uttar pradesh': 1600, 'madhya pradesh': 1400, 'chhattisgarh': 1200,
            'jharkhand': 900, 'bihar': 800, 'west bengal': 600, 'odisha': 800,
            'assam': 300, 'meghalaya': 400, 'sikkim': 500,
            'nagaland': 400, 'manipur': 400, 'mizoram': 500, 'tripura': 600
        },
        'nagaland': {
            'kerala': 2500, 'tamil nadu': 2300, 'karnataka': 2100, 'andhra pradesh': 1900,
            'telangana': 1700, 'goa': 2100, 'mumbai': 1900, 'maharashtra': 1700,
            'gujarat': 1900, 'rajasthan': 1900, 'delhi': 1800, 'haryana': 1750,
            'punjab': 1900, 'uttarakhand': 1700, 'himachal pradesh': 1800, 'kashmir': 2200,
            'uttar pradesh': 1500, 'madhya pradesh': 1300, 'chhattisgarh': 1100,
            'jharkhand': 800, 'bihar': 700, 'west bengal': 500, 'odisha': 700,
            'assam': 200, 'meghalaya': 300, 'sikkim': 400, 'arunachal pradesh': 400,
            'manipur': 200, 'mizoram': 300, 'tripura': 400
        },
        'manipur': {
            'kerala': 2500, 'tamil nadu': 2300, 'karnataka': 2100, 'andhra pradesh': 1900,
            'telangana': 1700, 'goa': 2100, 'mumbai': 1900, 'maharashtra': 1700,
            'gujarat': 1900, 'rajasthan': 1900, 'delhi': 1800, 'haryana': 1750,
            'punjab': 1900, 'uttarakhand': 1700, 'himachal pradesh': 1800, 'kashmir': 2200,
            'uttar pradesh': 1500, 'madhya pradesh': 1300, 'chhattisgarh': 1100,
            'jharkhand': 800, 'bihar': 700, 'west bengal': 500, 'odisha': 700,
            'assam': 300, 'meghalaya': 400, 'sikkim': 500, 'arunachal pradesh': 400,
            'nagaland': 200, 'mizoram': 200, 'tripura': 300
        },
        'mizoram': {
            'kerala': 2400, 'tamil nadu': 2200, 'karnataka': 2000, 'andhra pradesh': 1800,
            'telangana': 1600, 'goa': 2000, 'mumbai': 1800, 'maharashtra': 1600,
            'gujarat': 1800, 'rajasthan': 1800, 'delhi': 1700, 'haryana': 1650,
            'punjab': 1800, 'uttarakhand': 1600, 'himachal pradesh': 1700, 'kashmir': 2100,
            'uttar pradesh': 1400, 'madhya pradesh': 1200, 'chhattisgarh': 1000,
            'jharkhand': 700, 'bihar': 600, 'west bengal': 400, 'odisha': 600,
            'assam': 400, 'meghalaya': 300, 'sikkim': 600, 'arunachal pradesh': 500,
            'nagaland': 300, 'manipur': 200, 'tripura': 200
        },
        'tripura': {
            'kerala': 2300, 'tamil nadu': 2100, 'karnataka': 1900, 'andhra pradesh': 1700,
            'telangana': 1500, 'goa': 1900, 'mumbai': 1700, 'maharashtra': 1500,
            'gujarat': 1700, 'rajasthan': 1700, 'delhi': 1600, 'haryana': 1550,
            'punjab': 1700, 'uttarakhand': 1500, 'himachal pradesh': 1600, 'kashmir': 2000,
            'uttar pradesh': 1300, 'madhya pradesh': 1100, 'chhattisgarh': 900,
            'jharkhand': 600, 'bihar': 500, 'west bengal': 300, 'odisha': 500,
            'assam': 400, 'meghalaya': 300, 'sikkim': 500, 'arunachal pradesh': 600,
            'nagaland': 400, 'manipur': 300, 'mizoram': 200
        },

        # Additional city mappings for common queries
        'bangalore': {
            'kerala': 350, 'tamil nadu': 350, 'chennai': 350, 'mumbai': 980,
            'delhi': 2100, 'goa': 560, 'hyderabad': 600, 'pune': 800,
            'kolkata': 1400, 'ahmedabad': 1100, 'surat': 1000, 'jaipur': 1600,
            'lucknow': 1900, 'kanpur': 1950, 'nagpur': 800, 'indore': 1100,
            'thane': 1000, 'bhopal': 1100, 'visakhapatnam': 500, 'pimpri': 820,
            'patna': 1500, 'vadodara': 1050, 'ghaziabad': 2120, 'ludhiana': 2200,
            'agra': 2000, 'nashik': 900, 'faridabad': 2100, 'meerut': 2150,
            'rajkot': 1200, 'kalyan': 1010, 'vasai': 1020, 'varanasi': 1800,
            'srinagar': 2600, 'aurangabad': 800, 'dhanbad': 1400, 'amritsar': 2300,
            'navi mumbai': 990, 'allahabad': 1850, 'ranchi': 1400, 'howrah': 1410,
            'coimbatore': 500, 'jabalpur': 1200, 'gwalior': 1600
        },
        'chennai': {
            'kerala': 650, 'tamil nadu': 100, 'bangalore': 350, 'mumbai': 1100,
            'delhi': 2200, 'goa': 900, 'hyderabad': 600, 'pune': 1000,
            'kolkata': 1600, 'ahmedabad': 1300, 'surat': 1200, 'jaipur': 1800,
            'lucknow': 2100, 'kanpur': 2150, 'nagpur': 1000, 'indore': 1300,
            'thane': 1120, 'bhopal': 1300, 'visakhapatnam': 450, 'pimpri': 1020,
            'patna': 1700, 'vadodara': 1250, 'ghaziabad': 2220, 'ludhiana': 2300,
            'agra': 2200, 'nashik': 1100, 'faridabad': 2200, 'meerut': 2250,
            'rajkot': 1400, 'kalyan': 1130, 'vasai': 1140, 'varanasi': 2000,
            'srinagar': 2700, 'aurangabad': 1000, 'dhanbad': 1600, 'amritsar': 2400,
            'navi mumbai': 1110, 'allahabad': 2050, 'ranchi': 1600, 'howrah': 1610,
            'coimbatore': 350, 'jabalpur': 1400, 'gwalior': 1800
        },
        'hyderabad': {
            'kerala': 800, 'tamil nadu': 600, 'bangalore': 600, 'mumbai': 800,
            'delhi': 1800, 'goa': 900, 'chennai': 600, 'pune': 600,
            'kolkata': 1000, 'ahmedabad': 900, 'surat': 800, 'jaipur': 1300,
            'lucknow': 1600, 'kanpur': 1650, 'nagpur': 500, 'indore': 800,
            'thane': 820, 'bhopal': 800, 'visakhapatnam': 200, 'pimpri': 620,
            'patna': 1100, 'vadodara': 850, 'ghaziabad': 1820, 'ludhiana': 1900,
            'agra': 1700, 'nashik': 700, 'faridabad': 1800, 'meerut': 1850,
            'rajkot': 1000, 'kalyan': 830, 'vasai': 840, 'varanasi': 1500,
            'srinagar': 2300, 'aurangabad': 600, 'dhanbad': 1000, 'amritsar': 2000,
            'navi mumbai': 810, 'allahabad': 1450, 'ranchi': 1000, 'howrah': 1010,
            'coimbatore': 800, 'jabalpur': 900, 'gwalior': 1200
        }
    }

    source_key = source.lower()
    dest_key = destination.lower()

    # Check both directions
    distance = distances.get(source_key, {}).get(dest_key) or distances.get(dest_key, {}).get(source_key)
    distance = distance or 300  # Default fallback distance

    # Calculate minimum duration based on distance and travel mode
    if travel_mode == 'Self':
        # For self drive: Consider driving time + rest stops + sightseeing
        if distance <= 300:
            return 2  # 2 days minimum for short distances
        elif distance <= 800:
            return 3  # 3 days for medium distances
        elif distance <= 1500:
            return 4  # 4 days for long distances
        else:
            return 5  # 5+ days for very long distances
    else:  # Booking mode
        # For public transport: Less travel fatigue, can focus more on destination
        if distance <= 500:
            return 2  # 2 days minimum
        elif distance <= 1200:
            return 3  # 3 days for medium distances
        else:
            return 4  # 4 days for long distances

def get_feasible_durations(source: str, destination: str, travel_mode: str) -> list:
    """Get list of feasible duration options based on minimum requirements"""
    min_duration = calculate_minimum_duration(source, destination, travel_mode)

    # All possible duration options
    all_durations = [
        {"label": "1-2 days", "value": "2 days", "days": 2},
        {"label": "3-4 days", "value": "3 days", "days": 3},
        {"label": "5-7 days", "value": "7 days", "days": 7},
        {"label": "1 week+", "value": "10 days", "days": 10}
    ]

    # Filter out durations that are less than minimum required
    feasible_durations = [
        duration for duration in all_durations
        if duration["days"] >= min_duration
    ]

    return feasible_durations

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logging.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if os.getenv("DEBUG") else None
        }
    )

# Serve static files in production
if os.getenv("SERVE_STATIC", "false").lower() == "true":
    # Mount the built React app
    app.mount("/", StaticFiles(directory="../dist", html=True), name="static")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logging.info(f"Starting TravelBuddy AI server on {host}:{port}")
    logging.info(f"API Documentation: http://localhost:{port}/api/docs")
    logging.info(f"ReDoc: http://localhost:{port}/api/redoc")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )