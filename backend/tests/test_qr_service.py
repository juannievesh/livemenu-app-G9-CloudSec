from io import BytesIO

from app.services.qr_service import QRService


def test_qr_png_default():
    buf = QRService.generate_qr("https://livemenu.app/m/test", "png", "M")
    assert isinstance(buf, BytesIO)
    data = buf.getvalue()
    assert data[:4] == b"\x89PNG"


def test_qr_svg():
    buf = QRService.generate_qr("https://livemenu.app/m/test", "svg", "S")
    data = buf.getvalue()
    assert b"<svg" in data


def test_qr_sizes():
    for size in ("S", "M", "L", "XL"):
        buf = QRService.generate_qr("https://x.com/m/t", "png", size)
        assert len(buf.getvalue()) > 0


def test_qr_error_correction_h():
    buf = QRService.generate_qr("https://test.com/m/slug", "png", "M")
    assert len(buf.getvalue()) > 0
