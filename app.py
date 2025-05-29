from flask import Flask, request, jsonify
from flask_cors import CORS
import zipfile

app = Flask(__name__)
CORS(app)  # Sta requests toe vanaf externe websites zoals Shopify

def detect_3d_file_type(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(1024)

    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as z:
            if '3D/3dmodel.model' in z.namelist():
                return '3MF'

    if header[:5].lower() == b'solid':
        try:
            text = header.decode('utf-8')
            if 'facet normal' in text:
                return 'STL (ASCII)'
        except UnicodeDecodeError:
            pass
    elif len(header) >= 84:
        return 'STL (Binary)'

    try:
        text = header.decode('utf-8')
        if any(line.startswith(('v ', 'vt ', 'vn ', 'f ')) for line in text.splitlines()):
            return 'OBJ'
    except UnicodeDecodeError:
        pass

    try:
        text = header.decode('utf-8')
        if '<amf' in text.lower():
            return 'AMF'
    except UnicodeDecodeError:
        pass

    return 'Onbekend of niet-ondersteund bestandstype'

@app.route('/analyse', methods=['POST'])
def analyse():
    if 'file' not in request.files:
        return jsonify({'fout': 'Geen bestand meegestuurd'}), 400

    bestand = request.files['file']
    if bestand.filename == '':
        return jsonify({'fout': 'Geen bestandsnaam'}), 400

    bestand.save('tempfile')
    bestandstype = detect_3d_file_type('tempfile')
    print(f"Bestandstype gedetecteerd: {bestandstype}")
    return jsonify({'bestandstype': bestandstype})

if __name__ == '__main__':
    app.run(debug=True)
