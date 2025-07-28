
# 📌 Pinterest-Style Collage Generator

A web-based image scraping and collage creation tool built with **Flask**, **Selenium**, and **BeautifulSoup**. This app lets users input a URL, automatically scrape images from it, select desired images, and generate beautiful Pinterest-style collages with custom titles.

---

## ✨ Features

- 🔗 **URL Scraping**: Automatically loads and scrolls through pages to extract images.
- 📸 **Image Selection UI**: Select up to 6 images with a responsive grid gallery.
- 🎨 **Custom Titles**: Edit collage titles before generating final designs.
- 📐 **Pinterest Aspect Ratio (2:3)**: Collages are perfectly sized for Pinterest.
- 🖼️ **Canvas-Based Design**: Final collages rendered using Fabric.js.
- 📥 **Download Ready**: Export final designs as image files.
- 🔁 **Built-in Image Proxy**: Avoids CORS errors by fetching and streaming external images through Flask.

---

## 🗂 Project Structure

```
project/
│
├── templates/
│   ├── index.html              # Input page for scraping URL
│   ├── select_images.html      # Grid view for image selection
│   ├── design.html             # Collage generation and download
│
├── static/css
│   ├── index.css               # CSS for the index page
│   ├── select_images.css       # CSS for the image selection 
│   ├── design.css              # CSS for collage display
│
├── app.py                      # Main Flask application
├── Requirements.txt            # List of Python dependencies
└── README.md                   # Project documentation
```

---

## ⚙️ Setup Instructions

### 🔧 Prerequisites

- Python 3.7+
- Google Chrome installed
- ChromeDriver (automatically handled via `webdriver-manager`)

### 📦 Installation

1. **Install dependencies**
   ```bash
   pip install -r Requirements.txt
   ```

2. **Run the app**
   ```bash
   python app.py
   ```

3. **Visit in browser**
   ```
   http://localhost:5000
   ```
---

## 🧪 How It Works

1. **User enters a product/category URL**
2. **Selenium** opens the URL in a headless Chrome browser, scrolls, and clicks "Load More" buttons.
3. **BeautifulSoup** parses the HTML and extracts images with good quality.
4. Images are filtered and displayed in a grid for user selection.
5. User selects 2+ images and customizes a title.
6. Final collages are generated and rendered with **Fabric.js**, with a download option.

## 🧰 Tech Stack

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)

![Flask](https://img.shields.io/badge/Flask-Web_Framework-lightgrey?logo=flask)

![Selenium](https://img.shields.io/badge/Selenium-Automation-brightgreen?logo=selenium)

![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-Web%20Scraping-yellowgreen)

![Fabric.js](https://img.shields.io/badge/Fabric.js-Canvas_Design-blueviolet)

