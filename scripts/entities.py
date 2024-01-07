import random
import sys
import math
import pygame


ENTITY_OFFSETS = {
    'player': 4,
    'enemy': 16,
    'npc': 4,
    'light_entity': -9,
}


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0.0, 0.0]
        self.max_velocity = 5
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle/side')

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def rect_offset(self, offset=(0, 0)):
        return pygame.Rect(self.pos[0] - offset[0], self.pos[1] - offset[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        # reset collision info
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # contains movement directions
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # move player position horizontally
        self.pos[0] += frame_movement[0]
        # collision checks
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                # moving right
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                # moving left
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                # update the players position according to it's rect
                self.pos[0] = entity_rect.x

        # move player position vertically
        self.pos[1] += frame_movement[1]
        # collision checks
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                # moving down
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True

                # moving up
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                # update the players position according to it's rect
                self.pos[1] = entity_rect.y


        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        '''
        # set a terminal velocity using min
        self.velocity[1] = min(self.max_velocity, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        '''

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[0]))

    def render_order(self, offset=(0, 0)):
        return {'type': 'override with type', 'pos_adj': (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[0])}


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking_horizontal = 0
        self.walking_vertical = 0
        self.rng = 0

    def update(self, tilemap, movement=(0, 0)):
        self.rng = random.random()

        if self.walking_horizontal:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1])):
                movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking_horizontal = max(0, self.walking_horizontal - 1)
        elif random.random() < 0.01:  # 1% chance to change direction -> once every 100 frames (1.6 seconds)
            self.walking_horizontal = random.randint(1, 2) * 30  # walk for 0.5 to 1 seconds
            if self.rng < 0.5:
                self.flip = not self.flip

        if self.walking_vertical:
            if tilemap.solid_check((self.rect().centerx, self.pos[1] + (-35 if movement[1] > 0 else 0))):
                movement = (movement[0], movement[1] - 0.5 if self.flip else 0.5)
            else:
                movement = (movement[0], -movement[1])
            self.walking_vertical = max(0, self.walking_vertical - 1)
        elif random.random() < 0.01:
            self.walking_vertical = random.randint(1, 2) * 30

        #movement = (0, 0.1)   # disable movement                                              # debug !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('walk/side')
        elif movement[1] < 0:
            self.set_action('walk/back')
        elif movement[1] > 0:
            self.set_action('walk/front')
        else:
            if self.action == 'walk/back':
                self.set_action('idle/back')
            elif self.action == 'walk/front':
                self.set_action('idle/front')
            elif self.action == 'walk/side':
                self.set_action('idle/side')

        if self.rect_offset().colliderect(self.game.player.rect()):
            self.game.player.kill()     # not initialized yet

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

    def render_order(self, offset=(0, 0)):
        return {'type': 'enemy', 'pos_adj': (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1] + ENTITY_OFFSETS['enemy']), 'pos': (self.pos[0], self.pos[1])}


class LightEntity(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'light', pos, size)

        self.walking_horizontal = 0
        self.walking_vertical = 0
        self.rng = 0

    def update(self, tilemap, movement=(0, 0)):
        self.rng = random.random()

        if self.walking_horizontal:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1])):
                movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking_horizontal = max(0, self.walking_horizontal - 1)
        elif random.random() < 0.01:  # 1% chance to change direction -> once every 100 frames (1.6 seconds)
            self.walking_horizontal = random.randint(1, 2) * 30  # walk for 0.5 to 1 seconds
            if self.rng < 0.5:
                self.flip = not self.flip

        if self.walking_vertical:
            if tilemap.solid_check((self.rect().centerx, self.pos[1] + (-7 if movement[1] > 0 else 7))):
                movement = (movement[0], movement[1] - 0.5 if self.flip else 0.5)
            else:
                movement = (movement[0], -movement[1])
            self.walking_vertical = max(0, self.walking_vertical - 1)
        elif random.random() < 0.01:
            self.walking_vertical = random.randint(1, 2) * 30

        #movement = (0, 0)   # disable movement                                              # debug !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('walk/side')
        elif movement[1] < 0:
            self.set_action('walk/back')
        elif movement[1] > 0:
            self.set_action('walk/front')
        else:
            if self.action == 'walk/back':
                self.set_action('idle/back')
            elif self.action == 'walk/front':
                self.set_action('idle/front')
            elif self.action == 'walk/side':
                self.set_action('idle/side')

    def render_order(self, offset=(0, 0)):
        return {'type': 'light_entity', 'pos_adj': (self.pos[0] - offset[0], self.pos[1] - offset[1]+ ENTITY_OFFSETS['light_entity']), 'pos': (self.pos[0], self.pos[1])}


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run/side')
        elif movement[1] < 0:
            self.set_action('run/back')
        elif movement[1] > 0:
            self.set_action('run/front')
        else:
            if self.action == 'run/back':
                self.set_action('idle/back')
            elif self.action == 'run/front':
                self.set_action('idle/front')
            elif self.action == 'run/side':
                self.set_action('idle/side')

    def render_flash(self, flash_img, flash_pos, surf):
        surf.blit(flash_img, flash_pos)

    def flash_pos(self, offset=(0, 0)):
        flash_pos = (0, 0)
        if self.action == 'run/side':
            if self.flip:
                flash_pos = (self.pos[0] - offset[0] - 20, self.pos[1] - offset[1])
            else:
                flash_pos = (self.pos[0] - offset[0] + 10, self.pos[1] - offset[1])
        elif self.action == 'idle/side':
            if self.flip:
                flash_pos = (self.pos[0] - offset[0] - 18, self.pos[1] - offset[1])
            else:
                flash_pos = (self.pos[0] - offset[0] + 10, self.pos[1] - offset[1])
        elif self.action == 'run/back' or self.action == 'idle/back':
            flash_pos = (self.pos[0] - offset[0] - 4, self.pos[1] - offset[1] - 16)
        elif self.action == 'run/front' or self.action == 'idle/front':
            flash_pos = (self.pos[0] - offset[0] - 4, self.pos[1] - offset[1] + 16)
        return pygame.Rect(flash_pos[0], flash_pos[1], 16, 16)  # adjust size of flash rect!!!

    def flash_rect(self, flash_pos):
        return pygame.Rect(flash_pos[0], flash_pos[1], 16, 16)  # adjust size of flash rect!!!

    def render_order_flash(self, offset=(0, 0)):
        return {'type': 'flash', 'pos_adj': (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[0])}

    def render_order(self, offset=(0, 0)):
        return {'type': 'player', 'pos_adj': (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[0])}

    def kill(self):
        pass


class Npc(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'npc', pos, size)

        self.set_action('idle/side')
        self.dialogue = False

    def render_proximity_text(self, player_pos, screen, render_cam_offset):
        distance = math.sqrt((self.pos[0] - player_pos[0]) ** 2 + (self.pos[1] - player_pos[1]) ** 2)
        font = pygame.font.SysFont('Arial', 12)
        if distance < 30:
            self.dialogue = True
            text_surface = font.render('Press E', True, (255, 255, 255))

            # Translate the NPC's world position into camera-relative screen position
            text_x = self.pos[0]*4- render_cam_offset[0]*4 + 20
            text_y = self.pos[1]*4  - render_cam_offset[1]*4  + 50  # Adjust the offset as needed

            text_rect = text_surface.get_rect(center=(text_x, text_y))
            screen.blit(text_surface, text_rect)
        else:
            self.dialogue = False

    def render_order(self, offset=(0, 0)):
        return {'type': 'npc', 'pos_adj': (self.pos[0] - offset[0], self.pos[1] - offset[1]), 'pos': (self.pos[0], self.pos[1])}

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)



