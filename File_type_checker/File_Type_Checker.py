def detect_3d_file_type(file_path):
    import zipfile
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
        if '<amf' in text.lower():
            return 'AMF'
    except UnicodeDecodeError:
        pass

    return 'Onbekend of niet-ondersteund bestandstype'


# === Hoofdprogramma ===
if __name__ == "__main__":
    bestand = input("📂 Geef het pad naar een 3D-bestand: ")
    try:
        type_bestand = detect_3d_file_type(bestand)
        print(f"🔍 Detecteerde bestandstype: {type_bestand}")
    except FileNotFoundError:
        print("❌ Bestand niet gevonden. Controleer het pad.")
    except Exception as e:
        print(f"⚠️ Fout bij het verwerken van het bestand: {e}")
