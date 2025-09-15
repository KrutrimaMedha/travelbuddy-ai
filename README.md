# 🌍 TravelBuddy AI

An AI-powered travel planning assistant that helps users create personalized travel itineraries using Google Generative AI and real-time search capabilities.

## 🎯 Main Package

This repository contains the **travel_planner** package - a complete, self-contained AI travel planning system, and a **weather_tool** MCP server for weather data.

```
travelbuddy-ai/
├── travel_planner/          # 🎯 Complete Travel Planning Package
│   ├── src/                 # Source code
│   ├── tests/               # Test suite  
│   ├── examples/            # Example scripts
│   ├── README.md           # Complete documentation & setup guide
│   └── pyproject.toml      # Package configuration
├── weather_tool/            # 🌤️ Weather MCP Tool (Open‑Meteo)
│   ├── src/                 # Source code
│   ├── README.md           # Usage and server details
│   └── pyproject.toml      # Package configuration
├── .env.example            # Environment template
├── LICENSE                 # MIT License
└── README.md               # This file (overview)
```

## 🚀 Quick Start

**Navigate to the travel_planner package and follow its complete setup guide:**

```bash
cd travel_planner
# Follow the detailed instructions in travel_planner/README.md
```

The travel_planner package contains:
- ✅ Complete setup instructions with uv
- ✅ Full documentation and examples  
- ✅ Comprehensive test suite
- ✅ All source code and dependencies

## 📖 Complete Documentation

**👉 See [travel_planner/README.md](travel_planner/README.md) for:**
- 🛠️ Complete setup instructions with uv
- 🧪 Testing guide and commands
- 💡 Usage examples and API reference
- 🔧 Development workflow
- 🔑 API keys setup
- 🚀 Quick start guide

For the Weather MCP tool, see [weather_tool/README.md](weather_tool/README.md).

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
3. Make changes in the `travel_planner/` directory
4. Run tests: `uv run pytest`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: [travel_planner/README.md](travel_planner/README.md)
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions

---

**🎯 For the complete setup guide and detailed documentation, see [travel_planner/README.md](travel_planner/README.md)**
