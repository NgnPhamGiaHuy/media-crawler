# 🌐 Media Crawler

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green)

## 📝 Description

Media Crawler is a powerful web application that automates the discovery and downloading of media files (images, videos, and audio) from any website. It uses asynchronous crawling techniques to efficiently navigate through web pages, extract media URLs, and download them into a structured cache system. Perfect for content creators, researchers, and developers who need to extract media assets from websites.

The application features a clean web interface for URL submission and results viewing, with a robust backend API that handles the crawling, downloading, and media processing.

## ✨ Features

- Crawls websites to discover and download media files (images, videos, audio)
- Supports customizable crawl depth for single-page or multi-page extraction
- Generates thumbnails for visual preview of discovered media
- Respects robots.txt directives for ethical crawling
- Maintains session-based caching for efficient storage and retrieval
- Provides a clean web interface for easy interaction
- Offers a comprehensive API for programmatic access
- Handles concurrent downloads for optimal performance
- Auto-cleanup of expired cache sessions

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/NgnPhamGiaHuy/media-crawler.git
cd media-crawler

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp env.example .env  # Then edit the .env file as needed
```

## 🚀 Usage

```bash
# Run the application
python app.py

# Access the web interface
# Open http://localhost:5050 in your browser
```

### API Usage

```bash
# Example API call to crawl a URL
curl -X POST http://localhost:5050/api/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "depth": 1}'
```

## 🔧 Configuration

Create a `.env` file in the root directory with the following variables (or set them as environment variables):

```
DEBUG=False
SECRET_KEY=your_secret_key_here
CACHE_DIR=@cachefolder
CACHE_EXPIRY=3600
MAX_CRAWL_DEPTH=1
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
RESPECT_ROBOTS_TXT=True
USER_AGENT=MediaCrawler/1.0
HOST=0.0.0.0
PORT=5050
```

## 🗂️ Folder Structure

```
├── app/                  # Application code
│   ├── config/           # Configuration settings
│   ├── models/           # Data models
│   ├── routes/           # API and web routes
│   ├── services/         # Core services (crawler, cache, media)
│   │   ├── cache/        # Cache management
│   │   ├── crawler/      # Web crawling engine
│   │   └── media/        # Media processing
│   ├── static/           # Static files (JS, CSS)
│   ├── templates/        # HTML templates
│   └── utils/            # Utility functions
├── venv/                 # Virtual environment
├── app.py                # Application entry point
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## 🤝 Contributing

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/NgnPhamGiaHuy/media-crawler.git

# Create a feature branch
git checkout -b feature/amazing-feature

# Commit your changes
git commit -m "Add amazing feature"

# Push to the branch
git push origin feature/amazing-feature

# Open a Pull Request
```

## 📄 License

Licensed under the MIT License. See [LICENSE](./LICENSE) for more information.

## 👤 Author

**NgnPhamGiaHuy**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/NgnPhamGiaHuy)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/nguyenphamgiahuy)

## 🙏 Acknowledgements

- Built with Flask and Beautiful Soup
- Asynchronous operations powered by aiohttp
- Interface styled with Bootstrap
- Icons by Font Awesome 