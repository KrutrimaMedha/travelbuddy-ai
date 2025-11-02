@startuml
start

:User Opens App;
:View Homepage;
:Fill Trip Planning Form;

' Source/Destination Input & Validation
if (Enter Source/Destination?) then (Yes)
  :Auto-validate Duration Options;
  :AI checks distance matrix;
  :Filter feasible durations;
endif

' Travel Mode Selection
if (Select Travel Mode?) then (Self Mode)
  :Select Vehicle Type;
else (Booking Mode)
  :Select Transport Options;
endif

' Theme Selection
if (Select Theme?) then (Yes)
  :Adventure / Cultural / Devotional / Nightlife / Relaxation;
endif

' Budget Entry and Validation
:Enter Budget;
if (Budget Sufficient?) then (Yes)
  :Show Success Message;
else (No)
  :Show Minimum Required + Tips;
endif

:Submit Form;
:Loading - AI Planning in Progress;

' AI Itinerary Generation Process
partition "AI ITINERARY GENERATION" {
  :Step 1 - Validate Budget & Duration;
  :Calculate minimum requirements;

  :Step 2 - Get Weather Info;
  -> get_weather_info();

  :Step 3 - Find Hotels;
  -> get_hotels(location, theme, budget);

  :Step 4 - Find Restaurants;
  -> get_restaurants(location, theme);

  :Step 5 - Find Activities;
  -> get_activities(location, theme, weather);

  :Step 6 - Find Local Markets;
  -> get_local_markets(location);

  :Step 7 - Get Route Info;
  -> get_route_info(source, dest, mode);

  :Step 8 - Synthesize AI Response;
  :Generate Day-by-Day Itinerary;
}

' Display Results
:Display Comprehensive Itinerary;
:Trip Overview;
:Day-wise Schedule;
:Hotel Recommendations;
:Restaurant Suggestions;
:Transportation Details;
:Weather Info;
:Budget Breakdown;

' Booking Step
:User Clicks "Book on EaseMyTrip";
:Mock Booking API Call;
:EaseMyTrip-style Confirmation Modal;

stop
@enduml
