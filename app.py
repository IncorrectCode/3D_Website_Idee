from flask import Flask, request, jsonify
from flask_cors import CORS
import zipfile
import os
import trimesh

app = Flask(__name__)
CORS(app)  # Sta requests toe vanaf externe websites zoals Shopify

def detect_3d_file_type(file_path):
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as z:
            if '3D/3dmodel.model' in z.namelist():
                return '3MF'

    with open(file_path, 'rb') as f:
        header = f.read(1024)

    # ASCII STL check
    if header[:5].lower() == b'solid':
        try:
            text = header.decode('utf-8', errors='ignore')
            if 'facet normal' in text:
                return 'STL (ASCII)'
        except UnicodeDecodeError:
            pass

    # Binaire STL check: bestandsgrootte check
    filesize = os.path.getsize(file_path)
    if filesize > 84:
        with open(file_path, 'rb') as f:
            f.seek(80)
            tri_count_bytes = f.read(4)
            if len(tri_count_bytes) == 4:
                import struct
                tri_count = struct.unpack('<I', tri_count_bytes)[0]
                expected_size = 84 + tri_count * 50
                if filesize == expected_size:
                    return 'STL'

    # OBJ check
    try:
        text = header.decode('utf-8', errors='ignore')
        for line in text.splitlines():
            if line.startswith(('v ', 'vt ', 'vn ', 'f ')):
                return 'OBJ'
    except UnicodeDecodeError:
        pass

    # AMF check
    try:
        text = header.decode('utf-8', errors='ignore')
        if '<amf' in text.lower():
            return 'AMF'
    except UnicodeDecodeError:
        pass

    return 'Onbekend of niet-ondersteund bestandstype'

def schat_materiaal_en_tijd(pad, infill=0.2, dichtheid=1.24, snelheid_cm3_per_min=0.2):
    try:
        mesh = trimesh.load(pad)
        volume_mm3 = mesh.volume
        volume_cm3 = volume_mm3 / 1000  # van mm³ naar cm³

        effectief_volume = volume_cm3 * infill
        gewicht_gram = effectief_volume * dichtheid
        tijd_minuten = effectief_volume / snelheid_cm3_per_min

        return {
            'volume_cm3': round(volume_cm3, 2),
            'gewicht_gram': round(gewicht_gram, 2),
            'geschatte_printtijd_min': round(tijd_minuten)
        }
    except Exception as e:
        return {'fout': f'Fout bij analyse: {str(e)}'}

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

    resultaat = {'bestandstype': bestandstype}

    if bestandstype in ['STL', 'STL (ASCII)', 'OBJ']:
        extra = schat_materiaal_en_tijd('tempfile')
        resultaat.update(extra)

    # Verwijder tijdelijk bestand
    try:
        os.remove('tempfile')
    except:
        pass

    return jsonify(resultaat)

if __name__ == '__main__':
    app.run(debug=True)
