from flask import Flask, render_template_string, request
import requests
from datetime import datetime

app = Flask(__name__)

USERNAME = 'xxxxx'
ACCESS_KEY = 'xxxxx'
API_URL = 'https://api.hikerapi.com/a2/user'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_username = request.form['username']
        url = f"{API_URL}?username={target_username}"
        headers = {
            'accept': 'application/json',
            'x-access-key': ACCESS_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            user_info = response.json()
            user = user_info['graphql']['user']
            return render_template_string(html_template, user=user)
        else:
            return f"Error fetching data: {response.status_code}"
    return render_template_string(form_template)

form_template = """
<html>
<head>
    <title>Kullanıcı Bilgileri</title>
</head>
<body>
    <h1>Kullanıcı Bilgileri</h1>
    <form method="POST">
        <label for="username">Kullanıcı Adı:</label>
        <input type="text" id="username" name="username" required>
        <button type="submit">Getir</button>
    </form>
</body>
</html>
"""

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Kullanıcı Bilgileri</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        img {
            max-width: 100px;
            height: auto;
        }
    </style>
</head>
<body>
    <h1>Kullanıcı Bilgileri</h1>
    <table>
        <tr><th>Attribute</th><th>Value</th></tr>
        <tr><td>ID</td><td>{{ user.id }}</td></tr>
        <tr><td>Biography</td><td>{{ user.biography }}</td></tr>
        <tr><td>Full Name</td><td>{{ user.full_name }}</td></tr>
        <tr><td>Followers</td><td>{{ user.edge_followed_by.count }}</td></tr>
        <tr><td>Following</td><td>{{ user.edge_follow.count }}</td></tr>
        <tr><td>Profile Picture</td><td>{% if user.profile_pic_url %}<img src="{{ user.profile_pic_url }}" alt="Profile Picture">{% else %}Profile picture not available{% endif %}</td></tr>
        <tr><td>High-Res Profile Picture</td><td>{% if user.profile_pic_url_hd %}<img src="{{ user.profile_pic_url_hd }}" alt="High-Res Profile Picture">{% else %}High-res profile picture not available{% endif %}</td></tr>
        <tr><td>Total Posts</td><td>{{ user.edge_owner_to_timeline_media.count }}</td></tr>
    </table>
    <h2>Recent Posts</h2>
    <table>
        <tr>
            <th>Post ID</th>
            <th>Caption</th>
            <th>Likes</th>
            <th>Comments</th>
            <th>Location</th>
            <th>Images</th>
            <th>Date</th>
        </tr>
        {% for edge in user.edge_owner_to_timeline_media.edges %}
            {% set post = edge.node %}
            <tr>
                <td>{{ post.id }}</td>
                <td>{{ post.edge_media_to_caption.edges[0].node.text if post.edge_media_to_caption.edges else '' }}</td>
                <td>{{ post.edge_liked_by.count }}</td>
                <td>{{ post.edge_media_to_comment.count }}</td>
                <td>{{ post.location.name if post.location else 'N/A' }}</td>
                <td>
                    {% if post.__typename == 'GraphSidecar' %}
                        {% for child in post.edge_sidecar_to_children.edges %}
                            {% if child.node.display_url %}
                                <a href="{{ child.node.display_url }}" target="_blank"><img src="{{ child.node.thumbnail_url }}" width="50"></a>
                            {% else %}
                                Image not available
                            {% endif %}
                        {% endfor %}
                    {% else %}
                        {% if post.display_url %}
                            <a href="{{ post.display_url }}" target="_blank"><img src="{{ post.thumbnail_url }}" width="50"></a>
                        {% else %}
                            Image not available
                        {% endif %}
                    {% endif %}
                </td>
                <td>{{ datetime.fromtimestamp(post.taken_at_timestamp).strftime('%Y-%m-%d %H:%M:%S') if post.taken_at_timestamp else 'N/A' }}</td>
            </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
