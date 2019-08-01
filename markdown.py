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
        return render_template('index.html')
    elif request.method == 'POST':
        print(request.__dict__)
        file_list = request.files.getlist('files[]')

        # Return single file
        if len(file_list) == 0:
            print('No FILE')
            return render_template('index.html', error='No files selected')
        elif len(file_list) == 1:
            file = file_list[0]

            # Get file name and type
            filename = path.splitext(file.filename)[0]
            file_type = path.splitext(file.filename)[1].strip('.')

            try:  # Convert to markdown
                markdown = convert_text(file.stream.read(), 'md', file_type)
            except RuntimeError as e:
                if e.args[0].startswith('Invalid input format!'):
                    return render_template('index.html', unsupported=file_type.upper())
                else:
                    return render_template('index.html', error=True)

            # Send markdown file as attachment
            return Response(markdown, mimetype='text/markdown',
                            headers={'Content-Disposition': 'attachment;filename={}.md'.format(filename)})

        # Return zip file
        elif len(file_list) > 1:
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
                            return render_template('index.html', unsupported=file_type.upper())
                        else:
                            return render_template('index.html', error=True)

                    # Write File to Zipfile
                    data = ZipInfo('{}.md'.format(filename))
                    data.date_time = localtime(time())[:6]
                    data.compress_type = ZIP_DEFLATED
                    zf.writestr(data, markdown)

            # Send zip file as attachment
            memory_file.seek(0)
            return send_file(memory_file, attachment_filename='results.zip', as_attachment=True)
        else:
            return render_template('index.html')


if __name__ == "__main__":
    app.run()
