import unittest

from spatial import (
    get_attention_level,
    get_detection_context,
    get_horizontal_position,
    get_visual_prominence,
)


class SpatialTests(unittest.TestCase):
    def test_horizontal_position(self):
        self.assertEqual(get_horizontal_position(0, 100, 600), "LEFT")
        self.assertEqual(get_horizontal_position(250, 350, 600), "CENTRE")
        self.assertEqual(get_horizontal_position(500, 600, 600), "RIGHT")

    def test_invalid_frame_width(self):
        with self.assertRaises(ValueError):
            get_horizontal_position(0, 10, 0)

    def test_visual_prominence(self):
        # A 300 x 200 box in a 600 x 400 frame occupies 25%.
        ratio = get_visual_prominence(0, 0, 300, 200, 600, 400)
        self.assertAlmostEqual(ratio, 0.25)

    def test_boxes_are_clipped_to_frame(self):
        ratio = get_visual_prominence(-100, -100, 300, 200, 600, 400)
        self.assertAlmostEqual(ratio, 0.25)

    def test_attention_heuristic(self):
        self.assertEqual(get_attention_level("CENTRE", 0.10), "HIGH")
        self.assertEqual(get_attention_level("LEFT", 0.06), "MEDIUM")
        self.assertEqual(get_attention_level("RIGHT", 0.01), "LOW")

    def test_detection_context(self):
        context = get_detection_context(
            (200, 100, 400, 300), 600, 400
        )
        self.assertEqual(context["position"], "CENTRE")
        self.assertEqual(context["attention"], "HIGH")
        self.assertGreater(context["area_ratio"], 0)


if __name__ == "__main__":
    unittest.main()
