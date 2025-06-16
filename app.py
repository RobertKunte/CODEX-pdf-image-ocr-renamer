from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, abort
import os
import uuid
from pdf_ocr import pdf_to_images, images_to_text

app = Flask(__name__)
UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), 'uploads')

# store info about uploaded sessions
sessions = {}

@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'POST':
        file = request.files.get('pdf')
        if file and file.filename.lower().endswith('.pdf'):
            sid = str(uuid.uuid4())
            work_dir = os.path.join(UPLOAD_ROOT, sid)
            os.makedirs(work_dir, exist_ok=True)
            pdf_path = os.path.join(work_dir, file.filename)
            file.save(pdf_path)
            image_paths = pdf_to_images(pdf_path, work_dir)
            sessions[sid] = {
                'dir': work_dir,
                'images': image_paths
            }
            return redirect(url_for('preview', sid=sid))
    return render_template('upload.html')

@app.route('/preview/<sid>', methods=['GET', 'POST'])
def preview(sid):
    data = sessions.get(sid)
    if not data:
        abort(404)
    if request.method == 'POST':
        engine = request.form.get('engine', 'tesseract')
        lang = request.form.get('lang', 'deu')
        text = images_to_text(data['images'], lang=lang, engine=engine)
        text_file = os.path.join(data['dir'], 'output.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        data['text'] = text
        data['text_file'] = text_file
        return redirect(url_for('result', sid=sid))

    first_image = os.path.basename(data['images'][0])
    return render_template('preview.html', sid=sid, first_image=first_image)

@app.route('/result/<sid>')
def result(sid):
    data = sessions.get(sid)
    if not data or 'text' not in data:
        abort(404)
    return render_template('result.html', sid=sid, text=data['text'])

@app.route('/uploads/<sid>/<path:filename>')
def uploaded_file(sid, filename):
    data = sessions.get(sid)
    if not data:
        abort(404)
    return send_from_directory(data['dir'], filename)

@app.route('/download/<sid>')
def download_text(sid):
    data = sessions.get(sid)
    if not data or 'text_file' not in data:
        abort(404)
    return send_file(data['text_file'], as_attachment=True)

if __name__ == '__main__':
    os.makedirs(UPLOAD_ROOT, exist_ok=True)
    app.run(debug=True)
