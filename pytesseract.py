from flask import Flask, request, render_template, send_from_directory
from pdf2image import convert_from_path
import pytesseract
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/root/py2pdf/'

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


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
    txt_file_path = os.path.join(output_dir, os.path.splitext(pdf_file_name)[0] + '.txt')

    # Convert PDF to images
    pages = convert_from_path(pdf_file_path, 500)

    # Extract text from each image using OCR
    text = ''
    for page in pages:
        text += pytesseract.image_to_string(page)

    # Save extracted text to a text file
    with open(txt_file_path, 'w') as f:
        f.write(text)

    # Send the text file to the browser
    return send_from_directory(output_dir, os.path.basename(txt_file_path))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
