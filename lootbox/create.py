from .supabase import Supabase

class Create:
    def __init__(self):
        """
        Initializes the Create module and sets up the Supabase client.
        """
        self.supabase_client = Supabase().get_client()
        print("Initialized Create module with Supabase integration.")

    def create_lootbox(self, name, description):
        """
        Adds a new lootbox to the 'lootbox_reference' table in Supabase.

        Args:
            name (str): Name of the lootbox.
            description (str): Description of the lootbox.
        """
        data = {
            "name": name,
            "description": description,
        }

        try:
            response = self.supabase_client.table("lootbox_reference").insert(data).execute()

            if response.data:
                print(f"Lootbox '{name}' successfully created")
            else:
                print(f"Unexpected response format: {response}")
        except Exception as e:
            print(f"An error occurred while creating lootbox '{name}': {e}")
