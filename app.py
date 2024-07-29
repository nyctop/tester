from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

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
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_form)

@app.route('/run_instaloader', methods=['POST'])
def run_instaloader():
    username = request.form['username']
    current_dir = os.path.dirname(os.path.abspath(__file__))
    command = f"python3 {current_dir}/instaloader.py {username}"
    os.system(command)
    return f"Kullanıcı {username} için Instaloader çalıştırıldı!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
