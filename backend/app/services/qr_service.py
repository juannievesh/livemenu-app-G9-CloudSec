from io import BytesIO

import qrcode
import qrcode.image.svg


class QRService:
    @staticmethod
    def generate_qr(url: str, format_type: str = 'png', size: str = 'M') -> BytesIO:
        """
        Genera un código QR en formato PNG o SVG.
        Aplica nivel de corrección H (30%) obligatorio para entornos comerciales.
        """
        sizes = {'S': 5, 'M': 10, 'L': 15, 'XL': 20}
        box_size = sizes.get(size.upper(), 10)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img_io = BytesIO()

        if format_type.lower() == 'svg':
            factory = qrcode.image.svg.SvgImage
            img = qr.make_image(image_factory=factory)
            img.save(img_io)
        else:
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(img_io, format='PNG')

        img_io.seek(0)
        return img_io
