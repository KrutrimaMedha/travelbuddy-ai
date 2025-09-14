import os
import aiohttp
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Note: Google ADK imports removed for compatibility


load_dotenv()

class TravelPlanningTool:
    """ Travel Planning tools using SERP API as ADK Function tool"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SERP_API_KEY")
        if not self.api_key:
            raise ValueError("SERP_API_KEY environment variable is required")
        self.base_url = "https://serpapi.com/search"

    
    async def google_search(self, query: str, num_results: int = 10, 
                        country: str = "in", language: str = "en") -> Dict[str, Any]:

        """
        Perform comprehensive Google search
        
        Args:
            query: Search query string
            num_results: Number of results to return (1-100)
            country: Country code for search localization
            language: Language code for search results
            
        Returns:
            Dictionary containing search results, featured snippets, and related questions

        """

        params = {
            'engine': 'google',
            'q': query,
            'num': min(num_results, 100),
            'gl': country,
            'hl': language,
            'api_key': self.api_key
        }
        

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            # Extract organic results
            results = []
            if 'organic_results' in data:
                for result in data['organic_results'][:num_results]:
                    results.append({
                        'title': result.get('title', 'N/A'),
                        'link': result.get('link', 'N/A'),
                        'snippet': result.get('snippet', 'N/A'),
                        'position': result.get('position', 0),
                        'source': result.get('displayed_link', 'N/A')
                    })
            
            # Extract featured snippet
            featured_snippet = None
            if 'answer_box' in data:
                featured_snippet = {
                    'type': data['answer_box'].get('type', 'answer'),
                    'title': data['answer_box'].get('title', 'N/A'),
                    'snippet': data['answer_box'].get('snippet', 'N/A'),
                    'link': data['answer_box'].get('link', 'N/A')
                }
            
            # Extract knowledge graph
            knowledge_graph = None
            if 'knowledge_graph' in data:
                kg = data['knowledge_graph']
                knowledge_graph = {
                    'title': kg.get('title', 'N/A'),
                    'type': kg.get('type', 'N/A'),
                    'description': kg.get('description', 'N/A'),
                    'source': kg.get('source', {}).get('name', 'N/A')
                }
            
            # Extract related questions
            related_questions = []
            if 'related_questions' in data:
                for question in data['related_questions'][:5]:
                    related_questions.append({
                        'question': question.get('question', 'N/A'),
                        'snippet': question.get('snippet', 'N/A'),
                        'title': question.get('title', 'N/A'),
                        'link': question.get('link', 'N/A')
                    })
            
            return {
                'status': 'success',
                'query': query,
                'total_results': len(results),
                'organic_results': results,
                'featured_snippet': featured_snippet,
                'knowledge_graph': knowledge_graph,
                'related_questions': related_questions,
                'search_metadata': {
                    'search_time': data.get('search_metadata', {}).get('total_time_taken', 'N/A'),
                    'country': country,
                    'language': language
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Google search failed: {str(e)}',
                'query': query
            }

    async def get_weather_info(self, location: str, date_range: str = "current") -> Dict[str, Any]:
        """
        Get weather information for a location
        
        Args:
            location: Location name
            date_range: Date range (current, weekly, monthly)
            
        Returns:
            Dictionary containing weather information
        """
        query = f"{location} weather {date_range} forecast temperature climate"
        return await self.google_search(query=query, num_results=5)

    async def get_hotels(self, location: str, budget_range: str = "", theme: str = "") -> Dict[str, Any]:
        """
        Get hotel recommendations for a location
        
        Args:
            location: Destination location
            budget_range: Budget category (budget, mid-range, luxury)
            theme: Travel theme for hotel selection
            
        Returns:
            Dictionary containing hotel information
        """
        query = f"best hotels {location} {budget_range} {theme} accommodation booking reviews"
        return await self.google_search(query=query, num_results=8)

    async def get_restaurants(self, location: str, cuisine_type: str = "", theme: str = "") -> Dict[str, Any]:
        """
        Get restaurant recommendations for a location
        
        Args:
            location: Destination location
            cuisine_type: Type of cuisine preferred
            theme: Travel theme for restaurant selection
            
        Returns:
            Dictionary containing restaurant information
        """
        query = f"best restaurants {location} {cuisine_type} {theme} food dining local cuisine"
        return await self.google_search(query=query, num_results=8)

    async def get_events_activities(self, location: str, theme: str = "", date_range: str = "") -> Dict[str, Any]:
        """
        Get events and activities for a location
        
        Args:
            location: Destination location
            theme: Travel theme (adventure, cultural, nightlife, etc.)
            date_range: When visiting
            
        Returns:
            Dictionary containing events and activities information
        """
        query = f"{location} {theme} activities events attractions things to do {date_range}"
        return await self.google_search(query=query, num_results=8)

    async def get_local_markets(self, location: str, theme: str = "") -> Dict[str, Any]:
        """
        Get local markets and shopping information
        
        Args:
            location: Destination location
            theme: Travel theme for market selection
            
        Returns:
            Dictionary containing market information
        """
        query = f"{location} local markets shopping {theme} unique products souvenirs"
        return await self.google_search(query=query, num_results=6)

# Create travel planning instance
travel_planning = TravelPlanningTool()

# Create a wrapper function without default parameters for Google ADK compatibility
async def google_search_wrapper(query: str) -> Dict[str, Any]:
    """
    Wrapper function for google_search without default parameters
    
    Args:
        query: Search query string
        
    Returns:
        Dictionary containing search results
    """
    return await travel_planning.google_search(query=query, num_results=10, country="in", language="en")

# Function tools would be created here if Google ADK was available
# For now, we'll use the direct tool instance

__all__ = [
    'TravelPlanningTool',
    'travel_planning',
    'google_search_wrapper'
]


 