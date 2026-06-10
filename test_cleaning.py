import unittest
import json
import os
from cleaning import mask_email, clean_data


class TestMaskEmail(unittest.TestCase):
    def test_mask_email_simple(self):
        """Test basic email masking"""
        result = mask_email("vana@gmail.com")
        self.assertEqual(result, "v***@gmail.com")

    def test_mask_email_longer_username(self):
        """Test masking with longer username"""
        result = mask_email("john@example.com")
        self.assertEqual(result, "j***@example.com")

    def test_mask_email_with_subdomain(self):
        """Test masking with subdomain"""
        result = mask_email("user@mail.co.uk")
        self.assertEqual(result, "u***@mail.co.uk")


class TestCleanData(unittest.TestCase):
    def setUp(self):
        """Create a test input file"""
        self.test_input = "test_toxic_sample.json"
        self.test_output = "test_sanitized_sample.json"

        test_data = [
            {"id": "A001", "name": "User A", "email": "usera@test.com", "product": "Item1", "price": 100, "category": "cat1"},
            {"id": "A001", "name": "User A", "email": "usera@test.com", "product": "Item1", "price": 100, "category": "cat1"},  # Duplicate
            {"id": "A002", "name": "User B", "email": "userb@test.com", "product": "Item2", "price": 99999, "category": "cat2"},  # Outlier
            {"id": "A003", "name": "User C", "email": "userc@test.com", "product": "Item3", "price": -50, "category": "cat3"},  # Negative price
            {"id": "A004", "name": "User D", "email": "userd@test.com", "product": "Item4", "price": 500, "category": "cat4"}  # Valid
        ]

        with open(self.test_input, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_input):
            os.remove(self.test_input)
        if os.path.exists(self.test_output):
            os.remove(self.test_output)

    def test_deduplication(self):
        """Test that duplicates are removed"""
        clean_data(self.test_input, self.test_output)

        with open(self.test_output, 'r', encoding='utf-8') as f:
            result = json.load(f)

        # Should have 2 records (A001 deduplicated, A002 outlier removed, A003 negative removed)
        self.assertEqual(len(result), 2)
        ids = [item['id'] for item in result]
        # No duplicates
        self.assertEqual(len(ids), len(set(ids)))

    def test_outlier_removal(self):
        """Test that outliers (price > 5000) are removed"""
        clean_data(self.test_input, self.test_output)

        with open(self.test_output, 'r', encoding='utf-8') as f:
            result = json.load(f)

        for item in result:
            self.assertLessEqual(item['price'], 5000)

    def test_negative_price_removal(self):
        """Test that negative prices are removed"""
        clean_data(self.test_input, self.test_output)

        with open(self.test_output, 'r', encoding='utf-8') as f:
            result = json.load(f)

        for item in result:
            self.assertGreaterEqual(item['price'], 0)

    def test_name_field_removed(self):
        """Test that name field is removed"""
        clean_data(self.test_input, self.test_output)

        with open(self.test_output, 'r', encoding='utf-8') as f:
            result = json.load(f)

        for item in result:
            self.assertNotIn('name', item)

    def test_email_masked(self):
        """Test that email is masked"""
        clean_data(self.test_input, self.test_output)

        with open(self.test_output, 'r', encoding='utf-8') as f:
            result = json.load(f)

        for item in result:
            email = item['email']
            # Should have format: x***@domain
            self.assertIn("***@", email)
            # First character should not be repeated (masking worked)
            self.assertFalse(email.startswith(email[0] * 4))


if __name__ == '__main__':
    unittest.main()
