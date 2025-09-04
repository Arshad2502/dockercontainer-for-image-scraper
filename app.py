from flask import Flask, render_template, request, jsonify, send_file
import os
import threading
from scraper import ImageScraper   
import zipfile
import io

app = Flask(__name__)

# Add CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Global scraping status
scraping_status = {
    'active': False,
    'progress': 0,
    'total': 0,
    'downloaded': 0,
    'message': 'Ready to start scraping'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def start_scraping():
    global scraping_status

    if scraping_status['active']:
        return jsonify({'error': 'Scraping already in progress'})

    data = request.json
    source = data.get('source', 'google')
    query = data.get('query', '') 
    max_images = int(data.get('max_images', 20))

    # Start scraping in a background thread
    thread = threading.Thread(
        target=run_scraper,
        args=(source, query, max_images)
    )
    thread.start()

    return jsonify({'message': 'Scraping started'})

def run_scraper(source, query, max_images):
    global scraping_status

    scraping_status['active'] = True
    scraping_status['progress'] = 0
    scraping_status['total'] = max_images
    scraping_status['downloaded'] = 0
    scraping_status['message'] = f'Starting scraper for {source}...'

    try:
        scraper = ImageScraper()  
        downloaded = scraper.scrape_and_download(source, query, max_images)

        scraping_status['downloaded'] = downloaded
        scraping_status['message'] = f'Scraping completed! Downloaded {downloaded} images'
    except Exception as e:
        scraping_status['message'] = f'Error: {str(e)}'
    finally:
        scraping_status['active'] = False

@app.route('/status')
def get_status():
    return jsonify(scraping_status)

@app.route('/images')
def list_images():
    download_path = 'downloads'
    if not os.path.exists(download_path):
        return jsonify([])

    images = []
    for filename in os.listdir(download_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            images.append({
                'filename': filename,
                'url': f'/download/{filename}'
            })

    return jsonify(images)

@app.route('/download/<filename>')
def download_image(filename):
    filepath = os.path.join('downloads', filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    return 'File not found', 404

@app.route('/download-all')
def download_all():
    download_path = 'downloads'
    if not os.path.exists(download_path):
        return 'No images found', 404

    # Create ZIP file in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename in os.listdir(download_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                filepath = os.path.join(download_path, filename)
                zip_file.write(filepath, filename)

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='images.zip' 
    )

@app.route('/clear')
def clear_images():
    download_path = 'downloads'
    if os.path.exists(download_path):
        for filename in os.listdir(download_path):
            filepath = os.path.join(download_path, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

    return jsonify({'message': 'All images cleared'})

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    print("Starting Flask app on http://0.0.0.0:5000")
    print("Access the web interface at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

