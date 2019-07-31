from flask import Flask, request, redirect, url_for
from pypandoc import convert_file, convert_text
from os import path
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def root(): return redirect(url_for('index'))


@app.route('/index.html', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist("fileselect[]")
        for file in files:
            file_type = path.splitext(file.filename)[1].strip('.')
            return convert_text(file.stream.read(), 'md', file_type)
        return str(request.form)
    else:
        return app.send_static_file('index.html')


if __name__ == "__main__":
    app.run()
