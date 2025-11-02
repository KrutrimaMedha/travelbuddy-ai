# 🌍 TravelBuddy AI

An AI-powered travel planning assistant that helps users create personalized travel itineraries using Google Generative AI and real-time search capabilities.

## 🎯 Main Package

This repository contains the **travel_planner_agent** package - a complete, self-contained AI travel planning system.

```
travelbuddy-ai/
├── travel_planner_agent/     # 🤖 Core AI planning engine (Python package)
├── travel_planner_ui/        # 🎨 React + Tailwind EaseMyTrip-themed interface
│   ├── server/               # FastAPI gateway for the UI and mock EMT booking
│   └── docs/api/openapi.json # Generated OpenAPI spec for the server
├── docs/                     # Deployment & API documentation
├── .env.example              # Environment template
├── LICENSE                   # MIT License
└── README.md                 # This file (overview)
```

## 🚀 Quick Start

**Navigate to the travel_planner_agent package and follow its complete setup guide:**

```bash
cd travel_planner_agent
# Follow the detailed instructions in travel_planner_agent/README.md
```

The travel_planner_agent package contains:
- ✅ Complete setup instructions with uv
- ✅ Full documentation and examples  
- ✅ Comprehensive test suite
- ✅ All source code and dependencies

## 🖥️ Travel Planner UI

The `travel_planner_ui/` workspace provides the EaseMyTrip-inspired React experience, including the new mock “Book on EaseMyTrip” hand-off. See [travel_planner_ui/README.md](travel_planner_ui/README.md) for:

- Local UI development (`npm run dev`) and type checks
- Tailwind theming tokens aligned with EaseMyTrip branding
- Integration details for the mock booking flow and confirmation modal

## 🔌 FastAPI Gateway & Mock Services

The UI’s Python gateway lives in `travel_planner_ui/server/` and now exposes:

- `/api/mock-hotel-booking` – mocked EaseMyTrip-style confirmation payloads
- `/api/plan-trip` and validation endpoints backed by `travel_planner_agent`

Updated setup steps and environment variables are in [travel_planner_ui/server/README.md](travel_planner_ui/server/README.md). The generated OpenAPI/Swagger schema is available at `docs/api/openapi.json`.

## 📖 Complete Documentation

**👉 Detailed docs:**
- [travel_planner_agent/README.md](travel_planner_agent/README.md) – AI engine setup, uv workflow & testing
- [travel_planner_ui/README.md](travel_planner_ui/README.md) – React UI, theming and mock booking flow
- [travel_planner_ui/server/README.md](travel_planner_ui/server/README.md) – FastAPI gateway, environment config & mock endpoints
- [docs/api/openapi.json](docs/api/openapi.json) – Generated Swagger/OpenAPI schema for the server

## ☁️ Cloud Run Deployment

For CI/CD with GitHub Actions, Workload Identity Federation, and Artifact Registry setup, see:

- docs/DEPLOYMENT.md

## ✨ Key Features

- 🤖 **AI-Powered Planning**: Google Generative AI integration
- 🔍 **Real-time Search**: SERP API for current information  
- 🎯 **Theme-based**: Adventure, Cultural, Devotional, Nightlife
- 💰 **Budget Validation**: Smart cost analysis
- 🚗 **Multi-modal Transport**: Self-drive and public transport
- 🌤️ **Weather Integration**: Weather-appropriate recommendations
- 📱 **Structured Output**: JSON responses for UI integration

## 🔑 Environment Setup

```bash
# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Get API keys from:
# - Google AI Studio: https://makersuite.google.com/app/apikey
# - SerpApi: https://serpapi.com/ (optional)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes in the `travel_planner_agent/` directory
4. Run tests: `uv run pytest`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: [travel_planner_agent/README.md](travel_planner_agent/README.md)
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions

---

**🎯 For the complete setup guide and detailed documentation, see [travel_planner_agent/README.md](travel_planner_agent/README.md)**
