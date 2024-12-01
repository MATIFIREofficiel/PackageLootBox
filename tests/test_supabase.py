import unittest
from unittest.mock import patch
from lootbox.supabase import Supabase

class TestSupabase(unittest.TestCase):
    def reset_singleton_instance(self):
        """
        Resets the singleton instance of Supabase to ensure a clean state for each test.
        """
        Supabase._instance = None

    def setUp(self):
        self.reset_singleton_instance()

    @patch("lootbox.supabase.create_client")
    @patch("lootbox.supabase.os.getenv")
    def test_initialize_client_success(self, mock_getenv, mock_create_client):
        """
        Test successful initialization of the Supabase client.
        """
        mock_getenv.side_effect = lambda key: "mock_url" if key == "SUPABASE_URL" else "mock_key"

        supabase_instance = Supabase()

        mock_create_client.assert_called_once_with("mock_url", "mock_key")

        self.assertIsNotNone(supabase_instance.get_client())

    @patch("lootbox.supabase.os.getenv")
    def test_missing_supabase_url(self, mock_getenv):
        """
        Test that a ValueError is raised when SUPABASE_URL is missing.
        """
        mock_getenv.side_effect = lambda key: None if key == "SUPABASE_URL" else "mock_key"

        with self.assertRaises(ValueError) as context:
            Supabase()

        self.assertIn("Environment variable 'SUPABASE_URL' is missing.", str(context.exception))

        mock_getenv.assert_any_call("SUPABASE_URL")

    @patch("lootbox.supabase.os.getenv")
    def test_missing_supabase_key(self, mock_getenv):
        """
        Test that a ValueError is raised when SUPABASE_SERVICE_ROLE_KEY is missing.
        """

        mock_getenv.side_effect = lambda key: "mock_url" if key == "SUPABASE_URL" else None

        with self.assertRaises(ValueError) as context:
            Supabase()

        self.assertIn("Environment variable 'SUPABASE_SERVICE_ROLE_KEY' is missing.", str(context.exception))

        mock_getenv.assert_any_call("SUPABASE_SERVICE_ROLE_KEY")

    @patch("lootbox.supabase.create_client")
    @patch("lootbox.supabase.os.getenv")
    def test_singleton_behavior(self, mock_getenv, mock_create_client):
        """
        Test that the Supabase class enforces singleton behavior.
        """
        mock_getenv.side_effect = lambda key: "mock_url" if key == "SUPABASE_URL" else "mock_key"

        supabase_instance1 = Supabase()

        supabase_instance2 = Supabase()

        self.assertIs(supabase_instance1, supabase_instance2)

        mock_create_client.assert_called_once()

if __name__ == "__main__":
    unittest.main()
