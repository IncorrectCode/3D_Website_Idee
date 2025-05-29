import zipfile

def detect_3d_file_type(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(1024)

    # Check 3MF: ZIP-bestand met specifieke inhoud
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as z:
            if '3D/3dmodel.model' in z.namelist():
                return '3MF'

    # Check STL (ASCII of binair)
    if header[:5].lower() == b'solid':
        try:
            text = header.decode('utf-8')
            if 'facet normal' in text:
                return 'STL (ASCII)'
        except UnicodeDecodeError:
            pass
    elif len(header) >= 84:
        # Binair STL bevat 80-byte header + 4-byte integer (triangle count)
        return 'STL (Binary)'

    # Check OBJ
    try:
        text = header.decode('utf-8')
        if any(line.startswith(('v ', 'vt ', 'vn ', 'f ')) for line in text.splitlines()):
            return 'OBJ'
    except UnicodeDecodeError:
        pass

    # Check AMF (XML-based)
    try:
        text = header.decode('utf-8')
        if '<amf' in text.lower():
            return 'AMF'
    except UnicodeDecodeError:
        pass

    return 'Onbekend of niet-ondersteund bestandstype'

bestand = 'voorbeeld.stl'
type_bestand = detect_3d_file_type(bestand)
print(f'Detecteerde bestandstype: {type_bestand}')
