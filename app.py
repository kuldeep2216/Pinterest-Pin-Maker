from flask import Flask, render_template, request, session, redirect, url_for, flash, Response
import requests, os, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_and_complex_key_that_you_should_change_for_production_use')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    if not url:
        flash("Please enter a URL.", "error")
        return redirect(url_for('index'))
    if not urlparse(url).scheme: url = "https://" + url

    options = Options()
    for arg in ["--headless","--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--window-size=1920,1080","--start-maximized"]:
        options.add_argument(arg)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(3)
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            try:
                load_more_button = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH,
                   "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more')] | "
                   "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more')] | "
                   "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more')] | "
                   "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show more')] | "
                   "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show more')] | "
                   "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show more')] | "
                   "//button[contains(@class, 'load-more')] | //a[contains(@class, 'load-more')] | //div[contains(@class, 'load-more')] | "
                   "//button[contains(@class, 'show-more')] | //a[contains(@class, 'show-more')] | //div[contains(@class, 'show-more')]"
                )))
                if load_more_button: driver.execute_script("arguments[0].click();", load_more_button); time.sleep(2)
            except: pass
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        session['page_title'] = soup.title.text if soup.title else "Untitled Page"
        scraped_images_raw = []
        for img in soup.find_all('img'):
            img_src = img.get('src')
            img_data_src = img.get('data-src')
            img_srcset = img.get('srcset')
            img_data_srcset = img.get('data-srcset')
            fu = None
            if img_data_src and not img_data_src.startswith('data:'): fu = img_data_src
            elif img_data_srcset and not img_data_srcset.startswith('data:'): fu = img_data_srcset.split(',')[0].strip().split(' ')[0]
            elif img_srcset and not img_srcset.startswith('data:'): fu = img_srcset.split(',')[0].strip().split(' ')[0]
            elif img_src and not img_src.startswith('data:'): fu = img_src
            if fu and not fu.startswith('data:image/svg') and not fu.endswith('.svg'):
                abs_url = urljoin(url, fu)
                path = urlparse(abs_url).path
                if path and path.lower().endswith(('.png','.jpg','.jpeg','.gif','.webp')):
                    try: w = int(str(img.get('width','0')).replace('px','').replace('%','').strip()); h = int(str(img.get('height','0')).replace('px','').replace('%','').strip())
                    except: w = h = 0
                    if w > 0 and h > 0 and (w < 50 or h < 50): continue
                    alt = img.get('alt','No Alt Text')
                    scraped_images_raw.append(f"{abs_url}|||{alt}")
        uniques, seen = [], set()
        for item in scraped_images_raw:
            u = item.split('|||')[0]
            if u not in seen: uniques.append(item); seen.add(u)
        session['scraped_images'] = uniques
        return redirect(url_for('select_images'))
    except TimeoutException:
        flash(f"Page loading timed out for {url}. Please try again or a different URL.", "error")
        return redirect(url_for('index'))
    except WebDriverException as e:
        flash(f"Browser automation error: {e}. Ensure Chrome is installed and updated.", "error")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"An unexpected error occurred during scraping: {e}", "error")
        return redirect(url_for('index'))
    finally:
        if driver: driver.quit()

@app.route('/select_images')
def select_images():
    images = session.get('scraped_images', [])
    page_title = session.get('page_title', 'Untitled Page')
    if not images:
        flash("No images found or scrape failed for the provided URL. Please try a different URL.", "error")
        return redirect(url_for('index'))
    return render_template('select_images.html', images=images, page_title=page_title)

@app.route('/generate_collages', methods=['POST'])
def generate_collages():
    selected = request.form.getlist('selected_images')
    custom_title = request.form.get('custom_title')
    title = custom_title.strip() if custom_title and custom_title.strip() else session.get('page_title', "Untitled Collage")
    if not selected or len(selected) < 2:
        flash('Please select at least 2 images to create collages.', 'error')
        return redirect(url_for('select_images'))
    session['selected_images_for_collage'] = selected
    session['final_collage_title'] = title
    return redirect(url_for('design_page'))

@app.route('/proxy')
def proxy():
    image_url = request.args.get('url')
    if not image_url: return "URL parameter is missing", 400
    try:
        r = requests.get(image_url, stream=True, timeout=10)
        r.raise_for_status()
        ctype = r.headers.get('Content-Type')
        if not ctype or not ctype.startswith('image/'):
            if any(x in image_url.lower() for x in ['.png','.jpg','.jpeg','.gif','.webp']): ctype = 'image/jpeg'
            else: return "Not an image or unsupported content type", 415
        def gen(): yield from r.iter_content(chunk_size=8192)
        return Response(gen(), mimetype=ctype)
    except requests.exceptions.RequestException: return f"Proxy fetch failed for {image_url}", 500
    except Exception as e: return f"An unexpected error occurred in proxy: {e}", 500

@app.route('/design')
def design_page():
    imgs = session.get('selected_images_for_collage', [])
    title = session.get('final_collage_title', "Generated Collage")
    if not imgs:
        flash("No images were selected for collage generation. Please go back and select images.", "error")
        return redirect(url_for('index'))
    return render_template('design.html', images=imgs, page_title=title)

if __name__ == '__main__':
    app.run(debug=True)
    