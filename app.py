from flask import Flask, request, render_template_string, send_from_directory
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

html_form = '''
<!DOCTYPE html>
<html>
<head>
    <title>Instaloader Kullanıcı Adı Girişi</title>
</head>
<body>
    <h1>Instaloader Kullanıcı Adı Girişi</h1>
    <form action="/run_instaloader" method="post">
        <label for="username">Kullanıcı Adı:</label>
        <input type="text" id="username" name="username" required>
        <button type="submit">Gönder</button>
    </form>
    <h2>İndirilen Dosyalar:</h2>
    <ul>
        {% for file in files %}
            <li><a href="{{ url_for('download_file', filename=file) }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
'''

@app.route('/')
def index():
    files = os.listdir(app.config['DOWNLOAD_FOLDER'])
    return render_template_string(html_form, files=files)

@app.route('/run_instaloader', methods=['POST'])
def run_instaloader():
    username = request.form['username']
    current_dir = os.path.dirname(os.path.abspath(__file__))
    command = f"instaloader --dirname-pattern={app.config['DOWNLOAD_FOLDER']}/{username} profile {username}"
    
    result = os.system(command)
    
    if result != 0:
        return f"Instaloader çalıştırılamadı. Lütfen kullanıcı adını ve bağlantınızı kontrol edin. <a href='/'>Geri Dön</a>"
    
    return f"Kullanıcı {username} için Instaloader çalıştırıldı! <a href='/'>Geri Dön</a>"

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
