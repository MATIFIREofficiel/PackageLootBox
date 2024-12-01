from lootbox.supabase import Supabase

class SkinManager:
    def __init__(self) -> None:
        """
        Initializes the SkinManager module and sets up the Supabase client.
        """
        self.supabase_client_service_role = Supabase().get_client()

    def get_all_skins(self, limit=500, offset=0) -> list:
        """
        Retrieves a paginated list of skins.

        Args:
            limit (int): Number of skins to return (default 500).
            offset (int): Number of skins to skip before starting the result (default 0).

        Returns:
            list: A list of skins as dictionaries.

        Raises:
            ValueError: If an error occurs while retrieving skins.
        """
        try:
            response = (
                self.supabase_client_service_role
                .table("skins_reference")
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            raise ValueError(f"An error occurred while retrieving skins: {e}")


    def get_available_skins(self) -> list:
        """
        Retrieves all available skins with full information.

        Returns:
            list: A list of available skins as dictionaries.

        Raises:
            ValueError: If an error occurs while retrieving available skins.
        """
        try:
            response = (
                self.supabase_client_service_role
                .table("skins_reference")
                .select("*")
                .eq("available", True)
                .execute()
            )
            if response.data:
                return response.data

            return []

        except Exception as e:
            raise ValueError(f"An error occurred while retrieving available skins: {e}")

    def get_filtered_skins(
        self,
        min_price: float = 2.0,
        max_price: float = 1000.0,
        order: str = "asc",
        name_contains: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """
        Retrieves skins within a specified price range, optionally filtering by a keyword in the name,
        sorted in ascending or descending order, with pagination.

        Args:
            min_price (float, optional): The minimum price of the skins. Defaults to 2.0.
            max_price (float, optional): The maximum price of the skins. Defaults to 1000.0.
            order (str, optional): The sorting order, either 'asc' for ascending or 'desc' for descending. Defaults to 'asc'.
            name_contains (str, optional): A keyword to filter skins by name. Defaults to None.
            limit (int, optional): Number of results to return. Defaults to 50.
            offset (int, optional): Number of results to skip. Defaults to 0.

        Returns:
            list: A paginated list of skins as dictionaries.

        Raises:
            ValueError: If invalid arguments are provided or if an error occurs during execution.
        """
        try:
            if order not in ["asc", "desc"]:
                raise ValueError(f"Invalid order value '{order}'. Must be 'asc' or 'desc'.")

            if max_price < min_price:
                raise ValueError(f"max_price ({max_price}) cannot be less than min_price ({min_price}).")

            if limit <= 0:
                raise ValueError("Limit must be greater than 0.")
            if offset < 0:
                raise ValueError("Offset cannot be negative.")

            desc = True if order == "desc" else False

            query = (
                self.supabase_client_service_role
                .table("skins_reference")
                .select("*")
                .gte("base_price", min_price)
                .lte("base_price", max_price)
                .eq("available", True)
            )

            if name_contains:
                query = query.ilike("name", f"%{name_contains}%")

            query = query.order("base_price", desc=desc).range(offset, offset + limit - 1)

            response = query.execute()

            return response.data if response.data else []

        except ValueError as ve:
            raise ValueError(f"Value error: {ve}")
        except Exception as e:
            raise ValueError(f"An error occurred while retrieving skins by price range: {e}")

    def get_skin_by_id(self, skin_id: str) -> dict:
        """
        Retrieves a skin by its unique ID.

        Args:
            skin_id (str): The UUID of the skin to retrieve.

        Returns:
            dict: The details of the skin, or None if not found.

        Raises:
            ValueError: If an error occurs while retrieving the skin.
        """
        try:
            response = (
                self.supabase_client_service_role
                .table("skins_reference")
                .select("*")
                .eq("id", skin_id)
                .single()
                .execute()
            )

            if response.data:
                return response.data

            return None

        except Exception as e:
            raise ValueError(f"An error occurred while retrieving skin by ID: {e}")

    def get_skin_by_name(self, name: str) -> dict:
        """
        Retrieves a skin matching a specific name exactly (case-sensitive).

        Args:
            name (str): The exact name of the skin to retrieve.

        Returns:
            dict: The details of the skin, or None if not found.

        Raises:
            ValueError: If an error occurs while retrieving the skin.
        """
        try:
            response = (
                self.supabase_client_service_role
                .table("skins_reference")
                .select("*")
                .eq("name", name)
                .single()
                .execute()
            )

            if response.data:
                return response.data

            return None

        except Exception as e:
            raise ValueError(f"An error occurred while retrieving skin by name: {e}")
