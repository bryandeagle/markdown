from flask import Flask, request, send_file, Response
from pypandoc import convert_text
from os import path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from time import time, localtime
from io import BytesIO

app = Flask(__name__)


@app.route('/result.md', methods=['GET', 'POST'])
def root():
    if request.type == 'GET':
        return app.send_static_file('index.html')
    elif request.type == 'POST':
        file_list = request.files.getlist('fileselect[]')
        if len(file_list) == 0:
            return 'No'
        elif len(file_list) == 1:
            file = request.files.getlist('fileselect[]')[0]

            # Get file name and type
            filename = path.splitext(file.filename)[0]
            filetype = path.splitext(file.filename)[1].strip('.')

            # Convert to markdown
            markdown = convert_text(file.stream.read(), 'md', filetype)

            # Send markdown file as attachment
            return Response(markdown, mimetype='text/markdown',
                            headers={'Content-Disposition': 'attachment;filename={}.md'.format(filename)})
        else:
            memory_file = BytesIO()
            with ZipFile(memory_file, 'w') as zf:
                for file in request.files.getlist('fileselect[]'):

                    # Get file name and file type
                    filename = path.splitext(file.filename)[0]
                    filetype = path.splitext(file.filename)[1].strip('.')

                    # Convert to markdown
                    markdown = convert_text(file.stream.read(), 'md', filetype)

                    # Write File to Zipfile
                    data = ZipInfo('{}.md'.format(filename))
                    data.date_time = localtime(time())[:6]
                    data.compress_type = ZIP_DEFLATED
                    zf.writestr(data, markdown)

            # Send zip file as attachment
            memory_file.seek(0)
            return send_file(memory_file, attachment_filename='results.zip', as_attachment=True)


if __name__ == "__main__":
    app.run()
