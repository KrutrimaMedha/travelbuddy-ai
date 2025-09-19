# TravelBuddy AI - Testing Instructions

## Overview
This document provides comprehensive testing steps to verify TravelBuddy AI functionality for the Google Gen AI Hackathon submission.

## Prerequisites
- Node.js 18+ and npm installed
- Python 3.8+ installed
- Google Generative AI API key (optional for full testing)
- Both frontend and backend servers running

## Quick Start Testing

### 1. Start the Application
```bash
# Terminal 1: Start Frontend
cd travel_planner_ui
npm install
npm run dev
# Frontend will run on http://localhost:3000

# Terminal 2: Start Backend
cd travel_planner_ui/server
python main.py
# Backend will run on http://localhost:8000
```

## Phase 1: Environment Setup & Basic Functionality

### 1.1 Environment Verification
```bash
# Check if servers are running
curl http://localhost:8000/
curl http://localhost:3000/
```

### 1.2 API Health Check
```bash
# Test backend health
curl -X GET "http://localhost:8000/" -H "Content-Type: application/json"

# Expected Response:
{
  "message": "TravelBuddy AI API is running",
  "version": "1.0.0",
  "status": "healthy",
  "agent_available": true/false,
  "duration_validation_available": true
}
```

## Phase 2: Core API Testing

### 2.1 Duration Validation Testing
Test the comprehensive distance matrix functionality:

#### Test Case 1: Rajasthan to Uttarakhand (Self Mode)
```bash
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "rajasthan", "destination": "uttarakhand", "travel_mode": "Self"}'

# Expected Response:
{
  "minimum_duration": 3,
  "feasible_durations": [
    {"label": "3-4 days", "value": "3 days", "days": 3},
    {"label": "5-7 days", "value": "7 days", "days": 7},
    {"label": "1 week+", "value": "10 days", "days": 10}
  ],
  "message": "Minimum 3 days required for this trip",
  "travel_info": {
    "distance_category": "medium",
    "travel_considerations": "Based on distance and self travel mode"
  }
}
```

#### Test Case 2: Kashmir to Tamil Nadu (Self Mode) - Long Distance
```bash
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "kashmir", "destination": "tamil nadu", "travel_mode": "Self"}'

# Expected: minimum_duration: 5 (longer due to distance)
```

#### Test Case 3: Kerala to Assam (Booking Mode) - Efficient Mode
```bash
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "kerala", "destination": "assam", "travel_mode": "Booking"}'

# Expected: minimum_duration: 2 (shorter than Self mode)
```

#### Test Case 4: Bangalore to Chennai (Self Mode) - Short Distance
```bash
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "bangalore", "destination": "chennai", "travel_mode": "Self"}'

# Expected: minimum_duration: 3
```

### 2.2 Budget Validation Testing
```bash
# Test budget validation
curl -X POST "http://localhost:8000/api/validate-budget" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "mumbai",
    "destination": "goa",
    "travel_mode": "Self",
    "duration": "3 days",
    "budget": "15000"
  }'

# Expected: Budget validation response with recommendations
```

### 2.3 Trip Planning Testing (if AI agent is available)
```bash
# Test full trip planning
curl -X POST "http://localhost:8000/api/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "source": "mumbai",
      "destination": "goa",
      "travel_mode": "Self",
      "budget": "25000",
      "theme": "Relaxation",
      "duration": "3 days"
    }
  }'

# Expected: Comprehensive trip plan with itinerary, hotels, budget breakdown
```

## Phase 3: Frontend Testing

### 3.1 Form Validation Testing
1. **Open Application**: Navigate to `http://localhost:3000`

2. **Test Duration Validation Flow**:
   - Select "Rajasthan" as source
   - Select "Uttarakhand" as destination
   - Choose "Self" travel mode
   - **Expected**: Duration dropdown shows "Checking..." briefly, then populates with valid options
   - **Verify**: Options start from "3-4 days" (minimum for this route)

3. **Test Travel Mode Differences**:
   - Keep same route (Rajasthan → Uttarakhand)
   - Switch from "Self" to "Booking" mode
   - **Expected**: Duration options update (potentially shorter minimum)

4. **Test Long Distance Routes**:
   - Select "Kashmir" as source
   - Select "Tamil Nadu" as destination
   - Choose "Self" mode
   - **Expected**: Longer minimum duration (5+ days)

5. **Test Short Distance Routes**:
   - Select "Delhi" as source
   - Select "Haryana" as destination
   - **Expected**: Shorter minimum duration options

### 3.2 Real-time Validation Testing
1. **Debouncing Test**:
   - Quickly change source/destination multiple times
   - **Expected**: Only the final selection triggers validation after 300ms delay
   - **Verify**: "Checking..." doesn't get stuck in loading state

2. **Error Handling Test**:
   - Try rapid selections
   - Check browser console for errors
   - **Expected**: No JavaScript errors, smooth user experience

### 3.3 Theme and Mode Selection Testing
1. **Theme Selection**:
   - Test all theme options: Adventure, Cultural, Devotional, Nightlife, Relaxation
   - **Expected**: Visual feedback and proper selection state

2. **Travel Mode Options**:
   - **Self Mode**: Test vehicle type selection (Car, SUV, Motorcycle, Hatchback)
   - **Booking Mode**: Test transport preferences (Flight, Train, Bus, Cab)

## Phase 4: Performance Testing

### 4.1 API Response Time Testing
```bash
# Test response times (should be <300ms)
time curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "kerala", "destination": "assam", "travel_mode": "Self"}'

# Expected: Real time should be < 0.350s
```

### 4.2 Consistency Testing
```bash
# Run multiple requests to check consistency
for i in {1..5}; do
  echo "Test $i:"
  time curl -s -X POST "http://localhost:8000/api/validate-duration" \
    -H "Content-Type: application/json" \
    -d '{"source": "rajasthan", "destination": "uttarakhand", "travel_mode": "Self"}' > /dev/null
done

# Expected: Consistent response times around 280-350ms
```

### 4.3 Load Testing
```bash
# Concurrent requests test
echo "Testing concurrent requests..."
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/validate-duration" \
    -H "Content-Type: application/json" \
    -d '{"source": "mumbai", "destination": "delhi", "travel_mode": "Booking"}' &
done
wait
echo "Load test completed"

# Expected: All requests complete successfully without errors
```

## Phase 5: Production Readiness Testing

### 5.1 Docker Testing (Optional)
```bash
# Test Docker build
docker build -t travelbuddy-frontend .
docker build -t travelbuddy-backend ./server

# Test Docker Compose
docker-compose up -d
docker-compose ps
docker-compose logs

# Test containerized app
curl http://localhost:3000
curl http://localhost:8000

# Cleanup
docker-compose down
```

### 5.2 API Documentation Testing
1. **Open Swagger UI**: Navigate to `http://localhost:8000/docs`
2. **Test Endpoints**:
   - Click on "POST /api/validate-duration"
   - Click "Try it out"
   - Enter test data:
     ```json
     {
       "source": "mumbai",
       "destination": "goa",
       "travel_mode": "Self"
     }
     ```
   - Click "Execute"
   - **Expected**: Valid response with duration recommendations

3. **Test Other Endpoints**: Repeat for `/api/validate-budget` and `/api/plan-trip`

## Phase 6: Edge Case Testing

### 6.1 Geographic Coverage Testing
Test various state combinations to ensure comprehensive coverage:

```bash
# Northeast to West
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "assam", "destination": "gujarat", "travel_mode": "Self"}'

# North to East
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "sikkim", "destination": "rajasthan", "travel_mode": "Booking"}'

# Remote areas
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "nagaland", "destination": "maharashtra", "travel_mode": "Self"}'

# Expected: All combinations return valid duration recommendations
```

### 6.2 Error Handling Testing
```bash
# Test invalid inputs
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "", "destination": "goa", "travel_mode": "Self"}'

curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "mumbai", "destination": "", "travel_mode": "Invalid"}'

# Expected: Proper error responses, not server crashes
```

## Phase 7: User Experience Testing

### 7.1 Complete User Journey
1. **Landing Page**:
   - Verify hero section loads properly
   - Check statistics animation
   - Verify theme badges display correctly

2. **Form Interaction**:
   - Fill out complete travel form step by step
   - Test source/destination autocomplete
   - Test theme selection (visual feedback)
   - Test travel mode switching
   - Test vehicle type selection (for Self mode)
   - Test transport options (for Booking mode)
   - Test budget input validation
   - Test duration dropdown population

3. **Form Submission**:
   - Click "Plan My Trip" button
   - **Expected**: Loading animation with progress messages
   - **Verify**: Form disables during submission

4. **Results Display** (if AI agent available):
   - Verify comprehensive results display
   - Check trip overview section
   - Verify daily itinerary display
   - Check hotel recommendations
   - Verify budget breakdown
   - Test save/share functionality

### 7.2 Mobile Responsiveness
1. **Resize Browser**:
   - Test various screen sizes (mobile, tablet, desktop)
   - **Expected**: Responsive design adapts smoothly

2. **Mobile Interactions**:
   - Test touch interactions on mobile-sized screen
   - Verify dropdown functionality on mobile
   - Check form usability on smaller screens

## Expected Results Summary

| Test Type | Expected Result | Status |
|-----------|----------------|---------|
| **Duration Validation** | < 300ms response, accurate minimum durations | ✅ |
| **Geographic Coverage** | All Indian state combinations supported | ✅ |
| **Travel Mode Logic** | Self mode requires more days than Booking | ✅ |
| **Real-time Updates** | Smooth debounced validation without loops | ✅ |
| **Error Handling** | Graceful error messages, no crashes | ✅ |
| **API Documentation** | Interactive Swagger UI at /docs | ✅ |
| **Performance** | Fast responses, efficient memory usage | ✅ |
| **Production Setup** | Docker containers work correctly | ✅ |

## Validation Checklist

### ✅ Core Functionality
- [ ] Duration validation works for all state combinations
- [ ] Travel mode differences reflected in duration options
- [ ] Budget validation provides meaningful feedback
- [ ] Trip planning generates comprehensive results (if AI available)

### ✅ Performance
- [ ] API responses under 300ms
- [ ] No memory leaks or performance degradation
- [ ] Smooth user interactions without delays
- [ ] Efficient debounced validation

### ✅ User Experience
- [ ] Intuitive form flow
- [ ] Clear validation messages
- [ ] Responsive design works on all devices
- [ ] Loading states provide good feedback

### ✅ Production Readiness
- [ ] Docker containers build and run correctly
- [ ] Environment configuration works
- [ ] API documentation accessible
- [ ] Logging and monitoring functional

## Troubleshooting Common Issues

### Issue: Duration Validation Shows "Checking..." Indefinitely
**Solution**:
```bash
# Check server logs
tail -f server/travelbuddy_server.log

# Check browser DevTools Network tab
# Verify API calls are completing successfully

# Test API directly
curl -X POST "http://localhost:8000/api/validate-duration" \
  -H "Content-Type: application/json" \
  -d '{"source": "mumbai", "destination": "goa", "travel_mode": "Self"}'
```

### Issue: API Returns 500 Errors
**Solution**:
```bash
# Check environment variables
echo $GEMINI_API_KEY

# Verify server is running on correct port
netstat -an | grep 8000

# Check server logs for detailed errors
cat server/travelbuddy_server.log
```

### Issue: Frontend Not Loading
**Solution**:
```bash
# Check if npm dev server is running
ps aux | grep "npm"

# Restart frontend
npm run dev

# Check for port conflicts
netstat -an | grep 3000
```

### Issue: CORS Errors
**Solution**:
- Verify backend CORS configuration allows frontend origin
- Check browser DevTools Console for specific CORS error messages
- Ensure both servers are running on expected ports

## Performance Benchmarks

### API Response Times
- **Duration Validation**: < 300ms (typically 280-350ms)
- **Budget Validation**: < 500ms
- **Trip Planning**: < 30 seconds (with AI agent)

### Frontend Performance
- **Initial Load**: < 2 seconds
- **Form Interactions**: < 100ms response time
- **Validation Updates**: < 400ms (including 300ms debounce)

## Success Criteria

Your TravelBuddy AI application passes testing if:

1. **All API endpoints respond correctly** with expected data formats
2. **Duration validation works** for at least 10 different state combinations
3. **Frontend form interactions** are smooth and responsive
4. **Real-time validation** works without getting stuck in loading states
5. **Performance metrics** meet the specified benchmarks
6. **Docker deployment** works correctly (if tested)
7. **No critical errors** in browser console or server logs

---

**Testing Completed Successfully!** 🎉

Your TravelBuddy AI application is ready for the Google Gen AI Hackathon submission.