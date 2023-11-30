import sys
import pygame
from scripts.entities import Player
from scripts.utils import load_image
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
            # 'decor': load_images('tiles/decor'),
            # 'grass': load_images('tiles/grass'),
            # 'large_decor': load_images('tiles/large_decor'),
            # 'stone': load_images('tiles/stone'),
            'ground': load_images('tiles_1/ground'),
            'objects': load_images('tiles_1/objects'),
            'spawners': load_images('tiles_1/spawners'),
            #'player': load_image('entities/player.png'),
            'player': load_image('entities_1/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            #'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            #'player/run': Animation(load_images('entities/player/run'), img_dur=5),
            #'player/jump': Animation(load_images('entities/player/jump')),
            #'player/slide': Animation(load_images('entities/player/slide')),
            #'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'player/idle/side': Animation(load_images('entities_1/player/idle/side'), img_dur=6),
            'player/run/side': Animation(load_images('entities_1/player/run/side'), img_dur=5),
        }

        # create clouds
        self.clouds = Clouds(self.assets['clouds'], count=16)

        # create player
        self.player = Player(self, (50, 50), (8, 15))

        # create tilemap
        self.tilemap = Tilemap(self)
        self.tilemap.load('map.json')

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

            self.clouds.update()
            self.clouds.render(self.display, offset=render_cam)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], self.movement[2] - self.movement[3]))

            # render order: tiles behind player, player, tiles in front of player
            self.tilemap.render_back(self.display, offset=render_cam, player_pos=self.player.pos)
            self.player.render(self.display, offset=render_cam)
            self.tilemap.render_front(self.display, offset=render_cam, player_pos=self.player.pos)

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
                        pass

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

            # scale and project the screen to the full display
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()

            # keep fps at 60
            self.clock.tick(60)

Game().run()
