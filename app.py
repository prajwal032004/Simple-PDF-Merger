from flask import Flask, render_template, request, send_file
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

class PdfForm(FlaskForm):
    num_pdfs = IntegerField('Number of PDFs', validators=[DataRequired(), NumberRange(min=2, max=5)])
    submit = SubmitField('Upload PDFs')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PdfForm()
    if form.validate_on_submit():
        num_pdfs = form.num_pdfs.data
        return render_template('index.html', form=form, num_pdfs=num_pdfs)
    return render_template('index.html', form=form)

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    if 'pdf' not in request.files:
        return 'No file part', 400
    
    files = request.files.getlist('pdf')
    merger = PdfMerger()
    
    for file in files:
        if file.filename == '':
            return 'No selected file', 400
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            merger.append(file_path)
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'merged.pdf')
    merger.write(output_path)
    merger.close()
    
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)