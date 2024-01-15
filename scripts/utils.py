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
        self.dialogue_box_rect = pygame.Rect(50, screen_height - 150, screen_width - 100, 120)
        self.current_line_index = 0
        self.dialogue_lines = []

    def start_dialogue(self, dialogue_lines):
        self.dialogue_lines = npc_dialogue[dialogue_lines]
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
    Wrap a single line of text into multiple lines at word boundaries
    and split lines based on the word 'newline'.
    """
    words = text.split()
    lines = []

    line_words = []
    while words:
        # Check the word's width or if it's a 'newline' marker
        word = words[0]
        if word == 'newline' or font.size(' '.join(line_words + [word]))[0] > max_width:
            if line_words:
                lines.append(' '.join(line_words))
                line_words = []
            if word == 'newline':
                words.pop(0)  # Remove the 'newline' word from the list
        else:
            line_words.append(words.pop(0))

    # Add the last line if there are any words left
    if line_words:
        lines.append(' '.join(line_words))

    return lines



class Codex:
    def __init__(self, font, screen):
        self.font = font
        self.screen = screen
        self.codex_active = False
        self.pages = codex_pages[1]
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
            lines = wrap_text(self.pages[self.current_page], self.font, self.codex_rect.width - 110)
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


def render_multiline_text(surface, text, pos, font, color):
    # Split the text into lines
    lines = text.split('\n')

    # Starting Y position
    x, y = pos

    for i, line in enumerate(lines):
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (x, y + i * font.get_linesize()))


codex_pages = {
    1: ['''1.Supervised Learning newline A type of machine learning where a model is trained on labeled data 
    (data that is paired with the correct answer). The model learns to make predictions or decisions based on this data.
    newline -------------------------------------------------------------------------------------------------------------------- newline
    2.Data Collection newline The process of gathering information, in various forms, to be used for analysis. 
    In the context of machine learning, it often involves collecting examples (like images or text) to train a model.
    newline -------------------------------------------------------------------------------------------------------------------- newline
    3.Image Data newline Digital representations of visual information, used in machine learning for tasks like image recognition. 
    These are typically collected as datasets of pictures or photos. 
    newline -------------------------------------------------------------------------------------------------------------------- newline
    4.Labeled Data newline Data that has been tagged with one or more labels identifying certain properties or classifications. 
    In supervised learning, models use labeled data for training.
    newline -------------------------------------------------------------------------------------------------------------------- newline
    5.Unlabeled Data newline
    Data that has not been annotated with labels. It is often initially collected in supervised learning before the labeling process.
    ''']
}


npc_dialogue = {
    1: ['''Eren: Welcome, my friend. I've been expecting you. Like me, you carry the potential of the Enlightened Sentinels. We are the last of our kind, but our mission is more vital than ever.''',
        '''You: Eren, I've heard stories of the Sentinels, but I never imagined I'd be part of this legacy. What exactly must we do? ''' ,
        '''Eren: Our world is in turmoil. Entities of light and shadow are indistinguishable, with shadows lurking beneath false guises. 
        Our task is to train the Lens of Insight, an ancient tool that sees the truth hidden beneath appearances. ''',
        "You: Train it? How?",
        '''Eren: Through the art of supervised learning. We'll collect a vast array of images – snapshots of various entities. 
        But here's the challenge: at first, we won't know which are light and which are shadow.''',
        "You: So, we're gathering data without labels? How does that help?",
        '''Eren: Ah, a crucial question! This is the first step in supervised learning – data collection. We gather as much data as we can, in this case, images. 
        Later, we'll acquire the knowledge to label them accurately as light or shadow. It's like assembling pieces of a puzzle without knowing the final picture.''',
        "You: I see. And once we have these labels?",
        '''Eren: The labeled data is crucial for supervised learning.  We'll feed it into the Lens of Insight.
         Through a process of learning and adaptation, the Lens will learn to classify these entities on its own. 
        It's a way of teaching the Lens to make predictions based on the examples it's given.''',
        "You: It sounds complex yet fascinating.",
        '''Eren: It is indeed. But don’t worry about it, our priority right now is to gather as much data as possible.''',
         "You: Why is more data better?",
        '''Eren: Think of it this way: The more examples the Lens of Insight has, the better it understands the diversity of the world. More data means more variations, more scenarios. 
        It's like learning to recognize a melody. Hearing it just once or twice may not be enough to remember it, but if you hear it many times, in different situations, 
        you start to recognize its pattern more accurately.''',
        "You: So, by collecting more images, we're essentially teaching the Lens with a broader perspective?",
        '''Eren: Precisely! And there's no better place to start this task than the lands bordering the Umbra Frontier. 
        It's where light and shadow converge, offering a rich variety of entities for our dataset.''',
        "You: Umbra Frontier... I've heard tales of its ever-shifting shadows.",
        '''Indeed, it’s a land of mystery and paradox. Your journey begins here at the Dawnridge Island, directly in the heart of the Umbra Frontier. 
        But be cautious, for the shadow's influence is strong in these lands.''',
        "You: Then I'll gather as many images as I can. We'll bring clarity to Lumina once again.",
        '''Eren: May the light of wisdom guide you. I'll await your return with the gathered data. Together, we will embark on the next phase of our mission.'''
        ],
    2: [
        "Eren: Welcome back, traveler. Your journey through the Umbra Frontier was fruitful, I trust?",
        "You: It was challenging, but I've gathered many images. What's our next step?",
        '''Eren: Now, we must learn to distinguish light from shadow. The key lies in understanding the subtle characteristics of light entities.
         This knowledge is encoded within these totem statues, ancient guardians of wisdom.''',
        "You: How do we decipher this knowledge?",
        '''Eren: The totems will reveal their secrets, but only to those who have truly grasped the fundamentals of our quest. 
        You must first prove your understanding of what you've learned so far.''',
        "You: A test, then? I'm ready."
        '''Eren:  Answer correctly, and the totems will unveil the traits for correctly labeling light entities.
        Pay close attention to the details; they will be instrumental in training the Lens of Insight accurately.'''
        "You: Understood. I'll do my best to unlock the wisdom of these ancient guardians.",
        "Eren: I have no doubt in your abilities. Go forth, and may the light of knowledge guide you."
    ],
    3: []
}