from flask import Flask, render_template, request, send_from_directory
import os
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from pathlib import Path
#import docx
from pdf2docx import parse

def compress_pdf(input_pdf, output_path):
    output_pdf = PdfFileWriter()

    # Apply compression techniques to each page
    for page in input_pdf.pages:
        page.compressContentStreams()
        output_pdf.addPage(page)

    # Write the compressed PDF to the output file
    with open(output_path, 'wb') as output_file:
        output_pdf.write(output_file)
        
def merge_pdfs(files, output_path):
    merger = PdfFileMerger()
    for file in files:
        input_pdf = PdfFileReader(file)
        merger.append(input_pdf)
    with open(output_path, 'wb') as output_file:
        merger.write(output_file)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/root/py2pdf/data/'


# Define the route for the home page
@app.route('/')
def home():
    return render_template('home.html', title='Home')

# Define the route for the PDF splitter page
@app.route('/split', methods=['GET', 'POST'])
def split():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']
        
        # Create a new directory for the output files
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Open the PDF file and split it into pages
        input_pdf = PdfFileReader(file)
        num_pages = input_pdf.getNumPages()
        for i in range(num_pages):
            # Create a new PDF file for the current page
            output_pdf = PdfFileWriter()
            output_pdf.addPage(input_pdf.getPage(i))
            
            # Save the new PDF file with a unique name
            #output_file_path = os.path.join(output_dir, f'page_{i+1}.pdf')
            #with open(output_file_path, 'wb') as output_file:
            #    output_pdf.write(output_file)
            compressed_output_path = os.path.join(output_dir, f'page_{i+1}.pdf')
            compress_pdf(output_pdf, compressed_output_path)
        
        
        # Redirect the user to the output page
        return render_template('output.html', title='Split PDF', num_pages=num_pages)
    
    # If the request method is GET, show the upload form
    return render_template('split.html', title='Split PDF')

# Define the route for serving the output files
@app.route('/output/<filename>')
def output(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], f'output/{filename}')

# Define the route for the PDF compression page
@app.route('/compress', methods=['GET', 'POST'])
def compress():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']
        
        # Create a new directory for the output file
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Compress the PDF file
        input_pdf = PdfFileReader(file)
        compressed_output_path = os.path.join(output_dir, f'{file.filename}_compressed.pdf')
        compress_pdf(input_pdf, compressed_output_path)
        
        # Redirect the user to download the compressed file
        return send_from_directory(app.config['UPLOAD_FOLDER'], f'output/{file.filename}_compressed.pdf', as_attachment=True)
    
    # If the request method is GET, show the upload form
    return render_template('compress.html', title='Compress PDF')

# Define the route for the PDF merge page
@app.route('/merge', methods=['GET', 'POST'])
def merge():
    if request.method == 'POST':
        # Get the uploaded files
        files = request.files.getlist('file')
        
        # Create a new directory for the output file
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Merge the PDF files
        merged_output_path = os.path.join(output_dir, 'merged.pdf')
        merge_pdfs(files, merged_output_path)
        
        # Redirect the user to download the merged file
        return send_from_directory(app.config['UPLOAD_FOLDER'], 'output/merged.pdf', as_attachment=True)
    
    # If the request method is GET, show the upload form
    return render_template('merge.html', title='Merge PDF')

# Define the route for the PDF to Word conversion page
@app.route('/pdf2word', methods=['GET', 'POST'])

def pdf2word():
    if request.method == 'POST':
        # Get the uploaded file
        pdf_file = request.files['file']
        
        #Create upload directory
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'upload')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the uploaded file in upload dir
        pdf_file_name = pdf_file.filename
        pdf_file_path = os.path.join(upload_dir, pdf_file_name)
        pdf_file.save(pdf_file_path)
        
        # Create Output Directory
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # declare files in Output dir
        docx_file_path = os.path.join(output_dir, os.path.splitext(pdf_file_name)[0] + '.docx')
        txt_file_path = os.path.join(output_dir, os.path.splitext(pdf_file_name)[0] + '.txt')
        print("printing : ", docx_file_path)
        
        # Specify the output Word document path
        word_file_path = docx_file_path
        
        parse(pdf_file_path, docx_file_path)
        # Print a message to indicate that the conversion is complete
        print('PDF file converted to Word document successfully.')
            
        # Redirect the user to download the Word file
        return send_from_directory(output_dir, os.path.basename(docx_file_path), as_attachment=True)
    
    # If the request method is GET, show the upload form
    return render_template('pdf2word.html', title='PDF to Word')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
