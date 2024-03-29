import pygame
import json

# mapping of tiles depending on their neighbor
# tuple of sorted list so the order doesn't matter but need tuple as lists don't work as keys
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

PROGRESSBAR_POS = (0, 0)    # position of progressbar

NEIGHBOR_OFFSETS = [(1, -1), (1, 0), (1, 1),
                    (0, -1), (0, 0), (0, 1),
                    (-1, -1), (-1, 0), (-1, 1),
                    (2, 0), (0, 2), (-2, 0),
                    (1, 2), (-1, 2)]    # offsets of neighbors for big enemy

PHYSICS_TILES = {
                 'stone': {0: (16, 1, 0),   # variant: (width, height, vertical_offset)
                           1: (16, 1, 0),   # set as we don't put keys (set is more efficient for lookup than list)
                           2: (16, 1, 0),
                           3: (16, 0, 0),
                           4: (16, 0, 0),
                           5: (16, 1, 0),
                           6: (16, 1, 0),
                           7: (16, 1, 0),
                           8: (16, 0, 0),
                           9: (16, 0, 0),
                           10: (48, 18, 0),
                           11: (32, 12, 0),
                           12: (32, 12, 0),
                           13: (32, 14, 0),
                           14: (32, 14, 0),
                           },       # done
                 'decor': {0: (16, 8, 24),
                           1: (16, 8, 24),
                           2: (16, 8, 24),
                           3: (16, 8, 24),
                           4: (16, 8, 24),
                           },
                 'water': {0: (16, 8, 0),   # variant: (width, height, vertical_offset)
                           1: (16, 8, 0),
                           2: (16, 8, 0),
                           3: (16, 8, 0),
                           4: (16, 8, 0),
                           5: (16, 8, 0),
                           6: (16, 8, 0),
                           7: (16, 8, 0),
                           8: (16, 8, 0),
                           9: (16, 8, 0),
                           10: (16, 8, 0),
                           11: (16, 8, 0),
                           12: (16, 8, 0),
                           },       # done
                 }
AUTOTILE_TYPES = {}     # {'grass', 'stone'} # types of tiles that should be autotiled
FRONT_BACK_OFFSET = {
                    'decor':  {0: 18,  # almost done
                                1: 68,
                                2: -8,  # to be modified
                                3: -3,  # knn thingy
                                4: -8,  # knn thingy
                                },      # almost done
                    'spawners':   {0: 8,   # player
                                    1: 8,   # light entity
                                    2: 8,   # npc
                                    3: 60,  # enemy
                                    4: 8,   # shadow entity
                                    },       # irrelevant
                    'stone':  {    # done
                         0: -8,
                         1: -8,
                         2: -8,
                         3: -12,
                         4: -20,
                         5: -8,
                         6: -8,
                         7: -8,
                         8: -20,
                         9: -20,
                         10: -8,
                         11: -8,
                         12: -8,
                         13: -8,
                         14: -8,
                         },           # done
                    'ground_decor': {  # done
                        0: -8,
                        1: -8,
                        2: -10,
                        3: -9,
                        4: -30,
                        5: -30,
                        6: -30,
                        7: -30,
                        8: -30,
                        9: -30,
                        10: -30,
                     },     # done
                    'tree': {  # done
                         0: 62,
                         1: 62,
                         2: 62,
                         3: 62,
                         4: 62,
                         5: 62,
                         6: 62,
                         7: 62,
                     },             # done
                    'grass': {  # done
                         0: -30,
                         1: -30,
                         2: -30,
                         3: -30,
                         4: -30,
                         5: -30,
                         6: -30,
                         7: -30,
                         8: -30,
                         9: -30,
                        10: -30,
                        11: -30,
                        12: -30,
                        13: -30,
                        14: -30,
                        15: -30,
                        16: -30,
                        17: -30,
                        18: -30,
                        19: -30,
                        20: -30,
                        21: -30,
                        22: -30,
                        23: -30,
                        24: -30,
                        25: -30,
                        26: -30,
                        27: -30,
                        28: -30,
                        29: -30,
                        30: -30,
                        31: -30,
                        32: -30,
                        33: -30,
                        34: -30,
                        35: -30,
                        36: -30,
                        37: -30,
                        38: -30,
                     },            # done
                    }  # offsets for rendering front and back objects (has to be set manually)


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

        self.border = []    # define border of the map
        self.border_tiles = []

    # find all tiles of (type, variant) specified in id_pairs
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]

        return matches

    # get tiles that are currently around the player (big for optimization)
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc_int = [tile_loc[0] + offset[0],tile_loc[1] + offset[1]]
            check_loc_int_offgrid = [check_loc_int[0]*self.tile_size, check_loc_int[1]*self.tile_size]
            check_loc_str = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc_str in self.tilemap:
                tiles.append(self.tilemap[check_loc_str])
            for tile in self.offgrid_tiles:
                if tile['pos'] == check_loc_int_offgrid:
                    tiles.append({'type': tile['type'], 'pos': check_loc_int, 'variant': tile['variant']})
            if check_loc_int in self.border:
                tiles.append({'type': 'border element place holder', 'pos': check_loc_int})
        return tiles

    # save the tilemap to json
    def save(self, path):
        with open(path, 'w') as f:
            json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles, 'border': self.border}, f)

    # load tilemap from json
    def load(self, path):
        with open(path, 'r') as f:
            map_data = json.load(f)

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        self.border = map_data['border']

    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            return self.tilemap[tile_loc]
        for tile in self.offgrid_tiles:
            if tile['pos'] == pos and tile['type'] in PHYSICS_TILES:
                return tile

    # define which of the surrounding tiles have physics enabled
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size + PHYSICS_TILES[tile['type']][tile['variant']][2], PHYSICS_TILES[tile['type']][tile['variant']][0], PHYSICS_TILES[tile['type']][tile['variant']][1]))
            if tile['pos'] in self.border:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    # auto tiling and border generation
    def autotile(self):
        self.border = []    # reset border to get rid of old border elements
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1,0), (-1,0), (0,1), (0,-1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:     # check if the adjacent tile is of the same type
                        neighbors.add(shift)
                else:                                                       # add position to border if no tile is found (convert loc string to int list)
                    self.border.append([int(check_loc.split(';')[0]), int(check_loc.split(';')[1])])
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

        print(self.offgrid_tiles)

    # place tile TBA on the border only for debugging for now
    def show_border(self):
        for loc in self.border:
            self.border_tiles.append({'type': 'grass', 'variant': 0, 'pos': loc})
        print(self.border)

    def render_progress_bar(self, surf, progress):
        black = (0, 0, 0)
        white = (255, 255, 255)
        green = (0, 255, 0)
        red = (255, 0, 0)
        bar_width = 50
        bar_height = 10
        border_width = 1

        pygame.draw.rect(surf, black, (PROGRESSBAR_POS[0], PROGRESSBAR_POS[1], bar_width, bar_height))
        # Calculate width of progress bar based on percentage
        progress_width = int(bar_width * progress)
        pygame.draw.rect(surf, green, (PROGRESSBAR_POS[0], PROGRESSBAR_POS[1], progress_width, bar_height))

        # Draw border for the progress bar
        pygame.draw.rect(surf, black, (PROGRESSBAR_POS[0], PROGRESSBAR_POS[1], bar_width, bar_height), border_width)

    # render tilemap and offgrid tiles, the order sets what is in front and what in the back, offset used for cam
    # render all for editor
    def render(self, surf, offset=(0, 0)):

        # only render tiles that appear on screen (improves performance)
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                location = str(x) + ';' + str(y)
                if location in self.tilemap:
                    tile = self.tilemap[location]
                    surf.blit(self.game.assets[tile['type']][tile['variant']],
                              (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        for tile in self.border_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']],
                      (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

    # render tiles behind player
    def render_back(self, surf, offset=(0, 0), player_pos=(0, 0)):

        # only render tiles that appear on screen (improves performance)
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                location = str(x) + ';' + str(y)
                #print(y, player_pos[0] // self.tile_size)
                if location in self.tilemap: # and y <= (player_pos[1] // self.tile_size + 1):
                    tile = self.tilemap[location]
                    surf.blit(self.game.assets[tile['type']][tile['variant']],
                              (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

    def render_order_offgrid(self, surf, offset=(0, 0)):
        render_list = []

        '''
        #only take visible tiles
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                location_offgrid = [x * self.tile_size, y * self.tile_size]'''

        for tile in self.offgrid_tiles:
            tile_copy = tile.copy()
            tile_copy['pos_adj'] = tile_copy['pos'][0] - offset[0], tile_copy['pos'][1] - offset[1] + FRONT_BACK_OFFSET[tile_copy['type']][tile['variant']]
            render_list.append(tile_copy)

        return render_list

    def render_object(self, surf, type, variant, pos, offset=(0, 0)):
        surf.blit(self.game.assets[type][variant], (pos[0] - offset[0], pos[1] - offset[1]))

    def get_knn(self):
        knn_tiles = []
        for tile in self.offgrid_tiles:
            if tile['type'] == 'decor':
                if tile['variant'] == 2 or tile['variant'] == 3 or tile['variant'] == 4:
                    knn_tiles.append(tile)
        return knn_tiles


    def get_totems(self, level):
        totem_tiles=[]
        for tile in self.offgrid_tiles:
            if tile['type'] == 'decor':
                if tile['variant'] == 0:
                    #tile['dialogue'] = False
                    totem_tiles.append(tile)
        for index, tile in enumerate(totem_tiles):
            if level == 1:
                tile["index"] = index
            if level == 2:
                tile["index"] = index + 4

        return totem_tiles




