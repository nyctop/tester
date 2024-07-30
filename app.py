from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

CONTENT_URLS = {
    'photos': 'https://instagramdownloads.com/photo',
    'videos': 'https://instagramdownloads.com/video',
    'reels': 'https://instagramdownloads.com/reels',
    'stories': 'https://instagramdownloads.com/story-saver',
    'highlights': 'https://instagramdownloads.com/highlights',
    'profile': 'https://instagramdownloads.com/profile',
    'igtv': 'https://instagramdownloads.com/igtv',
}

@app.route('/')
def index():
    return render_template_string(open('index.html').read())

@app.route('/download', methods=['POST'])
def download():
    username = request.form['username']
    content_type = request.form['content_type']
    url = CONTENT_URLS.get(content_type, 'https://instagramdownloads.com/')

    payload = {'url': f'https://www.instagram.com/{username}'}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # `instagramdownloads.com` sitesine POST isteği gönderme
    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code != 200:
        return 'Bir hata oluştu, lütfen tekrar deneyin.'

    # Dönen HTML içeriğini konsola yazdır (debug amaçlı)
    print("Dönen HTML içeriği:")
    print(response.text)

    # HTML içeriğini işleme
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Örnek olarak 'btn--download' sınıfını içeren tüm <a> etiketlerini bulalım
    links = soup.find_all('a', class_='btn--download', href=True)
    download_links = [link['href'] for link in links]

    print("Bulunan indirme bağlantıları:")
    print(download_links)

    if not download_links:
        return 'İndirilecek içerik bulunamadı.'

    # İndirilen dosyaları saklama
    for idx, link in enumerate(download_links):
        print(f"İndirme bağlantısı: {link}")
        r = requests.get(link, allow_redirects=True)
        if r.status_code == 200:
            ext = link.split('.')[-1]
            filename = os.path.join(DOWNLOAD_FOLDER, f'{username}_{content_type}_{idx}.{ext}')
            with open(filename, 'wb') as f:
                f.write(r.content)
        else:
            print(f"Dosya indirilirken hata oluştu: {link}")
    
    return redirect(url_for('list_files'))

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
