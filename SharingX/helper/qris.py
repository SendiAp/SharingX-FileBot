import io
import qrcode
import urllib.request
from PIL import Image, ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

async def create_qris(qr_code: str, nominal: int) -> io.BytesIO:
    if "6304" in qr_code:
        base_qris = qr_code.split("6304")[0]
    else:
        base_qris = qr_code[:-4]

    base_qris = base_qris.replace("010211", "010212")

    str_nominal = str(nominal)
    len_nominal = f"{len(str_nominal):02d}"
    tag_54 = f"54{len_nominal}{str_nominal}"

    if "5802ID" in base_qris:
        parts = base_qris.split("5802ID")
        new_qris = parts[0] + tag_54 + "5802ID" + parts[1]
    elif "59" in base_qris:
        parts = base_qris.split("59")
        new_qris = parts[0] + tag_54 + "59" + parts[1]
    else:
        new_qris = base_qris + tag_54

    new_qris += "6304"
    
    crc = 0xFFFF
    for char in new_qris:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
            
    final_qris_string = new_qris + f"{crc:04X}"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(final_qris_string)
    qr.make(fit=True)

    COLOR_DOTS = (0, 37, 108)
    COLOR_BG = (255, 255, 255)
    COLOR_CORNER_DOT = (238, 28, 37)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(radius_ratio=0.5),
        color_mask=SolidFillColorMask(
            back_color=COLOR_BG,
            front_color=COLOR_DOTS
        )
    )

    base_img = img.convert("RGBA")
    img_w, _ = base_img.size
    draw = ImageDraw.Draw(base_img)

    matrix = qr.get_matrix()
    matrix_size = len(matrix)
    border_size = 2

    finder_positions = [
        (border_size, border_size),
        (matrix_size - 7 - border_size, border_size),
        (border_size, matrix_size - 7 - border_size)
    ]

    for fx, fy in finder_positions:
        px_start = (fx + 2) * 10
        py_start = (fy + 2) * 10
        px_end = px_start + (3 * 10)
        py_end = py_start + (3 * 10)
        draw.rectangle([px_start, py_start, px_end, py_end], fill=COLOR_CORNER_DOT)

    try:
        logo_url = "https://i.ibb.co.com/Xxk8dbsF/qris-removebg-preview.png"
        req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            logo = Image.open(io.BytesIO(response.read())).convert("RGBA")
        
        logo_size = int(img_w * 0.28)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        box_size = int(logo_size * 1.15)
        box_x = (img_w - box_size) // 2
        box_y = (img_w - box_size) // 2
        draw.rectangle([box_x, box_y, box_x + box_size, box_y + box_size], fill=COLOR_BG)
        
        pos_x = (img_w - logo_size) // 2
        pos_y = (img_w - logo_size) // 2
        base_img.paste(logo, (pos_x, pos_y), logo)
        final_img = base_img.convert("RGB")
    except Exception:
        final_img = base_img.convert("RGB")

    bio = io.BytesIO()
    bio.name = "qris_dinamis.png"
    final_img.save(bio, "PNG")
    bio.seek(0)
    return bio
