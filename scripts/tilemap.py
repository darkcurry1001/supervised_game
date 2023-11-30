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

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {}      # {'grass', 'stone'}  # set as we don't put keys (set is more efficient for lookup than list)
AUTOTILE_TYPES = {}     # {'grass', 'stone'} # types of tiles that should be autotiled
FRONT_BACK_OFFSET = {'objects': {0: 24,
                                 1: 68,
                                 },
                     'spawners': {0: 8,
                                  1: 8,
                                  },
                    }  # offsets for rendering front and back objects (has to be set manually)


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

        self.border = []    # define border of the map
        self.border_tiles = []

    # get tiles that are currently around the player (big for optimization)
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc_int = [tile_loc[0] + offset[0],tile_loc[1] + offset[1]]
            check_loc_str = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc_str in self.tilemap:
                tiles.append(self.tilemap[check_loc_str])
            if check_loc_int in self.border:
                tiles.append({'type': 'border element place holder', 'pos': check_loc_int})
        return tiles

    # save the tilemap to json
    def save(self, path):
        with open(path, 'w') as f:
            json.dump({'tilemap' : self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles, 'border': self.border}, f)

    # load tilemap from json
    def load(self, path):
        with open(path, 'r') as f:
            map_data = json.load(f)

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        self.border = map_data['border']

    # define which of the surrounding tiles have physics enabled
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
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
            self.border_tiles.append({'type': 'ground', 'variant': 0, 'pos': loc})
        print(self.border)

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

        for tile in self.offgrid_tiles:
            if tile['pos'][1] <= player_pos[1] - FRONT_BACK_OFFSET[tile['type']][tile['variant']]:
                surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        # do not display border in game
        '''
        for tile in self.border_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']],
                      (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
        '''

    # render tiles in front of player
    def render_front(self, surf, offset=(0, 0), player_pos=(0, 0)):
        '''
        # only render tiles that appear on screen (improves performance)
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                location = str(x) + ';' + str(y)
                #print(y, player_pos[0] // self.tile_size)
                if location in self.tilemap and y > (player_pos[1] // self.tile_size + 1):
                    tile = self.tilemap[location]
                    surf.blit(self.game.assets[tile['type']][tile['variant']],
                              (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
        '''

        for tile in self.offgrid_tiles:
            if tile['pos'][1] > player_pos[1] - FRONT_BACK_OFFSET[tile['type']][tile['variant']]:
                #print(tile['pos'][1], player_pos[1])
                surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        # do not display border in game
        '''
        for tile in self.border_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']],
                      (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
        '''






