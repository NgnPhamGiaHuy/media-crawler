# Media Crawler - Python Based Web Scraper

A powerful web application for crawling websites and extracting media files (images, videos, and audio) with an intuitive user interface.

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔍 Extract media files from websites (images, videos, audio)
- 🔗 Configurable crawl depth for exploring linked pages
- 📁 Automatic caching of downloaded media
- 🖼️ Thumbnail generation for quick preview
- 📱 Responsive web interface
- 📊 Detailed crawling statistics
- 🚀 Asynchronous processing with aiohttp
- 🛡️ Respects robots.txt (configurable)

## 📋 Requirements

- Python 3.7+
- Flask
- aiohttp
- BeautifulSoup4
- Pillow
- Python-magic
- Other dependencies listed in `requirements.txt`

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/ngnphamgiahuy/media-crawler.git
cd media-crawler
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (optional, for custom configuration):
```
DEBUG=True
SECRET_KEY=your_secret_key
CACHE_DIR=@cachefolder
MAX_CRAWL_DEPTH=1
RESPECT_ROBOTS_TXT=True
```

## 🏃‍♂️ Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5050
```

3. Enter a URL to crawl and configure crawl options
4. View and download extracted media files

## 🔧 Configuration

Configure the application using environment variables or a `.env` file:

| Setting | Description | Default |
|---------|-------------|---------|
| `DEBUG` | Enable debug mode | False |
| `CACHE_DIR` | Directory to store cached media | @cachefolder |
| `CACHE_EXPIRY` | Cache expiry time in seconds | 3600 |
| `MAX_CRAWL_DEPTH` | Maximum depth to crawl | 0 |
| `RESPECT_ROBOTS_TXT` | Whether to respect robots.txt | True |
| `HOST` | Host to bind the server | 0.0.0.0 |
| `PORT` | Port to run the server | 5050 |

## 🏗️ Project Structure

```
media-crawler/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── app/                   # Application package
│   ├── routes/            # API and web routes
│   ├── services/          # Core functionality
│   │   ├── crawler/       # Web crawling logic
│   │   ├── media/         # Media downloading and processing
│   │   └── cache/         # Caching system
│   ├── config/            # Configuration settings
│   ├── models/            # Data models
│   ├── utils/             # Utility functions
│   ├── templates/         # HTML templates
│   └── static/            # Static assets (CSS, JS, images)
```

## 🔄 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/crawl` | POST | Start crawling a website |
| `/api/media` | GET | Get all extracted media |
| `/api/media/<id>` | GET | Get specific media item |
| `/api/clear-cache` | POST | Clear the cache |
| `/api/status` | GET | Get crawling status |
| `/api/cache-info` | GET | Get cache information |

## 🧠 How It Works

1. **Crawling**: The application crawls the target website using asynchronous requests
2. **Extraction**: Identifies media files based on HTML structure and JSON data
3. **Processing**: Downloads media files, generates thumbnails, and extracts metadata
4. **Caching**: Stores media files and metadata for faster access
5. **Presentation**: Displays media in an intuitive web interface

## 🔒 Security Considerations

- The application stores media files temporarily in the cache folder
- Cache sessions are automatically expired and cleaned
- User-provided URLs are validated and normalized
- Content-type validation is performed on downloaded files

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [aiohttp](https://docs.aiohttp.org/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Pillow](https://python-pillow.org/) 