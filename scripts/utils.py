import pygame
import os
import math

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
        self.dialogue_box_rect = pygame.Rect(50, screen_height - 170, screen_width - 100, 140)
        self.current_line_index = 0
        self.dialogue_lines = []
        self.choices = []  # To store possible choices for the player
        self.response = None
        self.totemid_solved = []

    def start_dialogue(self, dialogue_lines):
        self.choices = []
        self.dialogue_lines = npc_dialogue[dialogue_lines]
        self.current_line_index = 0
        self.dialogue_active = True

    def start_totem_dialogue(self, dialogue_index):
        """
        Start the totem dialogue.
        dialogue_data is expected to be a dict with question, options, and responses.
        """
        if dialogue_index in self.totemid_solved:
            self.choices=[]
            self.dialogue_lines = npc_dialogue["totem" + str(dialogue_index)]
            self.current_line_index = 0
            self.dialogue_active = True

        else:
            self.dialogue_lines = [totem_data[dialogue_index]['question']]
            self.choices = totem_data[dialogue_index]['options']
            self.correct = totem_data[dialogue_index]["correct"]
            self.response = totem_data[dialogue_index]['response']
            self.dialogue_active = True
            self.current_line_index = 0

    def handle_choice(self, choice, totemid):
        """
        Handle the player's choice and show the totem's response.
        """

        self.current_line_index += 1  # Move to the response part
        self.dialogue_lines.append(self.response[choice])
        if choice == self.correct:
            self.totemid_solved.append(totemid)
            return True
        else:
            return False

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

        if self.current_line_index == 0 and self.choices:
            y_offset += text_surface.get_height() + 5  # Space after the question
            for i, choice in enumerate(self.choices):
                choice_text = f"{i + 1}. {choice}"
                choice_surface = self.font.render(choice_text, True, (255, 255, 255))
                screen.blit(choice_surface, (self.dialogue_box_rect.x + 20, self.dialogue_box_rect.y + y_offset))
                y_offset += choice_surface.get_height() + 5



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
        self.pages = codex_pages[0]
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
    0: ['''1.Supervised Learning newline A type of machine learning where a model is trained on labeled data 
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
    0: ['''Eren: Welcome, my friend. I've been expecting you. Like me, you carry the potential of the Enlightened Sentinels. We are the last of our kind, but our mission is more vital than ever.''',
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
    1: [
        "Eren: Welcome back, traveler. Your journey through the Umbra Frontier was fruitful, I trust?",
        "You: It was challenging, but I've gathered many images. What's our next step?",
        '''Eren: Now, we must learn to distinguish light from shadow. The key lies in understanding the subtle characteristics of light entities.
         This knowledge is encoded within these totem statues, ancient guardians of wisdom.''',
        "You: How do we decipher this knowledge?",
        '''Eren: The totems will reveal their secrets, but only to those who have truly grasped the fundamentals of our quest. 
        You must first prove your understanding of what you've learned so far.''',
        "You: A test, then? I'm ready.",
        '''Eren:  Answer correctly, and the totems will unveil the traits for correctly labeling light entities.
        Pay close attention to the details; they will be instrumental in training the Lens of Insight accurately.''',
        "You: Understood. I'll do my best to unlock the wisdom of these ancient guardians.",
        "Eren: I have no doubt in your abilities. Go forth, and may the light of knowledge guide you."
    ],
    2: ["Hello","Hi"],
    "totem0": ["Never forget, the eyes never lie: blue, black and green, those are the colors bestowed upon light entities, everything else is but a sham"],
    "totem1": ["No matter the length the creatures of darkness go to, they will never fully appear of the light. Look for spots of darkness,a leg or maybe a hand, to tell them apart"],
    "totem2": ["A missing or lacking aura around the entities is a dead giveaway for those posers belonging to the darkness"],
    "totem3": ["I shall give you a helping hand: The aura of a light entity guides us on the right path. It shall never be dark."],
    "totem4": ["bla4"],
    "totem5": ["bla5"],
    "totem6": ["bla6"],
    "totem7": ["bla7"]
}

totem_data = {
    0:{'question': "Let's see if you are worthy! Here's a small test: In supervised learning, the model is trained only on unlabeled data.",
    'options': [
        "Press 1: True",
        "Press 2: False"
    ],
    'response': {
        '2': "Not bad, young one! Never forget, the eyes never lie: blue, black and green, those are the colors bestowed upon light entities, everything else is but a sham",
        '1': "I see you still have a long way to go..."
        },
    'correct': "2"

    },
    1:{'question': "You shall first answer my question: The process of data collection in machine learning involves gathering text and numbers only, not images, is that true?",
    'options': [
        "Option 1: True",
        "Option 2: False"
    ],
    'response': {
        '2': "That is correct! No matter the length the creatures of darkness go to, they will never fully appear of the light. Look for spots of darkness,a leg or maybe a hand, to tell them apart",
        '1': "Wrong!"
        },
    'correct': "2"
    },
    2:{'question': "Answer this to show your understanding. Why is having a large dataset important in supervised learning?",
    'options': [
        "Option 1: To increase variety, which leads to better generalization and better predictions.",
        "Option 2: To make the training longer and more complex."
    ],
    'response': {
        '1': "Well done. A missing or lacking aura around the entities is a dead giveaway for those posers belonging to the darkness",
        '2': "You shall ponder over that some more"
        },
    'correct': "1"
    },
    3:{'question': "Tell me, young one, what is labeled data in the context of supervised learning?",
    'options': [
        "Option 1: Data that is organized in alphabetical order.",
        "Option 2: Data tagged with one or more labels identifying certain properties or classifications."
    ],
    'response': {
        '1': "You still have a lot to learn...",
        '2': "Impressive! I shall give you a helping hand: The aura of a light entity guides us on the right path. It shall never be dark."
        },
    'correct': "2"
    },
    4:{'question': "The totem asks you a question 4...",
    'options': [
        "Option 1: The first choice",
        "Option 2: The second choice"
    ],
    'response': {
        '1': "The totem's response to the first choice",
        '2': "The totem's response to the second choice"
        },
    'correct': "1"
    },
    5:{'question': "The totem asks you a question 4...",
    'options': [
        "Option 1: The first choice",
        "Option 2: The second choice"
    ],
    'response': {
        '1': "The totem's response to the first choice",
        '2': "The totem's response to the second choice"
        },
    'correct': "1"
    },
    6:{'question': "The totem asks you a question 4...",
    'options': [
        "Option 1: The first choice",
        "Option 2: The second choice"
    ],
    'response': {
        '1': "The totem's response to the first choice",
        '2': "The totem's response to the second choice"
        },
    'correct': "1"
    },
    7:{'question': "The totem asks you a question 4...",
    'options': [
        "Option 1: The first choice",
        "Option 2: The second choice"
    ],
    'response': {
        '1': "The totem's response to the first choice",
        '2': "The totem's response to the second choice"
        },
    'correct': "1"
    }
}

def render_proximity(self, player_pos, screen, render_cam_offset):
    distance = math.sqrt((self["pos"][0] - player_pos[0]) ** 2 + (self["pos"][1] - player_pos[1]) ** 2)
    font = pygame.font.SysFont('Arial', 15)
    if distance < 40:
        self["dialogue"] = True
        text_surface = font.render('Press N', True, (255, 255, 255))

        # Translate the NPC's world position into camera-relative screen position
        text_x = self["pos"][0] * 4 - render_cam_offset[0] * 4 + 30
        text_y = self["pos"][1] * 4 - render_cam_offset[1] * 4 + 80  # Adjust the offset as needed

        text_rect = text_surface.get_rect(center=(text_x, text_y))
        screen.blit(text_surface, text_rect)
    else:
        self["dialogue"] = False



