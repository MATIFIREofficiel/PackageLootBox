from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

class Supabase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ to implement Singleton behavior.
        """
        if cls._instance is None:
            cls._instance = super(Supabase, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes the Supabase client service role using environment variables.
        """
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url:
            raise ValueError("Environment variable 'SUPABASE_URL' is missing.")
        if not key:
            raise ValueError("Environment variable 'SUPABASE_SERVICE_ROLE_KEY' is missing.")
        self.client: Client = create_client(url, key)

    def get_client(self) -> Client:
        """
        Returns the Supabase client service role instance.
        """
        return self.client
