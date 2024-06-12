import fitz  # PyMuPDF
import os
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def replace_date_in_pdf(file_path, old_dates, new_date):
    doc = fitz.open(file_path)
    for page in doc:
        for old_date in old_dates:
            text_instances = page.search_for(old_date)
            for inst in text_instances:
                rect = fitz.Rect(inst)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                page.insert_text((rect.x0 + 2, rect.y1 - 14), new_date, fontsize=12, color=(0, 0, 0))
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], os.path.basename(file_path))
    doc.save(processed_path)
    doc.close()
    return processed_path

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            old_dates = request.form['old_dates'].split(',')
            new_date = request.form['new_date']
            
            processed_file_path = replace_date_in_pdf(file_path, old_dates, new_date)
            
            return send_from_directory(app.config['PROCESSED_FOLDER'], os.path.basename(processed_file_path), as_attachment=True)
    return '''
    <!doctype html>
    <title>Replace Dates in PDF</title>
    <h1>Upload PDF File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=text name=old_dates placeholder="Old dates, e.g., 23/11/2023,26/11/2023">
      <input type=text name=new_date placeholder="New date, e.g., 10/06/2024">
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    app.run(debug=True)
