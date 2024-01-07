import os
import sys
import pygame

from scripts.utils import load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 4.0


class Editor:
    def __init__(self):
        pygame.init()

        # set display name and size
        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))   # used for pixel art (render small and scale up to screen size)

        # init game clock
        self.clock = pygame.time.Clock()

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'ground_decor': load_images('tiles/ground_decor'),
            'spawners': load_images('tiles/spawners'),
            'stone': load_images('tiles/stone'),
            'tree': load_images('tiles/tree'),
            'water': load_images('tiles/water'),
        }

        # contains current moving direction of camera
        self.movement = [False, False, False, False]

        # create tilemap
        self.tilemap = Tilemap(self, tile_size=16)

        # load tilemap if file is found
        try:
            self.tilemap.load('map-big.json')
            # self.tilemap.load('map-debug.json')
        except FileNotFoundError:
            pass

        # camera position
        self.cam = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.strg = False
        self.ongrid = True


    def run(self):
        while True:
            self.display.fill((0, 0, 0))    # reset screen

            # camera movement
            self.cam[0] += (self.movement[1] - self.movement[0]) * 2
            self.cam[1] += (self.movement[3] - self.movement[2]) * 2

            render_scroll = (int(self.cam[0]), int(self.cam[1]))

            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant]
            current_tile_img.set_alpha(100)     # make slightly transparent (0 - 255)

            mouse_position = pygame.mouse.get_pos()     # get mouse position (based on window)
            mouse_position = (mouse_position[0] / RENDER_SCALE, mouse_position[1] / RENDER_SCALE)   # adjust position by render scale
            tile_pos = (int((mouse_position[0] + self.cam[0]) // self.tilemap.tile_size), int((mouse_position[1] + self.cam[1]) // self.tilemap.tile_size))

            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.cam[0], tile_pos[1] * self.tilemap.tile_size - self.cam[1]))
            elif self.strg:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.cam[0], tile_pos[1] * self.tilemap.tile_size - self.cam[1]))
            else:
                self.display.blit(current_tile_img, mouse_position)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.cam[0], tile['pos'][1] - self.cam[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mouse_position):
                        self.tilemap.offgrid_tiles.remove(tile)


            current_tile_img.set_alpha(255)
            self.display.blit(current_tile_img, (5, 5))



            # add event listeners
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # mouse clicks/wheel for placing tiles
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:                   # place on left click
                        self.clicking = True
                        if not self.ongrid and not self.strg:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mouse_position[0] + self.cam[0], mouse_position[1] + self.cam[1])})
                        elif not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (tile_pos[0] * self.tilemap.tile_size, tile_pos[1] * self.tilemap.tile_size)})
                            print((tile_pos[0] * self.tilemap.tile_size, tile_pos[1] * self.tilemap.tile_size))
                    if event.button == 3:                   # remove on right click
                        self.right_clicking = True

                    # select tile by wheel, tile group in general, tile of current group when holding shift
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_variant = 0
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                        if event.button == 5:
                            self.tile_variant = 0
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                # key press
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:             # move camera with w,a,s,d
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:             # toggle on and off grid with g
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:             # press o for saving
                        self.tilemap.save('map-big.json')
                    if event.key == pygame.K_t:             # automatically select correct variant with t
                        self.tilemap.autotile()
                    if event.key == pygame.K_b:             # press b to place tiles on border
                        self.tilemap.show_border()
                    if event.key == pygame.K_LSHIFT:        # hold shift to use wheel to swap in tile group
                        self.shift = True
                    if event.key == pygame.K_RSHIFT:
                        self.shift = True
                    if event.key == pygame.K_LCTRL:         # hold CTRL to align offgrid element on grid
                        self.strg = True

                # key release
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
                    if event.key == pygame.K_RSHIFT:
                        self.shift = False
                    if event.key == pygame.K_LCTRL:
                        self.strg = False

            # scale and project the screen to the full display
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()

            # keep fps at 60
            self.clock.tick(60)

Editor().run()