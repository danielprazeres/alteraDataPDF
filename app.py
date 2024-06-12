import fitz  # PyMuPDF
import os
import logging
import zipstream
from flask import Flask, request, send_from_directory, jsonify, Response
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def replace_date_in_pdf(file_path, old_dates, new_date):
    logging.info(f'Replacing dates in file: {file_path}')
    try:
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
        logging.info(f'Processed file saved to: {processed_path}')
        return processed_path
    except Exception as e:
        logging.error(f'Error processing file: {e}')
        raise

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'files' not in request.files:
            return jsonify(error='No file part'), 400
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify(error='No selected files'), 400
        
        old_dates_str = request.form['old_dates']
        new_date = request.form['new_date']

        # Garantir que a entrada de datas antigas seja sempre tratada como uma lista
        old_dates = [date.strip() for date in old_dates_str.split(',') if date.strip()]

        if not old_dates or not new_date:
            return jsonify(error='Invalid date input'), 400

        processed_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                logging.info(f'File uploaded to: {file_path}')

                try:
                    processed_file_path = replace_date_in_pdf(file_path, old_dates, new_date)
                    processed_files.append(processed_file_path)
                except Exception as e:
                    logging.error(f'Error in processing: {e}')
                    return jsonify(error='Internal Server Error'), 500

        # Create a zip file with all processed PDFs
        z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
        for file_path in processed_files:
            z.write(file_path, os.path.basename(file_path))

        response = Response(z, mimetype='application/zip')
        response.headers['Content-Disposition'] = 'attachment; filename=processed_files.zip'
        return response

    return '''
    <!doctype html>
    <title>Replace Dates in PDF</title>
    <h1>Upload PDF Files</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=files multiple>
      <input type=text name=old_dates placeholder="Old dates, e.g., 23/11/2023,26/11/2023">
      <input type=text name=new_date placeholder="New date, e.g., 10/06/2024">
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    app.run(debug=True)
