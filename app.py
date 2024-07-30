from flask import Flask, request, send_from_directory, render_template_string, jsonify
import os
import subprocess
import json
import instaloader

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
LOCATION_FILE = 'locations.json'

@app.route('/')
def index():
    return render_template_string(open('index.html').read())

@app.route('/download', methods=['POST'])
def download():
    username = request.form['username']
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    
    # Instagram içeriklerini indirme ve konum bilgilerini çıkartma
    loader = instaloader.Instaloader(dirname_pattern=DOWNLOAD_FOLDER)
    profile = instaloader.Profile.from_username(loader.context, username)
    locations = []

    for post in profile.get_posts():
        if post.location:
            location_info = {
                'title': post.title,
                'latitude': post.location.lat,
                'longitude': post.location.lng,
                'type': 'Video' if post.is_video else 'Photo'
            }
            locations.append(location_info)

    with open(os.path.join(DOWNLOAD_FOLDER, LOCATION_FILE), 'w') as f:
        json.dump(locations, f)

    return 'İndirme işlemi tamamlandı. <a href="/files">İndirilen Dosyaları Gör</a>'

@app.route('/files')
def list_files():
    files = os.listdir(DOWNLOAD_FOLDER)
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>İndirilen Dosyalar</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
            }
            h1 {
                margin-bottom: 20px;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin: 5px 0;
            }
            a {
                text-decoration: none;
                color: #007bff;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>İndirilen Dosyalar</h1>
        <ul>
        {% for file in files %}
            <li><a href="/files/{{ file }}">{{ file }}</a></li>
        {% endfor %}
        </ul>
        <a href="/">Geri Dön</a>
        <h2>Harita Üzerinde Gör</h2>
        <div id="map" style="height: 500px;"></div>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <script>
            var map = L.map('map').setView([0, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);

            fetch('/locations')
                .then(response => response.json())
                .then(data => {
                    data.forEach(location => {
                        L.marker([location.latitude, location.longitude])
                            .bindPopup(`<b>${location.title}</b><br>${location.type}`)
                            .addTo(map);
                    });
                });
        </script>
    </body>
    </html>
    """, files=files)

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

@app.route('/locations')
def locations():
    with open(os.path.join(DOWNLOAD_FOLDER, LOCATION_FILE), 'r') as f:
        locations = json.load(f)
    return jsonify(locations)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
