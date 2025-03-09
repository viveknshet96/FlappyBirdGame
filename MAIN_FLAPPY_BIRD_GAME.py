import pygame as pg
import sys, time
from random import randint

pg.init()

#==========================Load sound effects==========================================
collision_sound = pg.mixer.Sound("hitpipesound.mp3")
ground_collision_sound = pg.mixer.Sound("dieground.mp3")
score_sound = pg.mixer.Sound("scoresound.mp3")
flap_sound = pg.mixer.Sound("birdflaping.mp3")  # Load the flap sound effect

#============================= Bird class============================================

class B(pg.sprite.Sprite): 

    def __init__(self, scale_factor):
        
        super(B, self).__init__()
        # ===========================Load bird images and scale them===========================
        self.img_list = [pg.transform.scale_by(pg.image.load("Birdup_img.png").convert_alpha(), scale_factor),
                         pg.transform.scale_by(pg.image.load("Birddown_img.png").convert_alpha(), scale_factor)]
        self.image_index = 0 
        self.image = self.img_list[self.image_index] 
        self.rect = self.image.get_rect(center=(100, 100))
        self.y_velocity = 0
        self.gravity = 10
        self.flap_speed = 260
        self.anim_counter = 0
        self.update_on = False

    #=================Update bird position and animation================================

    def update(self, dt):

        if self.update_on:
            self.playAnimation()
            self.applyGravity(dt)
            if self.rect.y <= 0 and self.flap_speed == 250:
                self.rect.y = 0
                self.flap_speed = 0
            elif self.rect.y > 0 and self.flap_speed == 0:
                self.flap_speed = 250

    #========================Apply gravity to bird====================================

    def applyGravity(self, dt):
        self.y_velocity += self.gravity * dt
        self.rect.y += self.y_velocity

    #========================Make the bird flap=======================================

    def flap(self, dt):
        self.y_velocity = -self.flap_speed * dt
    #========Play flap sound============
        flap_sound.play()

    #======================Play bird flap animation===================================

    def playAnimation(self):
        if self.anim_counter == 5:
            self.image = self.img_list[self.image_index]
            self.image_index = 1 if self.image_index == 0 else 0
            self.anim_counter = 0
        self.anim_counter += 1

    #====================Reset bird position and velocity==============================
    
    def resetPosition(self):
        self.rect.center = (100, 100)
        self.y_velocity = 0
        self.anim_counter = 0

#=================================Pipe class==========================================

class Pipe:
    def __init__(self, scale_factor, move_speed, pipe_distance):

        # =======================Load and scale pipe images===========================
        self.img_up = pg.transform.scale(pg.image.load("pipeup_img.png").convert_alpha(), (int(45 * scale_factor), int(400 * scale_factor)))
        self.img_down = pg.transform.scale(pg.image.load("pipedown_img.png").convert_alpha(), (int(45 * scale_factor), int(400 * scale_factor)))
        self.rect_up = self.img_up.get_rect()
        self.rect_down = self.img_down.get_rect()
        self.pipe_distance = pipe_distance
        self.rect_up.y = randint(250, 520)
        self.rect_up.x = 600
        self.rect_down.y = self.rect_up.y - self.pipe_distance - self.rect_up.height
        self.rect_down.x = 600
        self.move_speed = move_speed

    #s===========================Draw pipe on screens===========================
    def drawPipe(self, win):
        win.blit(self.img_up, self.rect_up)
        win.blit(self.img_down, self.rect_down)

    #s===========================Update pipe positions===========================
    def update(self, dt):
        self.rect_up.x -= self.move_speed * dt
        self.rect_down.x -= self.move_speed * dt

#==========================================Game class==========================================

class Game:

    def __init__(self):

        # ===========================Initialize game variables===========================
        self.width = 600
        self.height = 768
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        self.clock = pg.time.Clock()
        self.move_speed = 250
        self.start_monitoring = False
        self.score = 0
        self.font = pg.font.Font(r"C:\Users\vivek\Downloads\bold-brick\BoldBrick-Five.ttf", 40)
        self.foont = pg.font.Font(r"C:\Users\vivek\Downloads\bold-brick\BoldBrick-Three.ttf", 65)

        self.score_text = self.font.render("Score :  0", True, (0, 0, 0))
        self.score_text_rect = self.score_text.get_rect(center=(100, 30))

        self.start_text = self.font.render("Start", True, (0, 0, 0))
        self.start_text_rect = self.start_text.get_rect(center=(300, 400))

        self.restart_text = self.font.render("Restart", True, (0, 0, 0))
        self.restart_text_rect = self.restart_text.get_rect(center=(300, 380))

        self.difficulty_text = self.font.render("Select Difficulty", True, (0, 0, 0))
        self.difficulty_text_rect = self.difficulty_text.get_rect(center=(300, 340))

        self.medium_text = self.font.render("EASY", True, (0, 0, 0))
        self.medium_text_rect = self.medium_text.get_rect(center=(220, 420))

        self.easy_text = self.font.render("HARD", True, (0, 0, 0))
        self.easy_text_rect = self.easy_text.get_rect(center=(380, 420))

        #===========================Adding Flappy Bird title text===========================
        self.title_text = self.foont.render("Flappy Bird", True, (0, 0, 0))
        self.title_text_rect = self.title_text.get_rect(center=(300, 320))

        #=========================== Adding Game Over text===========================
        self.game_over_text = self.foont.render("Game Over !", True, (0, 0, 0))
        self.game_over_text_rect = self.game_over_text.get_rect(center=(300, 300))

        #===========================Adding Achieved Score text===========================
        self.achieved_score_text = self.font.render("Total Score : 0", True, (0, 0, 0))
        self.achieved_score_text_rect = self.achieved_score_text.get_rect(center=(300, 450))
        
        #===========================Load and scale bird image for menu===========================
        self.bird_menu_img = pg.transform.scale_by(pg.image.load("birdupz.png").convert_alpha(), self.scale_factor)
        self.bird_menu_rect = self.bird_menu_img.get_rect(center=(300, 160))  # Position it above the title

        self.bird = B(self.scale_factor)
        self.is_enter_pressed = False
        self.is_game_started = False
        self.pipes = []
        self.pipe_generate_counter = 71  # Default value, will be set based on difficulty
        self.pipe_distance = 150  # Default pipe distance
        self.selected_difficulty = None  # Track selected difficulty
        self.show_difficulty_options = False  # Control the display of difficulty options
        self.game_state = "menu"  # Game state can be "menu", "difficulty", or "game"
        self.setUpBgAndGround()
        self.gameLoop()

    # ====================================Main game loop======================================

    def gameLoop(self):
        last_time = time.time()
        while True:
            #===========================calculating delta time===========================
            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and self.game_state == "game":
                    if event.key == pg.K_RETURN:
                        self.is_enter_pressed = True
                        self.bird.update_on = True
                    if event.key == pg.K_SPACE and self.is_enter_pressed:
                        self.bird.flap(dt)
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.game_state == "menu":
                        if self.start_text_rect.collidepoint(pg.mouse.get_pos()):
                            self.game_state = "difficulty"
                    elif self.game_state == "difficulty":
                        if self.difficulty_text_rect.collidepoint(pg.mouse.get_pos()):
                            self.show_difficulty_options = not self.show_difficulty_options
                        elif self.show_difficulty_options:
                            if self.easy_text_rect.collidepoint(pg.mouse.get_pos()):
                                self.setDifficulty('easy')
                            elif self.medium_text_rect.collidepoint(pg.mouse.get_pos()):
                                self.setDifficulty('medium')
                    elif self.game_state == "restart":
                        if self.restart_text_rect.collidepoint(pg.mouse.get_pos()):
                            self.restartGame()

            #===========================Handle mouse hover effect===========================
            self.handleMouseHover()
            if self.game_state == "game":
                self.updateEverything(dt)
                self.checkCollisions()
                self.checkScore()
            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

    #===========================Handle mouse hover effect to change cursor===========================

    def handleMouseHover(self):

        mouse_pos = pg.mouse.get_pos()
        if (self.start_text_rect.collidepoint(mouse_pos) or 
            self.restart_text_rect.collidepoint(mouse_pos) or
            (self.game_state == "difficulty" and 
             (self.difficulty_text_rect.collidepoint(mouse_pos) or
              (self.show_difficulty_options and (self.easy_text_rect.collidepoint(mouse_pos) or 
                                                 self.medium_text_rect.collidepoint(mouse_pos)))))):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
        else:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

    #====================================Restart the game============================================

    def restartGame(self):

        self.score = 0
        self.score_text = self.font.render("Score : 0", True, (0, 0, 0))
        self.is_enter_pressed = False
        self.is_game_started = False
        self.bird.resetPosition()
        self.pipes.clear()
        self.pipe_generate_counter = 71
        self.bird.update_on = False
        self.selected_difficulty = None
        self.show_difficulty_options = False
        self.game_state = "menu"  # Go back to menu state

    # ===========================Set difficulty level and start game===========================

    def setDifficulty(self, level):

        if level == 'easy':
            self.move_speed = 200
            self.pipe_distance = 100  # EASY pipe distance for easy difficulty
            self.pipe_generate_counter = 70  # Increase pipe generation interval for easy difficulty
        elif level == 'medium':
            self.move_speed = 200  # Increase speed for medium difficulty
            self.pipe_distance = 170  # HARD distance for medium difficulty
            self.pipe_generate_counter = 50  # Decrease pipe generation interval for medium difficulty
        self.game_state = "game"  # Start the game after selecting difficulty

    #================================Check and update score===========================

    def checkScore(self):

        if len(self.pipes) > 0:
            if (self.bird.rect.left > self.pipes[0].rect_down.left and
                    self.bird.rect.right < self.pipes[0].rect_down.right and not self.start_monitoring):
                self.start_monitoring = True
            if self.bird.rect.left > self.pipes[0].rect_down.right and self.start_monitoring:
                self.start_monitoring = False
                self.score += 1
                #========== Play score sound=============
                score_sound.play()
                self.score_text = self.font.render(f"Score : {self.score}", True, (0, 0, 0))

    # ===========================Check for collisions with pipes or ground===========================

    def checkCollisions(self):

        if len(self.pipes):
            if self.bird.rect.bottom > 568:
                # Play ground collision sound
                ground_collision_sound.play()
                self.bird.update_on = False
                self.is_enter_pressed = False
                self.is_game_started = False
                self.game_state = "restart"
                self.achieved_score_text = self.font.render(f"total Score : {self.score}", True, (0, 0, 0))

            if (self.bird.rect.colliderect(self.pipes[0].rect_down) or
                    self.bird.rect.colliderect(self.pipes[0].rect_up)):
            #========================== Play pipe collision sound========================================
                collision_sound.play()
                self.is_enter_pressed = False
                self.is_game_started = False
                self.game_state = "restart"
                self.achieved_score_text = self.font.render(f"total Score : {self.score}", True, (0, 0, 0))

    #===========================Update positions and states of all game objects===========================
    def updateEverything(self, dt):

        if self.is_enter_pressed:
            # ===========================moving ground===========================
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right

            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            #===========================generating pipe===========================
            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed, self.pipe_distance))
                self.pipe_generate_counter = 0
                print("pipe started")
            self.pipe_generate_counter += 1
            #===========================moving the pipes===========================
            for pipe in self.pipes:
                pipe.update(dt)

            if len(self.pipes) != 0:
                if self.pipes[0].rect_up.right < 0:
                    self.pipes.pop(0)
                    print("pipe Ended")

        self.bird.update(dt)
    # ===========================Draw all game elements on screen===========================
    def drawEverything(self):

        self.win.blit(self.bg_img, (0, -370))
        if self.game_state == "game":
            for pipe in self.pipes:
                pipe.drawPipe(self.win)
            self.win.blit(self.ground1_img, self.ground1_rect)
            self.win.blit(self.ground2_img, self.ground2_rect)
            self.win.blit(self.bird.image, self.bird.rect)
            self.win.blit(self.score_text, self.score_text_rect)
        elif self.game_state == "menu":
            self.win.blit(self.bird_menu_img, self.bird_menu_rect)
            self.win.blit(self.title_text, self.title_text_rect)  # Draw title text
            self.win.blit(self.start_text, self.start_text_rect)
        elif self.game_state == "difficulty":
            self.win.blit(self.difficulty_text, self.difficulty_text_rect)
            if self.show_difficulty_options:
                self.win.blit(self.easy_text, self.easy_text_rect)
                self.win.blit(self.medium_text, self.medium_text_rect)
        elif self.game_state == "restart":
            self.win.blit(self.game_over_text, self.game_over_text_rect)  # Draw Game Over text
            self.win.blit(self.restart_text, self.restart_text_rect)
            self.win.blit(self.achieved_score_text, self.achieved_score_text_rect)

     #===========================Don't show difficulty buttons in restart state===========================
            self.show_difficulty_options = False

    # ===========================Set up background and ground images===========================
    def setUpBgAndGround(self):

        self.bg_img = pg.transform.scale(pg.image.load("flapback_img.png").convert(), (int(600 * self.scale_factor), int(768 * self.scale_factor)))
        self.ground1_img = pg.transform.scale(pg.image.load("ground_img.png").convert(), (int(400 * self.scale_factor), int(133  * self.scale_factor)))
        self.ground2_img = pg.transform.scale(pg.image.load("ground_img.png").convert(), (int(400 * self.scale_factor), int(133 * self.scale_factor)))

        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568

# ===========================Initialize the game===========================
game = Game()