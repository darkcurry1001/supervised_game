import math
import sys
import time
from data.game_text import game_text
import pygame
from scripts.entities import Player, Enemy, LightEntity, Npc, ShadowEyeGlowEntity
from scripts.utils import load_image, load_transparent_images, render_proximity, totem_data
from scripts.utils import load_images
from scripts.utils import Animation, DialogueHandler, Codex
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds


def calculate_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def knn(k, target, group_one, group_two):
    distances = []
    for pos in group_one:
        distances.append([calculate_distance(target, pos), 1])
    for pos in group_two:
        distances.append([calculate_distance(target, pos), 2])

    distances = sorted(distances)[:k]
    neighbor_count_group_one = [element[1] for element in distances].count(1)
    if neighbor_count_group_one > k // 2:
        assigned_group = 1
    else:
        assigned_group = 2
    return assigned_group


class Game:
    def __init__(self):
        pygame.init()

        # set display name and size
        pygame.display.set_caption('Supervised game')
        self.screen = pygame.display.set_mode((1280, 960))
        self.display = pygame.Surface((320, 240))   # used for pixel art (render small and scale up to screen size)
        self.dialogue_display = pygame.Surface((1280, 960), pygame.SRCALPHA)


        # init game clock
        self.clock = pygame.time.Clock()
        self.level = 0

        self.movement = [False, False, False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'ground_decor': load_images('tiles/ground_decor'),
            'stone': load_images('tiles/stone'),
            'tree': load_images('tiles/tree'),
            'water': load_images('tiles/water'),
            'spawners': load_images('tiles/spawners'),

            'background': load_image('background.png'),
            'background2': load_image('background2.png'),
            'background2_dimmed': load_image('background/start/05.png'),
            "bg_dimmed": load_images("background/start"),

            'player': load_image('entities/player.png'),
            'player/idle/side': Animation(load_images('entities/player/idle/side'), img_dur=6),
            'player/idle/front': Animation(load_images('entities/player/idle/front'), img_dur=6),
            'player/idle/back': Animation(load_images('entities/player/idle/back'), img_dur=6),
            'player/run/side': Animation(load_images('entities/player/run/side'), img_dur=5),
            'player/run/front': Animation(load_images('entities/player/run/front'), img_dur=5),
            'player/run/back': Animation(load_images('entities/player/run/back'), img_dur=5),
            'player/slash/side': Animation(load_images('entities/player/slash/side'), img_dur=5),
            'player/slash/front': Animation(load_images('entities/player/slash/front'), img_dur=5),
            'player/slash/back': Animation(load_images('entities/player/slash/back'), img_dur=5),

            'light/idle/side': Animation(load_transparent_images('entities/light/idle/side'), img_dur=6),
            'light/idle/front': Animation(load_transparent_images('entities/light/idle/front'), img_dur=6),
            'light/idle/back': Animation(load_transparent_images('entities/light/idle/back'), img_dur=6),
            'light/walk/side': Animation(load_transparent_images('entities/light/walk/side'), img_dur=5),
            'light/walk/front': Animation(load_transparent_images('entities/light/walk/front'), img_dur=5),
            'light/walk/back': Animation(load_transparent_images('entities/light/walk/back'), img_dur=5),

            'enemy/attack/side': Animation(load_images('entities/enemy/attack/side', background=(0, 255, 43)), img_dur=5),
            'enemy/attack/front': Animation(load_images('entities/enemy/attack/front', background=(0, 255, 43)), img_dur=5),
            'enemy/attack/back': Animation(load_images('entities/enemy/attack/back', background=(0, 255, 43)), img_dur=5),
            'enemy/death': Animation(load_images('entities/enemy/death', background=(0, 255, 43)), img_dur=5),
            'enemy/idle/side': Animation(load_images('entities/enemy/idle/side', background=(0, 255, 43)), img_dur=6),
            'enemy/idle/front': Animation(load_images('entities/enemy/idle/front', background=(0, 255, 43)), img_dur=6),
            'enemy/idle/back': Animation(load_images('entities/enemy/idle/back', background=(0, 255, 43)), img_dur=6),
            'enemy/walk/side': Animation(load_images('entities/enemy/walk/side', background=(0, 255, 43)), img_dur=5),
            'enemy/walk/front': Animation(load_images('entities/enemy/walk/front', background=(0, 255, 43)), img_dur=5),
            'enemy/walk/back': Animation(load_images('entities/enemy/walk/back', background=(0, 255, 43)), img_dur=5),

            'npc/idle/side': Animation(load_images('entities/npc/idle/side', background=(0, 255, 43)), img_dur=24),

            'shadow-eye-glow/idle/side': Animation(load_transparent_images('entities/shadow-eye-glow/idle/side'), img_dur=6),
            'shadow-eye-glow/idle/front': Animation(load_transparent_images('entities/shadow-eye-glow/idle/front'), img_dur=6),
            'shadow-eye-glow/idle/back': Animation(load_transparent_images('entities/shadow-eye-glow/idle/back'), img_dur=6),
            'shadow-eye-glow/walk/side': Animation(load_transparent_images('entities/shadow-eye-glow/walk/side'), img_dur=5),
            'shadow-eye-glow/walk/front': Animation(load_transparent_images('entities/shadow-eye-glow/walk/front'), img_dur=5),
            'shadow-eye-glow/walk/back': Animation(load_transparent_images('entities/shadow-eye-glow/walk/back'), img_dur=5),

        }

        # create player
        self.player = Player(self, (50, 50), (8, 17))

        # create tilemap
        self.tilemap = Tilemap(self)
        self.totems = []
        self.totemid = -1
        self.solved_totems = 0

        # initialize lists used in load_level
        self.dialogue_handler = DialogueHandler(pygame.font.SysFont('Arial', 20))
        self.enemies = []
        self.light_entities = []
        self.shadow_eye_glow = []
        self.npcs = []
        self.nr_enemies = 0
        self.nr_light_and_shadow = 0

        # list of rects npcs
        self.npc_rects = []

        # variables for flash
        self.flash = False
        self.pictures_taken = 0

        # list to store render elements
        self.render_list = []

        # camera position
        self.cam = [0, 0]

        # dead timer
        self.dead_timer = 0

        # Render the text
        self.font = pygame.font.SysFont('Arial', 25)
        self.codex = Codex(self.font, self.dialogue_display)
        self.display_text = game_text["intro"]
        self.active_text = 0
        self.messages = self.display_text[self.active_text]
        self.snip = self.font.render('', True, (255, 255, 255))
        self.text_counter = 0
        self.text_speed = 3
        self.active_message = 0
        self.message = self.messages[self.active_message]
        self.text_done = False

    def load_level(self):
        # reset lists and vars
        self.enemies = []
        self.light_entities = []
        self.shadow_eye_glow = []
        self.npcs = []
        self.nr_enemies = 0
        self.nr_light_and_shadow = 0
        self.npc_rects = []
        self.pictures_taken = 0

        if self.level == 0:
            self.tilemap.load(f'map-big1.json')
        elif self.level == 1:
            self.tilemap.load(f'map-big2.json')
        elif self.level == 2:
            self.tilemap.load(f'map-big3.json')

        #self.tilemap.load('map-debug.json')

        # create player, enemies, npcs and light entities from spawners (and cont of enemies)
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1), ('spawners', 2), ('spawners', 3), ('spawners', 4), ]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            elif spawner['variant'] == 1:
                self.light_entities.append(LightEntity(self, spawner['pos'], (8, 15)))
            elif spawner['variant'] == 2:
                self.npcs.append(Npc(self, spawner['pos'], (18, 12)))
            elif spawner['variant'] == 3:
                self.enemies.append(Enemy(self, spawner['pos'], (16, 35)))
            elif spawner['variant'] == 4:
                self.shadow_eye_glow.append(ShadowEyeGlowEntity(self, spawner['pos'], (8, 15)))
            else:  # not accessed for now
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))  # might have to change size
        self.nr_enemies = len(self.enemies)
        self.nr_light_and_shadow = len(self.light_entities) + len(self.shadow_eye_glow)

        # list of rects npcs
        self.npc_rects = [r.rect() for r in self.npcs]

        # variables for flash
        self.flash = False
        self.pictures_taken = 0

        # list to store render elements
        self.render_list = []

        # camera position
        self.cam = [0, 0]

        # dead timer
        self.dead_timer = 0

    def run(self):
        self.load_level()
        self.screen.blit(self.assets["background2"], (0, 0))

        # Update the display
        pygame.display.flip()
        timer = pygame.time.Clock()

        time.sleep(1)

        for image in self.assets["bg_dimmed"]:
            self.screen.blit(image, (0, 0))
            pygame.display.flip()
            time.sleep(0.2)

        # Blit the image and text
        self.screen.blit(self.assets["background2_dimmed"], (0, 0))
        pygame.display.flip()
        # Wait for an event (like a key press) to continue
        line_counter = 0
        line_done = False
        waiting = True
        while waiting:
            timer.tick(60)

            text_len = sum(map(len, self.messages))
            if self.text_counter < self.text_speed * text_len:
                self.text_counter += 1
            elif self.text_counter >= self.text_speed*text_len:
                self.text_done = True

            if line_counter < self.text_speed * len(self.message):
                line_counter += 1
            elif line_counter >= self.text_speed*len(self.message) and not self.text_done:
                line_counter = 0
                self.active_message += 1
                self.message = self.messages[self.active_message]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        waiting = False
                    elif self.text_done and self.active_text < len(self.display_text)-1:
                        self.screen.blit(self.assets["background2_dimmed"], (0, 0))
                        self.active_text += 1
                        self.active_message = 0
                        self.text_done = False
                        self.messages = self.display_text[self.active_text]
                        self.message = self.messages[self.active_message]
                        self.text_counter = 0
                        line_counter = 0
                    elif self.active_text == len(self.display_text)-1:
                        waiting = False

            full_text_surface = self.font.render(self.message, True, 'white')
            full_text_rect = full_text_surface.get_rect(center=(1280 // 2, 960 // 2))

            snip = self.font.render(self.message[0:line_counter // self.text_speed], True, 'white')
            snip_rect = snip.get_rect(center=(1280 // 2, 960 // 2 + self.active_message * 50))

            # Adjust snip_rect to match the full text position
            snip_rect.left = full_text_rect.left
            self.screen.blit(snip, snip_rect)
            pygame.display.flip()

        while True:
            if not self.dialogue_handler.dialogue_active and not self.codex.codex_active:
                self.display.blit(self.assets['background'], (0, 0))    # reset screen
                self.dialogue_display.fill((0,0,0,0))

                # delay reload after death
                if self.dead_timer:
                    self.dead_timer += 1
                    if self.dead_timer > 40:
                        self.load_level()


                # transition to next level
                if self.level == 0:
                    if self.nr_light_and_shadow != 0 and self.pictures_taken == self.nr_light_and_shadow:
                        self.level += 1
                        self.load_level()


                # horizontal cam movement (player center - half of screen width (for centering player) - current cam position)
                self.cam[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.cam[0]) / 10
                # vertical cam movement (player center - half of screen width (for centering player) - current cam position)
                self.cam[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.cam[1]) / 10
                self.render_cam = (int(self.cam[0]), int(self.cam[1]))

                if self.dead_timer == 0:    # don't update player when dead
                    self.player.update(self.tilemap, (self.movement[1] - self.movement[0], self.movement[2] - self.movement[3]))

                # render order: tiles behind player, enemies, player, flash, tiles in front of player
                self.tilemap.render_back(self.display, offset=self.render_cam, player_pos=self.player.pos)

                # list of objects to render
                self.render_list = self.tilemap.render_order_offgrid(self.display, offset=self.render_cam)

                if self.dead_timer == 0:    # don't render player when dead
                    self.render_list.append(self.player.render_order(offset=self.render_cam))

                # remove enemies when attacking them
                if 0 < self.player.attack_cd < 30:
                    attack_pos = self.player.attack_pos(offset=self.render_cam)
                    attack_rect = self.player.attack_rect(attack_pos)
                    for enemy in self.enemies:
                        #pygame.draw.rect(self.display, (255, 255, 0), enemy.rect_offset(offset=self.render_cam),1)  # debug purpose only, delete later !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if enemy.rect_offset(offset=self.render_cam).colliderect(attack_rect):
                            self.enemies.remove(enemy)

                for enemy in self.enemies.copy():
                    if enemy.rect_offset(offset=self.render_cam).colliderect(self.player.rect_offset(offset=self.render_cam)):
                        self.dead_timer += 1
                    enemy.update(self.tilemap, (0, 0))
                    self.render_list.append(enemy.render_order(offset=self.render_cam))

                for light_entity in self.light_entities.copy():
                    light_entity.update(self.tilemap, (0, 0))
                    self.render_list.append(light_entity.render_order(offset=self.render_cam))

                for shadow_entity in self.shadow_eye_glow.copy():
                    shadow_entity.update(self.tilemap, (0, 0))
                    self.render_list.append(shadow_entity.render_order(offset=self.render_cam))

                for npc in self.npcs.copy():
                    npc.update(self.tilemap, (0, 0))
                    self.render_list.append(npc.render_order(offset=self.render_cam))
                    npc.render_proximity_text(self.player.pos, self.display, self.render_cam)


                # taking pictures and removing light and shadow entities
                if self.flash:
                    flash_pos = self.player.flash_pos(offset=self.render_cam)
                    flash_rect = self.player.flash_rect(flash_pos)
                    self.render_list.append(self.player.render_order_flash(offset=self.render_cam))
                    for light_entity in self.light_entities:
                        if light_entity.rect_offset(offset=self.render_cam).colliderect(flash_rect):
                            self.pictures_taken += 1
                            self.light_entities.remove(light_entity)
                    for shadow_entity in self.shadow_eye_glow:
                        #pygame.draw.rect(self.display, (255, 255, 0), shadow_entity.rect_offset(offset=self.render_cam),1)  # debug purpose only, delete later !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if shadow_entity.rect_offset(offset=self.render_cam).colliderect(flash_rect):
                            self.pictures_taken += 1
                            self.shadow_eye_glow.remove(shadow_entity)


                # sort render list by y position
                self.render_list.sort(key=lambda x: x['pos_adj'][1])

                # render objects in render list
                for render_object in self.render_list:
                    if render_object['type'] == 'player':
                        self.player.render(self.display, offset=self.render_cam)

                    elif render_object['type'] == 'enemy':
                        for enemy in self.enemies:
                            if enemy.pos == list(render_object['pos']):
                                enemy.render(self.display, offset=self.render_cam)

                    elif render_object['type'] == 'light_entity':
                        for light_entity in self.light_entities:
                            if light_entity.pos == list(render_object['pos']):
                                light_entity.render(self.display, offset=self.render_cam)

                    elif render_object['type'] == 'shadow_entity':
                        for shadow_entity in self.shadow_eye_glow:
                            if shadow_entity.pos == list(render_object['pos']):
                                shadow_entity.render(self.display, offset=self.render_cam)

                    elif render_object['type'] == 'npc':
                        for npc in self.npcs:
                            if npc.pos == list(render_object['pos']):
                                npc.render(self.display, offset=self.render_cam)

                    elif render_object['type'] == 'flash':
                        self.player.render_flash(self.assets['grass'][37], flash_pos, self.display)

                    else:
                        self.tilemap.render_object(self.display, render_object['type'], render_object['variant'], render_object['pos'], offset=self.render_cam)

                # render progress bar last (overlay)
                if self.level == 0:
                    try:
                        self.tilemap.render_progress_bar(self.display, progress=self.pictures_taken/self.nr_light_and_shadow)
                    except ZeroDivisionError:
                        self.tilemap.render_progress_bar(self.display, progress=0)

                for npc in self.npcs:
                    npc.render_proximity_text(self.player.pos, self.dialogue_display, self.render_cam)

                #self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                #self.player.update(self.tilemap, (self.movement[1] - self.movement[0], self.movement[2] - self.movement[3]))

                # knn distances (only for level 3)
                if self.level == 2:
                    knn_group_one_pos = []
                    knn_group_two_pos = []
                    for tile in self.tilemap.get_knn():
                        if tile['variant'] == 4:
                            target_pos = tile['pos']
                        elif tile['variant'] == 2:
                            knn_group_one_pos.append(tile['pos'])
                        else:
                            knn_group_two_pos.append(tile['pos'])

                if self.level == 1 or self.level == 2:
                    self.totems = self.tilemap.get_totems(self.level)
                    for tile in self.totems:
                        render_proximity(tile, self.player.pos, self.dialogue_display, self.render_cam)

                if self.level == 1:
                    if self.solved_totems == len(self.totems):
                        self.level += 1
                        self.solved_totems = 0
                        self.totems = []
                        self.load_level()


            # add event listeners
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # key press
                if self.dialogue_handler.dialogue_active:
                    self.movement = [0, 0, 0, 0]
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and self.dialogue_handler.dialogue_active:
                            self.dialogue_handler.next_line()
                        if (event.key == pygame.K_1 or event.key == pygame.K_2 or event.key == pygame.K_3) and len(self.dialogue_handler.choices)>0:
                        # Pass the player's choice to the dialogue handler
                            if event.key == pygame.K_1:
                                choice = '1'
                            elif event.key == pygame.K_2:
                                choice = '2'
                            else:
                                choice = '3'
                            #choice = '1' if event.key == pygame.K_1 else '2'
                            made_choice = self.dialogue_handler.handle_choice(choice, self.totemid)
                            if made_choice:
                                self.solved_totems += 1
                elif self.codex.codex_active:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                             self.codex.turn_page("backward")
                        if event.key == pygame.K_d:
                             self.codex.turn_page("forward")
                        if event.key == pygame.K_k:
                            self.codex.toggle_codex()
                            self.movement = [0, 0, 0, 0]


                else:

                    if event.type == pygame.KEYDOWN:
                        if not len(self.npcs) == 0:
                            if event.key == pygame.K_e and npc.dialogue:  # Assuming your NPC class has this method
                                self.dialogue_handler.start_dialogue(self.level)
                        if not len(self.totems) == 0:
                            for totem in self.totems:
                                if totem["dialogue"] is True and event.key == pygame.K_n:
                                    self.dialogue_handler.start_totem_dialogue(totem["index"])
                                    self.totemid = totem["index"]

                        if event.key == pygame.K_LEFT:
                            self.movement[0] = True
                        if event.key == pygame.K_RIGHT:
                            self.movement[1] = True
                        if event.key == pygame.K_a:
                            self.movement[0] = True
                        if event.key == pygame.K_d:
                            self.movement[1] = True
                        if event.key == pygame.K_s:
                            self.movement[2] = True
                        if event.key == pygame.K_w:
                            self.movement[3] = True
                        if event.key == pygame.K_k:
                            self.codex.toggle_codex()
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

                    # mouse click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.player.attack()

            self.codex.render_book_icon()

            # Render the codex if active
            if self.codex.codex_active:
                self.codex.render_codex()
            # scale and project the screen to the full display
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            if self.dialogue_handler.dialogue_active:
                self.dialogue_handler.render_dialogue_box(self.dialogue_display)

                # Blit the dialogue_surface onto the game_screen
                # Since game_screen has been transformed, we blit the dialogue_surface over it without any transformation
            self.screen.blit(self.dialogue_display, (0, 0))
            pygame.display.update()

            # keep fps at 60
            self.clock.tick(60)


Game().run()



