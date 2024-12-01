import unittest
from unittest.mock import MagicMock, patch
from lootbox.skin_manager import SkinManager

class TestSkinManager(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

        patcher = patch("lootbox.supabase.Supabase.get_client", return_value=self.mock_client)
        self.addCleanup(patcher.stop)
        self.mock_get_client = patcher.start()

        self.skin_manager = SkinManager()

    def test_get_all_skins_success(self):
        """
        Test retrieving all skins successfully when data is available.
        """
        self.mock_client.table.return_value.select.return_value.execute.return_value.data = [
            {"id": 1, "name": "AWP Dragon Lore"},
            {"id": 2, "name": "AK-47 Supra"},
        ]

        skins = self.skin_manager.get_all_skins()

        self.assertEqual(len(skins), 2)
        self.assertEqual(skins[0]["name"], "AWP Dragon Lore")
        self.assertEqual(skins[1]["name"], "AK-47 Supra")

    def test_get_all_skins_empty(self):
        """
        Test retrieving all skins when no data is available.
        """
        self.mock_client.table.return_value.select.return_value.execute.return_value.data = None

        skins = self.skin_manager.get_all_skins()

        self.assertEqual(len(skins), 0)

    def test_get_all_skins_error(self):
        """
        Test retrieving all skins when an exception occurs.
        """
        self.mock_client.table.return_value.select.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.skin_manager.get_all_skins()

        self.assertIn("An error occurred while retrieving skins", str(context.exception))

    def test_get_available_skins_success(self):
        """
        Test retrieving available skins successfully when data is available.
        """

        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": 1, "name": "Skin1", "available": True},
            {"id": 2, "name": "Skin2", "available": True},
        ]

        skins = self.skin_manager.get_available_skins()

        self.assertEqual(len(skins), 2)
        self.assertTrue(all(skin["available"] for skin in skins))

    def test_get_available_skins_empty(self):
        """
        Test retrieving available skins when no data is available.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = None

        skins = self.skin_manager.get_available_skins()

        self.assertEqual(len(skins), 0)

    def test_get_available_skins_error(self):
        """
        Test retrieving available skins when an exception occurs.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.skin_manager.get_available_skins()

        self.assertIn("An error occurred while retrieving available skins", str(context.exception))

    def test_get_skin_by_id_success(self):
        """
        Test retrieving a skin by its ID successfully when the skin exists.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "id": "1", "name": "Skin1", "available": True
        }

        skin = self.skin_manager.get_skin_by_id("1")

        self.assertIsNotNone(skin)
        self.assertEqual(skin["id"], "1")
        self.assertEqual(skin["name"], "Skin1")
        self.assertTrue(skin["available"])

    def test_get_skin_by_id_not_found(self):
        """
        Test retrieving a skin by its ID when the skin does not exist.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None

        skin = self.skin_manager.get_skin_by_id("nonexistent_id")

        self.assertIsNone(skin)

    def test_get_skin_by_id_error(self):
        """
        Test retrieving a skin by its ID when an exception occurs.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.skin_manager.get_skin_by_id("1")

        self.assertIn("An error occurred while retrieving skin by ID", str(context.exception))

    def test_get_skin_by_name_success(self):
        """
        Test retrieving a skin by its name successfully when the skin exists.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "id": "1", "name": "Skin1", "available": True
        }

        skin = self.skin_manager.get_skin_by_name("Skin1")

        self.assertIsNotNone(skin)
        self.assertEqual(skin["name"], "Skin1")
        self.assertEqual(skin["id"], "1")
        self.assertTrue(skin["available"])

    def test_get_skin_by_name_not_found(self):
        """
        Test retrieving a skin by its name when the skin does not exist.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None

        skin = self.skin_manager.get_skin_by_name("NonexistentSkin")

        self.assertIsNone(skin)

    def test_get_skin_by_name_error(self):
        """
        Test retrieving a skin by its name when an exception occurs.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.skin_manager.get_skin_by_name("Skin1")

        self.assertIn("An error occurred while retrieving skin by name", str(context.exception))

    def test_get_filtered_skins_success(self):
        """
        Test retrieving skins with valid parameters.
        """
        self.mock_client.table.return_value.select.return_value.gte.return_value.lte.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {"id": 1, "name": "Skin1", "base_price": 50},
            {"id": 2, "name": "Skin2", "base_price": 150},
        ]

        skins = self.skin_manager.get_filtered_skins(min_price=10, max_price=200, order="asc")

        self.assertEqual(len(skins), 2)
        self.assertEqual(skins[0]["name"], "Skin1")
        self.assertEqual(skins[1]["name"], "Skin2")

    def test_get_filtered_skins_invalid_order(self):
        """
        Test retrieving skins with an invalid order argument.
        """
        with self.assertRaises(ValueError) as context:
            self.skin_manager.get_filtered_skins(order="invalid")

        self.assertIn("Invalid order value", str(context.exception))

    def test_get_filtered_skins_invalid_price_range(self):
        """
        Test retrieving skins with an invalid price range.
        """
        with self.assertRaises(ValueError) as context:
            self.skin_manager.get_filtered_skins(min_price=100, max_price=50)

        self.assertIn("max_price (50) cannot be less than min_price (100)", str(context.exception))

    def test_get_filtered_skins_with_name_filter(self):
        """
        Test retrieving skins with a name filter.
        """
        self.mock_client.table.return_value.select.return_value.gte.return_value.lte.return_value.eq.return_value.ilike.return_value.order.return_value.execute.return_value.data = [
            {"id": 3, "name": "SpecialSkin", "base_price": 300},
        ]

        skins = self.skin_manager.get_filtered_skins(min_price=100, max_price=500, name_contains="Special")

        self.assertEqual(len(skins), 1)
        self.assertEqual(skins[0]["name"], "SpecialSkin")

    def test_get_filtered_skins_empty_response(self):
        """
        Test retrieving skins when no skins match the criteria.
        """
        self.mock_client.table.return_value.select.return_value.gte.return_value.lte.return_value.eq.return_value.order.return_value.execute.return_value.data = None

        skins = self.skin_manager.get_filtered_skins(min_price=10, max_price=20)

        self.assertEqual(len(skins), 0)

    def test_get_filtered_skins_error(self):
        """
        Test retrieving skins when an exception occurs.
        """
        self.mock_client.table.return_value.select.return_value.gte.return_value.lte.return_value.eq.return_value.order.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.skin_manager.get_filtered_skins(min_price=10, max_price=100)

        self.assertIn("An error occurred while retrieving skins by price range", str(context.exception))

if __name__ == "__main__":
    unittest.main()
