# punter613's AI Assistant

A powerful AI companion app with floating overlay interface, built with React, FastAPI, and Google Gemini 2.0 Flash.

![AI Assistant Demo](https://img.shields.io/badge/PWA-Ready-green) ![AI Powered](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-blue) ![Platform](https://img.shields.io/badge/Platform-Web%2FAndroid%2FWindows-purple)

## ✨ Features

### 🤖 Advanced AI Capabilities
- **Google Gemini 2.0 Flash** integration for intelligent responses
- **Conversation memory** - AI remembers context across messages
- **Code assistance** - Help with programming in any language
- **File analysis** - Upload and analyze documents, images, code files
- **Creative tasks** - Writing, brainstorming, problem solving

### 🎨 Modern Interface
- **Floating AI companion** - Draggable smiley face overlay
- **Beautiful code blocks** - Syntax highlighting with copy/download buttons
- **Session management** - Create, save, and organize conversations
- **Responsive design** - Works perfectly on mobile and desktop
- **Dark theme** - Professional, eye-friendly interface

### 📱 Progressive Web App (PWA)
- **Installable** on Android, Windows, and other platforms
- **Offline capable** with service worker
- **Native app experience** when installed
- **Quick access** from home screen or start menu

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and Python 3.8+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-assistant.git
   cd ai-assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Create .env file
   echo "MONGO_URL=mongodb://localhost:27017" > .env
   echo "DB_NAME=punter613_ai_app" >> .env
   echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   yarn install
   
   # Create .env file
   echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env
   ```

4. **Start the application**
   ```bash
   # Backend (in backend directory)
   python -m uvicorn server:app --host 0.0.0.0 --port 8001
   
   # Frontend (in frontend directory)
   yarn start
   ```

5. **Visit** `http://localhost:3000` in your browser

## 💻 Installation as App

### Android
1. Open the app in Chrome browser
2. Tap the "Add to Home Screen" prompt
3. Or use Chrome menu → "Add to Home Screen"

### Windows/Mac/Linux
1. Open the app in Chrome or Edge
2. Look for the install icon in the address bar
3. Click "Install" to add to your system

## 🛠️ Technology Stack

- **Frontend**: React 19, Tailwind CSS, Radix UI
- **Backend**: FastAPI, Python 3.8+
- **Database**: MongoDB
- **AI**: Google Gemini 2.0 Flash
- **PWA**: Service Worker, Web App Manifest

## 📂 Project Structure

```
ai-assistant/
├── frontend/          # React PWA
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── services/      # API services
│   │   └── hooks/         # Custom hooks
│   └── public/
│       ├── manifest.json  # PWA manifest
│       └── sw.js          # Service worker
├── backend/           # FastAPI server
│   ├── server.py         # Main server file
│   └── requirements.txt  # Python dependencies
└── README.md
```

## 🎯 Key Components

- **FloatingAssistant.jsx** - Draggable AI companion overlay
- **ChatInterface.jsx** - Main chat interface
- **CodeBlock.jsx** - Enhanced code display with copy/download
- **PWAInstaller.jsx** - Installation prompt for PWA

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=punter613_ai_app
GEMINI_API_KEY=your_api_key_here
```

**Frontend (.env)**
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- Radix UI for component primitives
- Tailwind CSS for styling
- FastAPI for the backend framework

## 📞 Support

If you have any questions or issues, please open an issue on GitHub or contact [your-email@example.com].

---

**Made with ❤️ by punter613**
