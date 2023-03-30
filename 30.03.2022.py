from flask import Flask, request, render_template, send_from_directory
from pdf2docx import parse
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/root/py2pdf/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    pdf_file = request.files['pdf-file']
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'upload')
    os.makedirs(upload_dir, exist_ok=True)
    pdf_file_name = pdf_file.filename
    pdf_file_path = os.path.join(upload_dir, pdf_file_name)
    pdf_file.save(pdf_file_path)

    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
    os.makedirs(output_dir, exist_ok=True)
    docx_file_path = os.path.join(output_dir, os.path.splitext(pdf_file_name)[0] + '.docx')

    parse(pdf_file_path, docx_file_path, retain_layout=True, start=0, end=None)

    # Send the converted file to the browser
    return send_from_directory(output_dir, os.path.basename(docx_file_path))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
