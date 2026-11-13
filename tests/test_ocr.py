import unittest

from ocr import format_reading, read_text

try:
    import cv2
    import numpy as np
    import rapidocr_onnxruntime  # noqa: F401
    HAS_ENGINE = True
except ImportError:
    HAS_ENGINE = False


class FormatReadingTests(unittest.TestCase):
    def test_reads_confident_lines_in_order(self):
        lines = [("FIRE EXIT", 0.99), ("PLEASE KEEP CLEAR", 0.96)]
        self.assertEqual(format_reading(lines),
                         "The text reads: FIRE EXIT, PLEASE KEEP CLEAR")

    def test_drops_low_confidence_lines(self):
        self.assertEqual(format_reading([("EXIT", 0.99), ("OWVF", 0.4)]),
                         "The text reads: EXIT")

    def test_drops_lines_the_english_voice_cannot_say(self):
        lines = [("禁止吸烟", 0.99), ("NO SMOKING", 0.97), ("((", 0.9)]
        self.assertEqual(format_reading(lines), "The text reads: NO SMOKING")

    def test_says_so_when_nothing_is_readable(self):
        self.assertEqual(format_reading([]), "I cannot read any text right now.")
        self.assertEqual(format_reading([("S", 0.3)]),
                         "I cannot read any text right now.")

    def test_limits_how_much_is_read_aloud(self):
        lines = [(f"WORD{i}", 0.99) for i in range(50)]
        self.assertEqual(format_reading(lines).count("WORD"), 30)


@unittest.skipUnless(HAS_ENGINE, "needs rapidocr-onnxruntime and OpenCV")
class ReadTextTests(unittest.TestCase):
    def test_reads_light_text_on_a_dark_sign(self):
        # Tesseract missed light-on-dark signs such as a real EXIT sign.
        sign = np.full((240, 640, 3), (40, 40, 160), np.uint8)
        cv2.putText(sign, "EXIT", (150, 170), cv2.FONT_HERSHEY_SIMPLEX, 4,
                    (255, 255, 255), 12)
        self.assertEqual(read_text(sign), "The text reads: EXIT")

    def test_blank_frame_has_no_text(self):
        blank = np.full((240, 320, 3), 128, np.uint8)
        self.assertEqual(read_text(blank), "I cannot read any text right now.")


if __name__ == "__main__":
    unittest.main()
