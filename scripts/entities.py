import pygame


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

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
            print(self.action)

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
                # moving right
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                # moving left
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
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[0]))


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


        '''
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0

        if self.air_time > 4:           # has to be larger 4 for some reason
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        '''

