from lootbox.supabase import Supabase
from lootbox.skin_manager import SkinManager
from typing import List

class LootboxManager:
    def __init__(self):
        """
        Initializes the LootboxManager module and sets up the Supabase client.
        """
        self.supabase_client_service_role = Supabase().get_client()
        self.skin_manager = SkinManager()

    def get_all_lootbox(self, limit=500, offset=0) -> list:
        """
        Retrieves a paginated list of lootbox.

        Args:
            limit (int): Number of lootbox to return (default 500).
            offset (int): Number of lootbox to skip before starting the result (default 0).

        Returns:
            list: A list of lootbox as dictionaries.

        Raises:
            ValueError: If an error occurs while retrieving lootbox.
        """
        try:
            if limit <= 0:
                raise ValueError("Limit must be greater than 0.")
            if offset < 0:
                raise ValueError("Offset cannot be negative.")

            response = (
                self.supabase_client_service_role
                .table("lootbox_reference")
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            raise ValueError(f"An error occurred while retrieving lootbox: {e}")

    def get_lootbox_id_by_name(self, lootbox_name: str) -> int:
        """
        Retrieves the ID of a lootbox by its name.

        Args:
            lootbox_name (str): The name of the lootbox.

        Returns:
            int: The ID of the lootbox if found, or None if the lootbox does not exist.

        Raises:
            ValueError: If an error occurs while retrieving the lootbox ID.
        """
        try:
            response = (
                self.supabase_client_service_role
                .table("lootbox_reference")
                .select("lootbox_id")
                .eq("name", lootbox_name)
                .single()
                .execute()
            )

            if response.data:
                return response.data["lootbox_id"]

            return None

        except Exception as e:
            raise ValueError(f"An error occurred while retrieving lootbox ID for '{lootbox_name}': {e}")

    def get_lootbox_contents(self, lootbox_name: str) -> list:
        """
        Displays the contents of a lootbox by showing all associated skins.

        Args:
            lootbox_name (str): The name of the lootbox to display.

        Returns:
            dict: A result containing the lootbox contents or an error message.

        Raises:
            ValueError: If the lootbox is not found or an error occurs during execution.
        """
        try:
            lootbox_id = self.get_lootbox_id_by_name(lootbox_name)
            if not lootbox_id:
                raise ValueError(f"Lootbox '{lootbox_name}' not found.")

            lootbox_skins_response = (
                self.supabase_client_service_role
                .table("lootbox_skins")
                .select("skin_id")
                .eq("lootbox_id", lootbox_id)
                .execute()
            )

            if not lootbox_skins_response.data:
                return []

            skin_ids = [entry["skin_id"] for entry in lootbox_skins_response.data]
            skin_details = [
                self.skin_manager.get_skin_by_id(skin_id)
                for skin_id in skin_ids
                if self.skin_manager.get_skin_by_id(skin_id)
            ]

            return skin_details

        except Exception as e:
            raise ValueError(f"An error occurred while fetching contents of lootbox '{lootbox_name}': {e}")

    def create(self, name: str, description: str) -> None:
        """
        Adds a new lootbox to the 'lootbox_reference' table in Supabase.

        Args:
            name (str): Name of the lootbox.
            description (str): Description of the lootbox.

        Raises:
            ValueError: If the name or description is invalid, or if an error occurs during creation.
        """
        try:
            if not name.strip() or not description.strip():
                raise ValueError("Name and description are required and cannot be empty.")

            existing_response = (
                self.supabase_client_service_role
                .table("lootbox_reference")
                .select("lootbox_id")
                .eq("name", name)
                .execute()
            )

            if existing_response.data:
                raise ValueError(f"A lootbox with the name '{name}' already exists.")

            data = {
                "name": name,
                "description": description,
            }

            response = self.supabase_client_service_role.table("lootbox_reference").insert(data).execute()

            if not response.data:
                raise ValueError("Unexpected response format from Supabase.")

        except Exception as e:
            raise ValueError(f"An error occurred while creating the lootbox '{name}': {e}")

    def update(self, lootbox_name: str, skin_names: List[str]) -> list:
        """
        Adds a list of skins to a lootbox using the lootbox name and a list of skin names.
        Does not update the lootbox price or drop rate.

        Args:
            lootbox_name (str): Name of the lootbox to update.
            skin_names (List[str]): List of skin names to add to the lootbox.

        Returns:
            list: The list of skin names added to the lootbox.

        Raises:
            ValueError: If the lootbox is not found or if an error occurs during the update process.
        """
        try:
            lootbox_id = self.get_lootbox_id_by_name(lootbox_name)
            if not lootbox_id:
                raise ValueError(f"Lootbox '{lootbox_name}' not found.")

            skins_to_add = []
            duplicates = []
            not_found = []

            existing_skins_response = (
                self.supabase_client_service_role
                .table("lootbox_skins")
                .select("skin_id")
                .eq("lootbox_id", lootbox_id)
                .execute()
            )

            existing_skin_ids = {
                entry["skin_id"] for entry in existing_skins_response.data if isinstance(entry, dict) and "skin_id" in entry
            }

            for skin_name in skin_names:
                skin_data = self.skin_manager.get_skin_by_name(skin_name)
                if not skin_data:
                    not_found.append(skin_name)
                    continue

                skin_id = skin_data.get("id")
                if not skin_id:
                    not_found.append(skin_name)
                    continue

                if skin_id in existing_skin_ids:
                    duplicates.append(skin_name)
                    continue

                skins_to_add.append({
                    "lootbox_id": lootbox_id,
                    "skin_id": skin_id,
                    "drop_rate": 0
                })

            if skins_to_add:
                insert_response = (
                    self.supabase_client_service_role
                    .table("lootbox_skins")
                    .insert(skins_to_add)
                    .execute()
                )
                if not insert_response.data:
                    raise ValueError("Failed to add skins to lootbox.")

            return self.get_lootbox_contents(lootbox_name)

        except Exception as e:
            raise ValueError(f"An error occurred while updating lootbox '{lootbox_name}': {e}")

    def delete(self, lootbox_name: str) -> None:
        """
        Deletes a lootbox and its associated skins from the database.

        Args:
            lootbox_name (str): The name of the lootbox to delete.

        Raises:
            ValueError: If the lootbox is not found or if an error occurs during the deletion.
        """
        try:
            lootbox_id = self.get_lootbox_id_by_name(lootbox_name)
            if not lootbox_id:
                raise ValueError(f"Lootbox '{lootbox_name}' not found.")

            delete_skins_response = (
                self.supabase_client_service_role
                .table("lootbox_skins")
                .delete()
                .eq("lootbox_id", lootbox_id)
                .execute()
            )

            if delete_skins_response.data is None:
                raise ValueError(f"Failed to delete associated skins for lootbox '{lootbox_name}'.")

            delete_lootbox_response = (
                self.supabase_client_service_role
                .table("lootbox_reference")
                .delete()
                .eq("lootbox_id", lootbox_id)
                .execute()
            )

            if not delete_lootbox_response.data:
                raise ValueError(f"Failed to delete lootbox '{lootbox_name}'.")

        except Exception as e:
            raise ValueError(f"An error occurred while deleting lootbox '{lootbox_name}': {e}")

    def update_probabilities(self, lootbox_name: str, probabilities: dict[str, float]) -> None:
        """
        Updates the drop probabilities of skins in a lootbox.

        Args:
            lootbox_name (str): The name of the lootbox to update.
            probabilities (dict): A dictionary where the key is the skin name
                                and the value is the probability as a float.

        Raises:
            ValueError: If the lootbox is not found or if an error occurs during the update process.
        """
        try:
            lootbox_contents = self.get_lootbox_contents(lootbox_name)

            if not lootbox_contents:
                raise ValueError(f"Lootbox '{lootbox_name}' is empty.")

            lootbox_skin_names = {skin["name"] for skin in lootbox_contents}

            if len(probabilities) != len(lootbox_skin_names):
                raise ValueError("Different number of skins provided.")

            for skin_name in probabilities.keys():
                if skin_name not in lootbox_skin_names:
                    raise ValueError(f"Skin '{skin_name}' is not present in lootbox '{lootbox_name}'.")

            total_probability = sum(probabilities.values())
            if not abs(total_probability - 1.0) < 1e-20:
                raise ValueError(f"Probabilities must sum to 1. Current sum is {total_probability:.20f}.")

            expected_value = 0.0
            for skin in lootbox_contents:
                skin_name = skin["name"]
                skin_price = skin["base_price"]
                skin_probability = probabilities.get(skin_name, 0.0)
                expected_value += skin_price * skin_probability

            adjusted_price = expected_value * 1.2

            response = (
                self.supabase_client_service_role
                .table("lootbox_reference")
                .update({"base_price": adjusted_price})
                .eq("name", lootbox_name)
                .execute()
            )

            if response.data is None or len(response.data) == 0:
                raise ValueError(f"Failed to update the base price for lootbox '{lootbox_name}'.")

            lootbox_id = self.get_lootbox_id_by_name(lootbox_name)
            if not lootbox_id:
                raise ValueError(f"Lootbox '{lootbox_name}' not found for updating drop rates.")

            for skin in lootbox_contents:
                skin_id = skin["id"]
                skin_name = skin["name"]
                drop_rate = probabilities.get(skin_name, 0.0)

                drop_rate_response = (
                    self.supabase_client_service_role
                    .table("lootbox_skins")
                    .update({"drop_rate": drop_rate})
                    .eq("lootbox_id", lootbox_id)
                    .eq("skin_id", skin_id)
                    .execute()
                )

                if drop_rate_response.data is None or len(drop_rate_response.data) == 0:
                    raise ValueError(f"Failed to update drop rate for skin '{skin_name}' in lootbox '{lootbox_name}'.")

        except Exception as e:
            raise ValueError(f"An error occurred while updating probabilities for '{lootbox_name}': {e}")
