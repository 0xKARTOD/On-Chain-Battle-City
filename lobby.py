
#!/usr/bin/python
# coding=utf-8

import os, pygame, time, sys
#socket
import socket, errno
from dotenv import load_dotenv

from server import start_game, create_thread
from client import join_game


class Game():

    # direction constants
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

    TILE_SIZE = 32

    def __init__(self):

        global screen, sprites, play_sounds, sounds, height, width

        # center window
        os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

        if play_sounds:
            pygame.mixer.pre_init(44100, -16, 1, 512)

        size = width, height = 960, 760

        pygame.init()
        
        if "-f" in sys.argv[1:]:
            screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode(size)

        self.clock = pygame.time.Clock()

        sprites = pygame.transform.scale(pygame.image.load("images/sprites.gif"), [192, 224])

        pygame.display.set_icon(sprites.subsurface(0, 0, 13*2, 13*2))

        # load sounds
        if play_sounds:
            pygame.mixer.init(44100, -16, 1, 512)

            sounds["start"] = pygame.mixer.Sound("sounds/gamestart.ogg")
            sounds["main_menu"] = pygame.mixer.Sound("sounds/main_menu.ogg")
            sounds["end"] = pygame.mixer.Sound("sounds/gameover.ogg")
            sounds["score"] = pygame.mixer.Sound("sounds/score.ogg")
            sounds["bg"] = pygame.mixer.Sound("sounds/background.ogg")
            sounds["fire"] = pygame.mixer.Sound("sounds/fire.ogg")
            sounds["explosion"] = pygame.mixer.Sound("sounds/explosion.ogg")
            sounds["brick"] = pygame.mixer.Sound("sounds/brick.ogg")
            sounds["steel"] = pygame.mixer.Sound("sounds/steel.ogg")

        self.player_life_image = sprites.subsurface(89*2, 56*2, 7*2, 8*2)

        # this is used in intro screen
        self.player_image = pygame.transform.rotate(sprites.subsurface(0, 0, 13*2, 13*2), 270)

        # if true, no new enemies will be spawn during this time
        self.timefreeze = False

        # load custom font
        self.font = pygame.font.Font("fonts/prstart.ttf", self.TILE_SIZE)

        self.nr_of_option = 1

        del bullets[:]

    def is_port_in_use(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((self.HOST, port))
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                s.close()
                return True
            else:
                s.close()
                return False
    
    def findLobby(self):

        load_dotenv()
        self.HOST = os.getenv('IP_ADDRESS') #socket.gethostname()
        self.PORT = 65432

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #sock stream is used for TCP protocols
     
        if self.is_port_in_use(self.PORT):
            join_game([
                sprites, 
                play_sounds, 
                sounds, 
                height, 
                width, 
                address, 
                self.PORT
            ])
        else:
            start_game([
                sprites, 
                play_sounds, 
                sounds, 
                height, 
                width, 
                address, 
                self.PORT
            ])

    def showMenu(self):

        global players, screen

        # stop game main loop (if any)
        self.running = False

        self.animateIntroScreen()

        main_loop = True
        while main_loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        quit()
                    elif event.key == pygame.K_UP:
                        if self.nr_of_option == 2:
                            self.nr_of_option = 1
                            self.drawIntroScreen()
                    elif event.key == pygame.K_DOWN:
                        if self.nr_of_option == 1:
                            self.nr_of_option = 2
                            self.drawIntroScreen()
                    elif event.key == pygame.K_RETURN:
                        main_loop = False

        if play_sounds:
            for sound in sounds:
                sounds[sound].stop()

        if self.nr_of_option == 1:
            self.findLobby()
        elif self.nr_of_option == 2:
            quit()
        


    def drawIntroScreen(self, put_on_surface = True):

        global screen

        screen.fill([0, 0, 0])

        lower_solf =  pygame.font.Font("fonts/prstart.ttf", int(self.TILE_SIZE/2))

        if pygame.font.get_init():
            screen.blit(self.font.render("READY", True, pygame.Color('white')), [width/3 + 80, 370])
            screen.blit(self.font.render("EXIT", True, pygame.Color('white')), [width/3 + 92, 470])

            screen.blit(lower_solf.render("(c) 1980 1985 NAMCO LTD. AND THAILAND OPERATION", True, pygame.Color('white')), [110, height - 80])
            screen.blit(lower_solf.render("ALL RIGHTS RESERVED", True, pygame.Color('white')), [width/3, height - 40])


        if self.nr_of_option == 1:
            screen.blit(self.player_image, [width/3 + 20, 371])
        elif self.nr_of_option == 2:
            screen.blit(self.player_image, [width/3 + 20, 471])

        self.writeInBricks("battle", [width/3 - 10, 80])
        self.writeInBricks("city", [width/3 + 50, 180])

        if put_on_surface:
            pygame.display.flip()

    def animateIntroScreen(self):

        global screen

        self.drawIntroScreen(False)
        screen_cp = screen.copy()

        screen.fill([0, 0, 0])

        if play_sounds:
            sounds["main_menu"].play()

        y = height
        while (y > 0):

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        y = 0
                        break

            screen.blit(screen_cp, [0, y])
            pygame.display.flip()
            y -= 1
            time.sleep(0.01)

        screen.blit(screen_cp, [0, 0])
        pygame.display.flip()


    def chunks(self, l, n):
        return [l[i:i+n] for i in range(0, len(l), n)]

    def writeInBricks(self, text, pos):

        global screen, sprites

        bricks = sprites.subsurface(56*2, 64*2, 8*2, 8*2)
        brick1 = bricks.subsurface((0, 0, 8, 8))
        brick2 = bricks.subsurface((8, 0, 8, 8))
        brick3 = bricks.subsurface((8, 8, 8, 8))
        brick4 = bricks.subsurface((0, 8, 8, 8))

        alphabet = {
            "a" : "0071b63c7ff1e3",
            "b" : "01fb1e3fd8f1fe",
            "c" : "00799e0c18199e",
            "e" : "01fb060f98307e",
            "g" : "007d860cf8d99f",
            "i" : "01f8c183060c7e",
            "l" : "0183060c18307e",
            "m" : "018fbffffaf1e3",
            "o" : "00fb1e3c78f1be",
            "r" : "01fb1e3cff3767",
            "t" : "01f8c183060c18",
            "v" : "018f1e3eef8e08",
            "y" : "019b3667860c18"
        }

        abs_x, abs_y = pos

        for letter in text.lower():

            binstr = ""
            for h in self.chunks(alphabet[letter], 2):
                binstr += str(bin(int(h, 16)))[2:].rjust(8, "0")
            binstr = binstr[7:]

            x, y = 0, 0
            letter_w = 0
            surf_letter = pygame.Surface((56, 56))
            for j, row in enumerate(self.chunks(binstr, 7)):
                for i, bit in enumerate(row):
                    if bit == "1":
                        if i%2 == 0 and j%2 == 0:
                            surf_letter.blit(brick1, [x, y])
                        elif i%2 == 1 and j%2 == 0:
                            surf_letter.blit(brick2, [x, y])
                        elif i%2 == 1 and j%2 == 1:
                            surf_letter.blit(brick3, [x, y])
                        elif i%2 == 0 and j%2 == 1:
                            surf_letter.blit(brick4, [x, y])
                        if x > letter_w:
                            letter_w = x
                    x += 8
                x = 0
                y += 8
            screen.blit(surf_letter, [abs_x, abs_y])
            abs_x += letter_w + 16


def start_lobby(wallet_address):
    global sprites, screen, bullets, play_sounds, sounds, address

    address = wallet_address

    sprites = None
    screen = None
    bullets = []

    play_sounds = True
    sounds = {}

    game = Game()
    game.showMenu()