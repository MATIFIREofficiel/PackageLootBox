from lootbox import LootboxManager
from lootbox import SkinManager

try:
    lootbox = LootboxManager()

    lootbox.create("Basic Chest", "It's just a basic chest")

    result = lootbox.get_lootbox_contents("Basic Chest")

    skins_list = ["M4A4 | Polysoup (Minimal Wear)", "StatTrak™ UMP-45 | Momentum (Minimal Wear)", "StatTrak™ Tec-9 | Decimator (Minimal Wear)"]

    lootbox.update("Basic Chest", skins_list)

    lootbox.delete("Basic Chest")

except ValueError as e:
    print(f"Error: {e}")
