import io
import qrcode
import urllib.request

from PIL import Image, ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer


def parse_tlv(data):
    result = []
    i = 0

    while i + 4 <= len(data):
        tag = data[i:i + 2]
        try:
            length = int(data[i + 2:i + 4])
        except ValueError:
            break

        value_start = i + 4
        value_end = value_start + length

        if value_end > len(data):
            break

        result.append((tag, data[value_start:value_end]))
        i = value_end

    return result


def build_tlv(items):
    return "".join(
        f"{tag}{len(value):02d}{value}"
        for tag, value in items
    )


async def create_qris(qr_code: str, nominal: int) -> io.BytesIO:

    qr_code = qr_code.strip()

    if "6304" in qr_code:
        qr_code = qr_code.split("6304", 1)[0]

    items = parse_tlv(qr_code)

    if not items:
        raise ValueError("Format QRIS tidak valid")

    new_items = []

    for tag, value in items:

        if tag == "01":
            value = "12"

        if tag == "54":
            continue

        new_items.append(
            (tag, value)
        )

    amount = str(int(nominal))

    final_items = []

    inserted_amount = False

    for tag, value in new_items:

        if tag == "58" and not inserted_amount:

            final_items.append(
                ("54", amount)
            )

            inserted_amount = True

        final_items.append(
            (tag, value)
        )

    if not inserted_amount:
        final_items.append(
            ("54", amount)
        )

    base_qris = build_tlv(
        final_items
    )

    crc_data = base_qris + "6304"

    crc = 0xFFFF

    for char in crc_data:
        crc ^= ord(char) << 8

        for _ in range(8):

            if crc & 0x8000:
                crc = (
                    (crc << 1)
                    ^ 0x1021
                )
            else:
                crc <<= 1

            crc &= 0xFFFF

    final_qris_string = (
        crc_data
        + f"{crc:04X}"
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(
        final_qris_string
    )

    qr.make(
        fit=True
    )

    COLOR_DOTS = (
        0,
        37,
        108
    )

    COLOR_BG = (
        255,
        255,
        255
    )

    COLOR_CORNER_DOT = (
        238,
        28,
        37
    )

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(
            radius_ratio=0.35
        ),
        color_mask=SolidFillColorMask(
            back_color=COLOR_BG,
            front_color=COLOR_DOTS
        )
    )

    base_img = img.convert(
        "RGBA"
    )

    img_w, img_h = base_img.size

    draw = ImageDraw.Draw(
        base_img
    )

    matrix = qr.get_matrix()
    matrix_size = len(matrix)
    border_size = 4
    module_size = 10

    finder_positions = [
        (
            border_size,
            border_size
        ),
        (
            matrix_size - 7 - border_size,
            border_size
        ),
        (
            border_size,
            matrix_size - 7 - border_size
        )
    ]

    for fx, fy in finder_positions:

        px_start = (
            fx + 2
        ) * module_size

        py_start = (
            fy + 2
        ) * module_size

        px_end = (
            px_start
            + (3 * module_size)
        )

        py_end = (
            py_start
            + (3 * module_size)
        )

        draw.rectangle(
            [
                px_start,
                py_start,
                px_end,
                py_end
            ],
            fill=COLOR_CORNER_DOT
        )

    try:

        logo_url = (
            "https://i.ibb.co.com/"
            "Xxk8dbsF/"
            "qris-removebg-preview.png"
        )

        req = urllib.request.Request(
            logo_url,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=10
        ) as response:

            logo = Image.open(
                io.BytesIO(
                    response.read()
                )
            ).convert(
                "RGBA"
            )

        logo_size = int(
            img_w * 0.18
        )

        logo = logo.resize(
            (
                logo_size,
                logo_size
            ),
            Image.Resampling.LANCZOS
        )

        box_size = int(
            logo_size * 1.12
        )

        box_x = (
            img_w - box_size
        ) // 2

        box_y = (
            img_h - box_size
        ) // 2

        draw.rounded_rectangle(
            [
                box_x,
                box_y,
                box_x + box_size,
                box_y + box_size
            ],
            radius=8,
            fill=COLOR_BG
        )

        pos_x = (
            img_w - logo_size
        ) // 2

        pos_y = (
            img_h - logo_size
        ) // 2

        base_img.paste(
            logo,
            (
                pos_x,
                pos_y
            ),
            logo
        )

        final_img = base_img.convert(
            "RGB"
        )

    except Exception:

        final_img = base_img.convert(
            "RGB"
        )

    bio = io.BytesIO()

    bio.name = (
        "qris_dinamis.png"
    )

    final_img.save(
        bio,
        "PNG"
    )

    bio.seek(0)

    return bio
