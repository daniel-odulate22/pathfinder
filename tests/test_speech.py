import unittest

from speech import build_scene_description, should_announce


class SpeechDescriptionTests(unittest.TestCase):
    def test_describes_single_detection(self):
        result = build_scene_description([{
            "class_name": "person", "position": "CENTRE",
            "attention": "HIGH", "confidence": 0.91,
        }])
        self.assertEqual(result, "I can see person in the centre.")

    def test_prioritises_high_attention(self):
        result = build_scene_description([
            {"class_name": "chair", "position": "LEFT",
             "attention": "LOW", "confidence": 0.99},
            {"class_name": "person", "position": "CENTRE",
             "attention": "HIGH", "confidence": 0.80},
        ])
        self.assertTrue(result.startswith("I can see person in the centre"))

    def test_ignores_low_confidence_detections(self):
        result = build_scene_description([{
            "class_name": "bottle", "position": "RIGHT",
            "attention": "MEDIUM", "confidence": 0.20,
        }])
        self.assertEqual(result, "")

    def test_deduplicates_same_class_and_position(self):
        result = build_scene_description([
            {"class_name": "person", "position": "CENTRE",
             "attention": "HIGH", "confidence": 0.90},
            {"class_name": "person", "position": "CENTRE",
             "attention": "HIGH", "confidence": 0.88},
        ])
        self.assertEqual(result, "I can see person in the centre.")

    def test_limits_number_of_objects(self):
        detections = [
            {"class_name": name, "position": position,
             "attention": "HIGH", "confidence": 0.9}
            for name, position in [
                ("person", "LEFT"), ("chair", "CENTRE"),
                ("bottle", "RIGHT"), ("book", "LEFT"),
            ]
        ]
        result = build_scene_description(detections, max_objects=2)
        self.assertNotIn("book", result)

    def test_announce_first_scene_after_minimum_interval(self):
        self.assertTrue(should_announce("person", "", 6, 0, 5, 12))

    def test_changed_scene_uses_short_minimum_interval(self):
        self.assertTrue(should_announce("chair", "person", 6, 0, 5, 12))

    def test_same_scene_repeats_after_repeat_interval(self):
        self.assertTrue(should_announce("person", "person", 13, 0, 5, 12))

    def test_same_scene_does_not_repeat_too_soon(self):
        self.assertFalse(should_announce("person", "person", 8, 0, 5, 12))

    def test_empty_scene_is_not_announced(self):
        self.assertFalse(should_announce("", "person", 20, 0, 5, 12))


if __name__ == "__main__":
    unittest.main()
