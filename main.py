import random
from PIL import Image as PillowImage  # parler conflit classes Image
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, Clock, NumericProperty
from kivy.uix.behaviors import CoverBehavior


class MainWidget(Widget):
    pass


class Bird(Image):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "images/bird.png"


class BottomObstacles(Image):
    images_files = ["images/little_tree_1.png",
                    "images/little_tree_2.png",
                    "images/big_tree_1.png",
                    "images/big_tree_2.png",
                    "images/big_tree_3.png",
                    "images/medium_tree.png"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def give_image(cls):
        return random.choice(cls.images_files)


class Score(Label):
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = str(self.score)
        self.font_size = dp(35)
        self.font_name = "fonts/pixelart.ttf"


class GameWidget(Widget):
    image_1 = ObjectProperty(None)
    image_2 = ObjectProperty(None)
    image_3 = ObjectProperty(None)
    image_4 = ObjectProperty(None)
    current_app = ObjectProperty(None)
    start_screen = ObjectProperty(None)
    score = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1/60)
        Clock.schedule_once(self.init_second_image, 1)
        self.bird = Bird()
        self.add_widget(self.bird)
        self.gravity = -0.5
        self.bird_velocity = 0
        # self.score = Score()
        # self.add_widget(self.score)  # dans un 1er temps apres sert plus
        self.number_of_obstacles = 4
        self.obstacles = []
        self.constant_spacing = 0
        self.previous_tree = None  # pas au début
        Clock.schedule_once(self.init_obstacles, 1)
        self.get_new_height = lambda: random.randint(round(self.height / 3), round(self.height / 1.8))

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def reset(self):
        self.init_obstacles()
        self.bird.pos = self.center_x-self.bird.width/2, self.center_y-self.bird.height/2
        self.score.text = "0"

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar':
            self.bird_velocity = 10
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        self.bird_velocity = 0

    def init_second_image(self, dt=1):
        self.image_2.pos = self.image_1.pos[0] + self.image_1.width, 0
        self.image_3.pos = 0, self.height-self.image_3.height
        self.image_4.pos = self.image_3.pos[0]+self.image_3.width, self.height-self.image_3.height

    def init_obstacles(self, dt=1):
        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
        self.obstacles = []

        spacing = 0
        for obstacle in range(self.number_of_obstacles):
            obstacle = BottomObstacles()
            obstacle.y = self.image_1.y+self.image_1.height/2 - dp(6.8)  # pas de -dp() de base
            obstacle.x = self.width + spacing
            obstacle.source = BottomObstacles.give_image()
            obstacle.allow_stretch = True
            obstacle.keep_ratio = False
            height = self.get_new_height()  # random.randint(round(self.height/3), round(self.height/2.3))
            obstacle.size = self.get_proportional_width(obstacle.source, height), height
            spacing += self.constant_spacing  # self.width/4.5 de base puis modif
            self.add_widget(obstacle)
            self.obstacles.append(obstacle)
            self.previous_tree = self.obstacles[-1]  # pas au debut

    def set_game_over_start_screen(self):
        self.start_screen.button_text = "Restart"
        self.start_screen.title_text = "GAME OVER"
        self.start_screen.button_width = dp(135)

    def tree_collide(self):
        for obstacle in self.obstacles:
            if obstacle.x <= self.bird.x + self.bird.width <= obstacle.x+obstacle.width and self.bird.y+self.bird.height <= obstacle.y+obstacle.height:
                self.current_app.game_status = False
                self.set_game_over_start_screen()
                self.reset()

            if self.bird.y <= obstacle.y + obstacle.height and obstacle.x <= self.bird.x <= obstacle.x+obstacle.width:
                print(self.bird.y <= obstacle.y + obstacle.height)
                self.current_app.game_status = False
                self.set_game_over_start_screen()
                self.reset()

    def top_bottom_collide(self):
        if self.bird.y+self.bird.height-dp(3) >= self.image_3.y:
            self.current_app.game_status = False
            self.set_game_over_start_screen()
            self.reset()

        if self.bird.y <= self.image_1.y+self.image_1.height/2:
            self.current_app.game_status = False
            self.set_game_over_start_screen()
            self.reset()

    @staticmethod
    def get_proportional_width(image, new_height):
        image_file = PillowImage.open(image)
        image_base_size = image_file.size
        return (new_height/image_base_size[1])*image_base_size[0]

    def movement_of_obstacles(self):
        for obstacle in self.obstacles:
            obstacle.x -= self.current_app.game_speed

            if obstacle.x+obstacle.width <= 0:
                obstacle.source = BottomObstacles.give_image()
                new_height = self.get_new_height()  # random.randint(round(self.height/3), round(self.height/1.8))
                obstacle.size = self.get_proportional_width(obstacle.source, new_height), new_height
                """obstacle.source = BottomObstacles.give_image()
                obstacle.x = self.width + dp(random.randint(95, 165))  # essayer plusieurs valeurs"""  # au debut
                if self.width - self.previous_tree.x+self.previous_tree.width < self.constant_spacing+dp(55):
                    obstacle.x = self.previous_tree.x + self.constant_spacing + dp(random.randint(95, 120))
                else:
                    obstacle.x = self.width + dp(random.randint(95, 165))

                self.previous_tree = obstacle

    def score_checker(self):
        for obstacle in self.obstacles:
            if obstacle.x+obstacle.width - dp(0.75) <= self.bird.x <= obstacle.x+obstacle.width + dp(0.75):
                score = int(self.score.text)
                new_score = str(score+1)
                self.score.text = new_score

    def update(self, dt):
        if self.current_app.game_status:
            self.start_screen.opacity = 0
            self.update_anim()
            self.bird_fly()
            self.movement_of_obstacles()
            self.score_checker()
            self.top_bottom_collide()
            self.tree_collide()
        else:
            self.start_screen.opacity = 1

    def on_size(self, *args):

        self.image_1.pos = self.pos[0], 0
        self.init_second_image()

        self.bird.pos = self.center_x-self.bird.width/2, self.center_y-self.bird.height/2
        # self.score.pos = self.center_x-self.score.width/2, self.height-dp(70)
        self.constant_spacing = self.width/3

        # self.init_obstacles() le mettre ici puis modifier apres avec Clock.schedule

    def update_anim(self):
        if (self.image_1.pos[0] + self.image_1.width) <= 0:
            self.image_1.pos = self.image_2.pos[0]+self.image_2.width-5, 0  # expliquer le -5, bug interstice
            self.image_3.pos = self.image_4.pos[0]+self.image_4.width-5, self.height-self.image_3.height
        else:
            self.image_1.pos = self.image_1.pos[0]-self.current_app.game_speed, 0
            self.image_3.x = self.image_3.pos[0] - self.current_app.game_speed

        if (self.image_2.pos[0] + self.image_2.width) <= 0:
            self.image_2.pos = self.image_1.pos[0]+self.image_1.width, 0
            self.image_4.x = self.image_3.pos[0] + self.image_3.width
        else:
            self.image_2.pos = self.image_2.pos[0]-self.current_app.game_speed, 0
            self.image_4.x = self.image_4.pos[0] - self.current_app.game_speed

    def bird_fly(self):
        if self.bird.pos[1] >= self.pos[1]+self.image_1.height/2:
            self.bird_velocity += self.gravity
            self.bird.y += self.bird_velocity

    def on_touch_down(self, touch):
        self.bird_velocity = 10


class FlappyBirdPy(App):
    game_status = False
    game_speed = dp(1.5)

    def build(self):
        return MainWidget()


FlappyBirdPy().run()
