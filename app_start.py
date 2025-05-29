from flask import Flask, request, jsonify, send_from_directory
import zipfile
import os

app = Flask(__name__, static_folder='static')

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

@app.route('/detect', methods=['POST'])
def detect_file_type():
    if 'file' not in request.files:
        return jsonify({'error': 'Geen bestand ontvangen'}), 400

    file = request.files['file']
    filepath = f'/tmp/{file.filename}'
    file.save(filepath)

    result = detect_3d_file_type(filepath)
    os.remove(filepath)  # schoonmaken
    return jsonify({'bestandstype': result})

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='https://threed-website-idee.onrender.com', port=5000)