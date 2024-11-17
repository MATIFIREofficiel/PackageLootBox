from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

class Supabase:
    def __init__(self):
        """
        Initializes the Supabase client using environment variables.
        """
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("Supabase URL or Key is not set in environment variables.")
        self.client: Client = create_client(url, key)

    def get_client(self) -> Client:
        """
        Returns the Supabase client instance.
        """
        return self.client
