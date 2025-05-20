import os, json, hashlib, qrcode
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, request, send_file, abort

app = Flask(__name__)

panundaan = 'hasil'
rupi = 'assets'
if not os.path.exists(panundaan):
    os.makedirs(panundaan)
if not os.path.exists(rupi):
    os.makedirs(rupi)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Part Nyieun Variabel
    ngaran = request.form['ngaran']
    boga = request.form['boga']
    murag = request.form['borojol']
    reureuh = int(request.form['reureuh'])
    
    # Parse and format the dates
    borojol = datetime.strptime(murag, "%Y-%m-%d").date()
    borojol_formatted = borojol.strftime("%d %B %Y")  # Format as 'DD Month YYYY'
    
    ayeuna = datetime.today().date()
    ayeuna_formatted = ayeuna.strftime("%d %B %Y")  # Format as 'DD Month YYYY'
    
    # Calculate age
    yuswa = str(ayeuna.year - borojol.year - ((ayeuna.month, ayeuna.day) < (borojol.month, borojol.day)))
    
    # Determine the date based on reureuh input
    ngaso = {
        1: ayeuna,
        2: ayeuna + timedelta(days=1),
        3: ayeuna + timedelta(days=2)
    }.get(reureuh, ayeuna)
    
    ngaso_formatted = ngaso.strftime("%d %B %Y")  # Format as 'DD Month YYYY'

    # Part Nyeting Gambar
    image_path = 'blank-sik.jpg'
    alas = os.path.join(rupi, image_path)
    image = Image.open(alas)
    draw = ImageDraw.Draw(image)

    font_size = 22
    aksara = os.path.join(rupi, "Nunito-SemiBold.ttf")
    font = ImageFont.truetype(aksara, font_size)
    text_color = (40, 40, 40, 255)

    texts = [
        (ngaran, (253, 238)),  # Ngaran Maneh
        (boga, (760, 238)),  # Memes
        (borojol_formatted, (253, 303)),  # Titimangsa Borojol
        (yuswa, (760, 303)),  # Yuswa Anjen
        (ayeuna_formatted, (335, 488)),  # Tanggal Nyien
        (ayeuna_formatted + " hingga " + ngaso_formatted, (56, 748)),  # Tanggal Pere
        ("17/IX/2023", (956, 998)),  # Wilangan Hade
    ]

    for text, position in texts[:-1]: 
        draw.text(position, text, font=font, fill=text_color)

    different_font_size = 22
    panyerat = os.path.join(rupi, "Nunito.ttf")
    different_font = ImageFont.truetype(panyerat, different_font_size)
    different_text_color = (40, 40, 40, 255)

    draw.text(texts[-1][1], texts[-1][0], font=different_font, fill=different_text_color)

    # Part Nyieun Kode Hade
    inisial = hashlib.md5()
    puyeng = ngaran + borojol_formatted + ayeuna_formatted
    inisial.update(puyeng.encode('utf-8'))
    hash_value = inisial.hexdigest()

    ling = 'http://8.215.77.47:82/validasi/rekomendasi-istirahat/'+hash_value
    
    # Nyimpen Data
    uesina = {
        "pasien": 0, 
        "ingfo": {
            'AngkaHade': hash_value,
            'Ngaran': ngaran,
            'Borojol': borojol_formatted,  
            'Bobogaan': boga,
            'Dokter': 'Rini Aprilia',
            'TglKonsul': ayeuna_formatted,
            'Pere': ayeuna_formatted, 
            'Asup': ngaso_formatted,
            'Lingna': ling
        }
    }
    
    if os.path.exists('pasien.json'):
        with open('pasien.json', 'r') as p:
            try:
                data = json.load(p)
            except json.JSONDecodeError:
                data = {"NuGering": []}  
    else:
        data = {"NuGering": []}

    uesina["pasien"] = len(data["NuGering"]) + 1
    data["NuGering"].append(uesina)
    with open('pasien.json', 'w') as p:
        json.dump(data, p, indent=4)

    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=4,
    )

    qr.add_data(ling)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_code_path = f"{hash_value}.png"
    qrna = os.path.join(panundaan, qr_code_path)
    img.save(qrna)

    overlay_image = Image.open(qrna)
    new_size = (90, 90)  
    overlay_image = overlay_image.resize(new_size, Image.LANCZOS)
    overlay_position = (965, 1090)  
    image.paste(overlay_image, overlay_position)

    # Part Ngasave Gambar
    output_path = f"{hash_value}-output_image.jpg"
    anuasli = os.path.join(panundaan, output_path)
    image.save(anuasli)

    luarpdf = f"{hash_value}.pdf"
    jantenpdf = os.path.join(panundaan, luarpdf)

    with Image.open(anuasli) as img:
        img = img.convert('RGB')
        img.save(jantenpdf)

    hapus = os.listdir(panundaan)
    for h in hapus:
        if h.endswith(".jpg") or h.endswith(".png"):
            os.remove(os.path.join(panundaan, h))

    return send_file(jantenpdf, as_attachment=True)

@app.route('/validasi/rekomendasi-istirahat/<angka_hade>', methods=['GET'])
def validate(angka_hade):
    with open('pasien.json', 'r') as file:
        data = json.load(file)

    result = None
    for item in data.get('NuGering', []):  
        if item['ingfo'].get('AngkaHade') == angka_hade:  
            result = item 
            break  

    return render_template('validation.html', data=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='82')