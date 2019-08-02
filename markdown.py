from flask import Flask, request, send_file, Response, flash, render_template
from pypandoc import convert_text
from os import path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from time import time, localtime
from io import BytesIO

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return app.send_static_file('index.html')
    elif request.method == 'POST':
        file_list = request.files.getlist('files[]')
        # Return single file
        if len(file_list) < 1:
            return 'No files uploaded'
        elif len(file_list) == 1:
            file = file_list[0]
            # Get file name and type
            filename = path.splitext(file.filename)[0]
            file_type = path.splitext(file.filename)[1].strip('.')

            try:  # Convert to markdown
                markdown = convert_text(file.stream.read(), 'md', file_type)
            except RuntimeError as e:
                if e.args[0].startswith('Invalid input format!'):
                    return 'Unsupported file type: {}'.format(file_type.upper())
                else:
                    return 'Unknown Error'

            # Send markdown file as attachment
            return Response(markdown, mimetype='text/markdown',
                            headers={'Content-Disposition': 'attachment;filename={}.md'.format(filename)})

        elif len(file_list) > 1:  # Return zip file
            memory_file = BytesIO()
            with ZipFile(memory_file, 'w') as zf:
                for file in file_list:

                    # Get file name and file type
                    filename = path.splitext(file.filename)[0]
                    file_type = path.splitext(file.filename)[1].strip('.')
                    
                    try:  # Convert to markdown
                        markdown = convert_text(file.stream.read(), 'md', file_type)
                    except RuntimeError as e:
                        if e.args[0].startswith('Invalid input format!'):
                            return 'Unsupported file type: {}'.format(file_type.upper())
                        else:
                            return 'Unknown Error'

                    # Write File to Zipfile
                    data = ZipInfo('{}.md'.format(filename))
                    data.date_time = localtime(time())[:6]
                    data.compress_type = ZIP_DEFLATED
                    zf.writestr(data, markdown)

            # Send zip file as attachment
            memory_file.seek(0)
            return send_file(memory_file, attachment_filename='Markdown.zip', as_attachment=True)
        else:
            return 'Unknown Error'


if __name__ == "__main__":
    app.run()
