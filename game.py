import sys
import time

import pygame
from scripts.entities import Player, Enemy, LightEntity
from scripts.utils import load_image, load_transparent_images
from scripts.utils import load_images
from scripts.utils import Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds


class Game:
    def __init__(self):
        pygame.init()

        # set display name and size
        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))   # used for pixel art (render small and scale up to screen size)

        # init game clock
        self.clock = pygame.time.Clock()

        self.movement = [False, False, False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'ground_decor': load_images('tiles/ground_decor'),
            'spawners': load_images('tiles/spawners'),
            'stone': load_images('tiles/stone'),
            'tree': load_images('tiles/tree'),
            'water': load_images('tiles/water'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            #'clouds': load_images('clouds'),
            #'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            #'player/run': Animation(load_images('entities/player/run'), img_dur=5),
            #'player/jump': Animation(load_images('entities/player/jump')),
            #'player/slide': Animation(load_images('entities/player/slide')),
            #'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'player/idle/side': Animation(load_images('entities/player/idle/side'), img_dur=6),
            'player/idle/front': Animation(load_images('entities/player/idle/front'), img_dur=6),
            'player/idle/back': Animation(load_images('entities/player/idle/back'), img_dur=6),
            'player/run/side': Animation(load_images('entities/player/run/side'), img_dur=5),
            'player/run/front': Animation(load_images('entities/player/run/front'), img_dur=5),
            'player/run/back': Animation(load_images('entities/player/run/back'), img_dur=5),

            'light/idle/side': Animation(load_transparent_images('entities/light/idle/side'), img_dur=6),
            'light/idle/front': Animation(load_transparent_images('entities/light/idle/front'), img_dur=6),
            'light/idle/back': Animation(load_transparent_images('entities/light/idle/back'), img_dur=6),
            'light/walk/side': Animation(load_transparent_images('entities/light/walk/side'), img_dur=5),
            'light/walk/front': Animation(load_transparent_images('entities/light/walk/front'), img_dur=5),
            'light/walk/back': Animation(load_transparent_images('entities/light/walk/back'), img_dur=5),

        }

        # create clouds
        # self.clouds = Clouds(self.assets['clouds'], count=16)

        # create player
        self.player = Player(self, (50, 50), (8, 15))

        # create tilemap
        self.tilemap = Tilemap(self)
        self.tilemap.load('map-big.json')

        # create player, enemies and light entities from spawners (and cont of enemies)
        self.enemies = []
        self.light_entities = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            elif spawner['variant'] == 1:
                self.light_entities.append(LightEntity(self, spawner['pos'], (8, 15)))
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))    # debuggin only, remove later!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))    # might have to change size
        self.nr_enemies = len(self.enemies)

        # variables for flash
        self.flash = False
        self.pictures_taken = 0

        # list to store render elements
        self.render_list = []
            
        # camera position
        self.cam = [0, 0]

    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))    # reset screen

            # horizontal cam movement (player center - half of screen width (for centering player) - current cam position)
            self.cam[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.cam[0]) / 10
            # vertical cam movement (player center - half of screen width (for centering player) - current cam position)
            self.cam[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.cam[1]) / 10
            render_cam = (int(self.cam[0]), int(self.cam[1]))

            # self.clouds.update()
            # self.clouds.render(self.display, offset=render_cam)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], self.movement[2] - self.movement[3]))

            # render order: tiles behind player, enemies, player, flash, tiles in front of player
            self.tilemap.render_back(self.display, offset=render_cam, player_pos=self.player.pos)

            # list of objects to render
            self.render_list = self.tilemap.render_order_offgrid(self.display, offset=render_cam)

            self.render_list.append(self.player.render_order(offset=render_cam))

            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, (0, 0))
                self.render_list.append(enemy.render_order())

            for light_entity in self.light_entities.copy():
                light_entity.update(self.tilemap, (0, 0))
                self.render_list.append(light_entity.render_order(offset=render_cam))

            if self.flash:
                flash_pos = self.player.flash_pos(offset=render_cam)
                flash_rect = self.player.flash_rect(flash_pos)
                self.render_list.append(self.player.render_order_flash(offset=render_cam))
                for enemy in self.enemies:
                    pygame.draw.rect(self.display, (255, 0, 0), enemy.rect_offset(offset=render_cam), 1) # debug purpose only, delete later !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    if enemy.rect_offset(offset=render_cam).colliderect(flash_rect):
                        self.pictures_taken += 1
                        self.enemies.remove(enemy)
                        print(self.pictures_taken)

            # sort render list by y position
            self.render_list.sort(key=lambda x: x['pos_adj'][1])

            # render objects in render list
            for render_object in self.render_list:
                if render_object['type'] == 'player':
                    self.player.render(self.display, offset=render_cam)

                elif render_object['type'] == 'enemy':
                    for enemy in self.enemies:
                        if enemy.pos == render_object['pos_adj']:
                            enemy.render(self.display, offset=render_cam)

                elif render_object['type'] == 'light_entity':
                    for light_entity in self.light_entities:
                        if light_entity.pos == list(render_object['pos']):
                            light_entity.render(self.display, offset=render_cam)

                elif render_object['type'] == 'flash':
                    self.player.render_flash(self.assets['water'][4], flash_pos, self.display)

                else:
                    self.tilemap.render_object(self.display, render_object['type'], render_object['variant'], render_object['pos'], offset=render_cam)

            # render progress bar last (overlay)
            try:
                self.tilemap.render_progress_bar(self.display, progress=self.pictures_taken/self.nr_enemies)
            except ZeroDivisionError:
                self.tilemap.render_progress_bar(self.display, progress=0)

            #self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            #self.player.update(self.tilemap, (self.movement[1] - self.movement[0], self.movement[2] - self.movement[3]))

            # add event listeners
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # key press
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_a:             # move camera with w,a,s,d
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_s:
                        self.movement[2] = True
                    if event.key == pygame.K_w:
                        self.movement[3] = True
                    if event.key == pygame.K_SPACE:
                        self.flash = True

                # key release
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_s:
                        self.movement[2] = False
                    if event.key == pygame.K_w:
                        self.movement[3] = False
                    if event.key == pygame.K_SPACE:
                        self.flash = False

            # scale and project the screen to the full display
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()

            # keep fps at 60
            self.clock.tick(60)

Game().run()
