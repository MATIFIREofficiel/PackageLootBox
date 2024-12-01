import unittest
from unittest.mock import MagicMock, patch
from lootbox.lootbox_manager import LootboxManager


class TestLootboxManager(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_skin_manager = MagicMock()

        patcher_client = patch("lootbox.supabase.Supabase.get_client", return_value=self.mock_client)
        patcher_skin_manager = patch("lootbox.lootbox_manager.SkinManager", return_value=self.mock_skin_manager)
        self.addCleanup(patcher_client.stop)
        self.addCleanup(patcher_skin_manager.stop)
        self.mock_get_client = patcher_client.start()
        self.mock_skin_manager_class = patcher_skin_manager.start()

        self.lootbox_manager = LootboxManager()

    def test_get_lootbox_id_by_name_success(self):
        """
        Test retrieving a lootbox ID by its name successfully.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "lootbox_id": 123
        }

        lootbox_id = self.lootbox_manager.get_lootbox_id_by_name("TestLootbox")

        self.assertEqual(lootbox_id, 123)

    def test_get_lootbox_id_by_name_not_found(self):
        """
        Test retrieving a lootbox ID by its name when the lootbox does not exist.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None

        lootbox_id = self.lootbox_manager.get_lootbox_id_by_name("NonexistentLootbox")

        self.assertIsNone(lootbox_id)

    def test_get_lootbox_id_by_name_error(self):
        """
        Test retrieving a lootbox ID by its name when an exception occurs.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.get_lootbox_id_by_name("TestLootbox")

        self.assertIn("An error occurred while retrieving lootbox ID for 'TestLootbox'", str(context.exception))

    def test_get_lootbox_contents_success(self):
        """
        Test retrieving lootbox contents successfully.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"skin_id": "1"}, {"skin_id": "2"}
        ]
        self.mock_skin_manager.get_skin_by_id.side_effect = lambda skin_id: {"id": skin_id, "name": f"Skin{skin_id}"}

        contents = self.lootbox_manager.get_lootbox_contents("TestLootbox")

        self.assertEqual(len(contents), 2)
        self.assertEqual(contents[0]["name"], "Skin1")
        self.assertEqual(contents[1]["name"], "Skin2")

    def test_get_lootbox_contents_empty(self):
        """
        Test retrieving lootbox contents when no skins are associated with the lootbox.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = None

        contents = self.lootbox_manager.get_lootbox_contents("EmptyLootbox")

        self.assertEqual(len(contents), 0)

    def test_get_lootbox_contents_not_found(self):
        """
        Test retrieving lootbox contents when the lootbox is not found.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=None)

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.get_lootbox_contents("NonexistentLootbox")

        self.assertIn("Lootbox 'NonexistentLootbox' not found", str(context.exception))

    def test_create_success(self):
        """
        Test creating a lootbox successfully.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = None
        self.mock_client.table.return_value.insert.return_value.execute.return_value.data = [{"lootbox_id": 123}]

        self.lootbox_manager.create(name="NewLootbox", description="A new lootbox")

        self.mock_client.table.return_value.insert.assert_called_once_with({
            "name": "NewLootbox",
            "description": "A new lootbox",
        })

    def test_create_name_or_description_empty(self):
        """
        Test creating a lootbox with empty name or description.
        """
        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.create(name="", description="Valid description")
        self.assertIn("Name and description are required and cannot be empty", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.create(name="Valid name", description="")
        self.assertIn("Name and description are required and cannot be empty", str(context.exception))

    def test_create_duplicate_lootbox(self):
        """
        Test creating a lootbox when it already exists.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"lootbox_id": 123}]

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.create(name="DuplicateLootbox", description="Duplicate description")

        self.assertIn("A lootbox with the name 'DuplicateLootbox' already exists", str(context.exception))

    def test_create_unexpected_response(self):
        """
        Test creating a lootbox with an unexpected response format.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = None
        self.mock_client.table.return_value.insert.return_value.execute.return_value.data = None

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.create(name="NewLootbox", description="A new lootbox")

        self.assertIn("Unexpected response format from Supabase", str(context.exception))

    def test_create_exception_handling(self):
        """
        Test creating a lootbox when an exception occurs.
        """
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.create(name="ErrorLootbox", description="Error description")

        self.assertIn("An error occurred while creating the lootbox 'ErrorLootbox'", str(context.exception))

    def test_update_success(self):
        """
        Test updating a lootbox successfully by adding new skins.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"skin_id": "1"}
        ]

        self.mock_skin_manager.get_skin_by_name.side_effect = lambda name: {
            "Skin2": {"id": "2", "name": "Skin2"},
            "Skin3": {"id": "3", "name": "Skin3"},
        }.get(name, None)
        self.mock_skin_manager.get_skin_by_id.side_effect = lambda skin_id: {
            "1": {"id": "1", "name": "Skin1"},
            "2": {"id": "2", "name": "Skin2"},
            "3": {"id": "3", "name": "Skin3"},
        }.get(skin_id, None)

        self.mock_client.table.return_value.insert.return_value.execute.return_value.data = [{"success": True}]

        self.lootbox_manager.get_lootbox_contents = MagicMock(return_value=[
            {"id": "1", "name": "Skin1"},
            {"id": "2", "name": "Skin2"},
            {"id": "3", "name": "Skin3"},
        ])

        updated_contents = self.lootbox_manager.update("TestLootbox", ["Skin2", "Skin3"])

        self.assertIn({"id": "2", "name": "Skin2"}, updated_contents)
        self.assertIn({"id": "3", "name": "Skin3"}, updated_contents)

    def test_update_duplicates(self):
        """
        Test updating a lootbox with duplicate skins.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"skin_id": "1"}
        ]

        self.mock_skin_manager.get_skin_by_name.side_effect = lambda name: {
            "Skin1": {"id": "1", "name": "Skin1"}
        }.get(name, None)
        self.mock_skin_manager.get_skin_by_id.side_effect = lambda skin_id: {
            "1": {"id": "1", "name": "Skin1"}
        }.get(skin_id, None)

        self.lootbox_manager.get_lootbox_contents = MagicMock(return_value=[
            {"id": "1", "name": "Skin1"}
        ])

        updated_contents = self.lootbox_manager.update("TestLootbox", ["Skin1"])

        self.assertEqual(len(updated_contents), 1)
        self.assertEqual(updated_contents[0]["id"], "1")
        self.assertEqual(updated_contents[0]["name"], "Skin1")

    def test_update_lootbox_not_found(self):
        """
        Test updating a lootbox that does not exist.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=None)

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.update("NonexistentLootbox", ["Skin1", "Skin2"])

        self.assertIn("Lootbox 'NonexistentLootbox' not found", str(context.exception))

    def test_update_error(self):
        """
        Test updating a lootbox when an exception occurs.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.update("TestLootbox", ["Skin1", "Skin2"])

        self.assertIn("An error occurred while updating lootbox 'TestLootbox'", str(context.exception))

    def test_delete_success(self):
        """
        Test deleting a lootbox and its associated skins successfully.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)
        self.mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{"success": True}]

        self.lootbox_manager.delete("TestLootbox")

        self.mock_client.table.return_value.delete.assert_any_call()
        self.mock_client.table.return_value.delete.return_value.eq.assert_any_call("lootbox_id", 123)

    def test_delete_lootbox_not_found(self):
        """
        Test deleting a lootbox that does not exist.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=None)

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.delete("NonexistentLootbox")

        self.assertIn("Lootbox 'NonexistentLootbox' not found", str(context.exception))

    def test_delete_associated_skins_failure(self):
        """
        Test deleting a lootbox when associated skins cannot be deleted.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)

        self.mock_client.table.return_value.delete.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=None),
            MagicMock(data=[{"success": True}])
        ]

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.delete("TestLootbox")

        self.assertIn("Failed to delete associated skins for lootbox 'TestLootbox'", str(context.exception))

    def test_delete_lootbox_failure(self):
        """
        Test deleting a lootbox when the lootbox itself cannot be deleted.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)

        self.mock_client.table.return_value.delete.return_value.eq.return_value.execute.side_effect = [
            MagicMock(data=[{"success": True}]),
            MagicMock(data=None)
        ]

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.delete("TestLootbox")

        self.assertIn("Failed to delete lootbox 'TestLootbox'", str(context.exception))

    def test_update_failed_to_add_skins(self):
        """
        Test updating a lootbox when adding skins fails.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)

        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        self.mock_skin_manager.get_skin_by_name.side_effect = lambda name: {"id": name[-1], "name": name}

        self.mock_client.table.return_value.insert.return_value.execute.return_value.data = None

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.update("TestLootbox", ["Skin2", "Skin3"])

        self.assertIn("Failed to add skins to lootbox.", str(context.exception))

    def test_update_skin_data_not_found(self):
        """
        Test updating a lootbox with a skin that cannot be found in the database.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)

        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        self.mock_skin_manager.get_skin_by_name.side_effect = lambda name: None

        updated_contents = self.lootbox_manager.update("TestLootbox", ["NonexistentSkin"])

        self.assertEqual(len(updated_contents), 0)

    def test_update_skin_id_not_found(self):
        """
        Test updating a lootbox with a skin that has no valid ID.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)

        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        self.mock_skin_manager.get_skin_by_name.side_effect = lambda name: {"name": name}

        updated_contents = self.lootbox_manager.update("TestLootbox", ["SkinWithoutID"])

        self.assertEqual(len(updated_contents), 0)

    def test_delete_error(self):
        """
        Test deleting a lootbox when an exception occurs.
        """
        self.lootbox_manager.get_lootbox_id_by_name = MagicMock(return_value=123)
        self.mock_client.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        with self.assertRaises(ValueError) as context:
            self.lootbox_manager.delete("TestLootbox")

        self.assertIn("An error occurred while deleting lootbox 'TestLootbox'", str(context.exception))

if __name__ == "__main__":
    unittest.main()