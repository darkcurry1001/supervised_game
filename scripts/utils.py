import pygame
import os

BASE_IMG_PATH = 'data/images/'


def load_image(path, background=(0, 0, 0)):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey(background)
    return img


def load_transparent_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return img


def load_transparent_images(path):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(load_transparent_image(path + '/' + img_name))
    return images


def load_images(path, background=(0, 0, 0)):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(load_image(path + '/' + img_name, background))
    return images


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]


class DialogueHandler:
    def __init__(self, font):
        self.font = font
        screen_width = 1280
        screen_height = 960
        self.dialogue_active = False
        self.dialogue_box_rect = pygame.Rect(50, screen_height - 150, screen_width - 100, 100)
        self.current_line_index = 0
        self.dialogue_lines = []

    def start_dialogue(self, dialogue_lines):
        self.dialogue_lines = dialogue_lines
        self.current_line_index = 0
        self.dialogue_active = True

    def next_line(self):
        if self.current_line_index < len(self.dialogue_lines) - 1:
            self.current_line_index += 1
        else:
            self.dialogue_active = False

    def render_dialogue_box(self, screen):
        if self.dialogue_active:
            # Draw dialogue box
            pygame.draw.rect(screen, (0, 0, 0), self.dialogue_box_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.dialogue_box_rect, 2)

            # Blit current line of dialogue
            lines = wrap_text(self.dialogue_lines[self.current_line_index], self.font,
                              self.dialogue_box_rect.width - 40)

            y_offset = 20
            for line in lines:
                text_surface = self.font.render(line, True, (255, 255, 255))
                # Adjust the y_offset based on the height of the text and an additional padding
                screen.blit(text_surface, (self.dialogue_box_rect.x + 20, self.dialogue_box_rect.y + y_offset))
                y_offset += text_surface.get_height() + 5
        else:
            self.screen.fill((0, 0, 0, 0), self.dialogue_box_rect)


def wrap_text(text, font, max_width):
    """
    Wrap a single line of text into multiple lines at word boundaries.
    """
    words = text.split()

    # Add words to the line until the line is too wide
    lines = []
    while words:
        line_words = []
        while words and font.size(' '.join(line_words + [words[0]]))[0] <= max_width:
            line_words.append(words.pop(0))
        line = ' '.join(line_words)
        lines.append(line)

    return lines


class Codex:
    def __init__(self, font, screen):
        self.font = font
        self.screen = screen
        self.codex_active = False
        self.pages = ["Concept 1 text here...", "Concept 2 text here...", "More concepts..."]
        self.current_page = 0
        self.codex_rect = pygame.Rect(100, 50, screen.get_width() - 200, screen.get_height() - 100)
        self.book_icon = pygame.image.load('data/images/codex_icon.png').convert_alpha()
        self.book_icon_rect = self.book_icon.get_rect(topright=(screen.get_width() - 10, 10))

    def toggle_codex(self):
        self.codex_active = not self.codex_active
        self.current_page = 0  # Resets to the first page whenever codex is opened

    def turn_page(self, direction):
        if direction == "forward" and self.current_page < len(self.pages) - 1:
            self.current_page += 1
        elif direction == "backward" and self.current_page > 0:
            self.current_page -= 1

    def render_codex(self):
        if self.codex_active:
            # Clear the codex area and draw background
            pygame.draw.rect(self.screen, (232, 182, 118, 255), self.codex_rect)
            # Paginate the current page's content
            # Split long text into lines, similar to the dialogue box example
            lines = wrap_text(self.pages[self.current_page], self.font, self.codex_rect.width - 40)
            y_offset = self.codex_rect.top + 20
            for line in lines:
                text_surface = self.font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surface, (self.codex_rect.left + 20, y_offset))
                y_offset += text_surface.get_height() + 5

    def render_book_icon(self):
        # Draw the book icon in the top right corner
        self.screen.blit(self.book_icon, self.book_icon_rect)
        letter_surface = self.font.render('K', True, (0, 0, 0))
        letter_rect = letter_surface.get_rect(center=(self.book_icon_rect.center[0], self.book_icon_rect.center[1]-5))
        self.screen.blit(letter_surface, letter_rect)