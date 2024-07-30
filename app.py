from flask import Flask, request, render_template_string, send_from_directory
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template_string(open('index.html').read())

@app.route('/download', methods=['POST'])
def download():
    username = request.form['username']
    url = 'https://instagramdownloads.com/'
    payload = {'username': username}
    
    # `instagramdownloads.com` sitesine POST isteği gönderme
    response = requests.post(url, data=payload)
    
    if response.status_code != 200:
        return 'Bir hata oluştu, lütfen tekrar deneyin.'

    # HTML içeriğini işleme
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    download_links = [link['href'] for link in links if 'download' in link['href']]

    # İndirilen dosyaları saklama
    for idx, link in enumerate(download_links):
        r = requests.get(link, allow_redirects=True)
        filename = os.path.join(DOWNLOAD_FOLDER, f'{username}_{idx}.jpg')
        with open(filename, 'wb') as f:
            f.write(r.content)
    
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
    </body>
    </html>
    """, files=files)

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
