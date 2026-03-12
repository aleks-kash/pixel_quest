from src.platform.platform_obj import Platform
from src.level.level_0_hub import Level0Hub
from src.level.level_1_tutorial import Level1Tutorial
from src.level.level_2_night import Level2Night

class Level:
    def __init__(self, k_lvl):
        if k_lvl == 0:
            self.level = Level0Hub()
        elif k_lvl == 1:
            self.level = Level1Tutorial()
        elif k_lvl == 2:
            self.level = Level2Night()
        else:
            self.level = Level0Hub()

    def get_platforms(self):
        return self.level.platforms
    def get_items(self):
        return self.level.items
    def get_npcs(self):
        return self.level.npcs
    def get_projectiles(self):
        return self.level.projectiles