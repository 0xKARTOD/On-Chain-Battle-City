#!/usr/bin/python
# coding=utf-8

import os, pygame, sys, socket
from dotenv import load_dotenv
from server import Timer

class Battle():

    # direction constants
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    
    def __init__(self, _port):
        
        global screen, sprites, play_sounds, sounds, player

        self.font = pygame.font.Font("fonts/prstart.ttf", 16)
        self.TILE_SIZE = 32

        os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

        if play_sounds:
            pygame.mixer.pre_init(44100, -16, 1, 512)

        pygame.init()

        size = width, height

        self.clock = pygame.time.Clock()

        load_dotenv()
        self.HOST = os.getenv('IP_ADDRESS')

        if "-f" in sys.argv[1:]:
            screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode(size)

        pygame.display.set_icon(sprites.subsurface(0, 0, 13*2, 13*2))

        self.clock = pygame.time.Clock() 

        self.running = True

        self.connection_established = True

        self.gameover = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #sock stream is used for TCP protocols
        self.sock.connect((self.HOST,_port))
    
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

    def gameOverScreen(self):
        """ Show game over screen """

        global screen, gtimer, play_sounds

        # stop game main loop (if any)
        self.running = False

        screen.fill([0, 0, 0])

        short_wallet = self.winner[:5] + '...' + self.winner[-5:]

        self.writeInBricks("ggggame", [width/3, height/3])
        self.writeInBricks("over", [width/3, height/3 + 150])
        screen.blit(self.font.render("winner:" + short_wallet, True, pygame.Color('white')), [width/3 - 20, height/3 + 300])
        pygame.display.flip()
        
        while self.gameover:
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            gtimer.update(time_passed)

            pygame.display.flip()
                    
    def game_started(self):

        global player, play_sounds, sounds, bullets, players

        del bullets[:]
        del players[:]
        del gtimer.timers[:]

        if play_sounds:
            sounds["start"].play()
            gtimer.add(4330, lambda :sounds["bg"].play(-1), 1)

        format = 'RGB'
        expected_length = width * height * len(format)

        self.sock.send("{}".format(address).encode())

        # Game loop
        while self.running:
            if self.connection_established:
                time_passed = self.clock.tick(50)

                surface_bytes = b''
                while len(surface_bytes) < expected_length:
                    data = self.sock.recv(expected_length - len(surface_bytes))
                    #print(data)
                    if not data or str(data)[2:-1].startswith(str('0x')):
                        self.winner = str(data)[2:-1]
                        break
                    surface_bytes += data

                    
                if len(surface_bytes) == 0:
                    self.running = False
                    self.gameover = True
                    break

                if len(surface_bytes) == expected_length:
                    img_surface = pygame.image.fromstring(surface_bytes, (width, height), format)

                    screen.blit(img_surface, (0, 0))
                    pygame.display.update()
                else:
                    print(f'Error: received {len(surface_bytes)} bytes, expected {expected_length} bytes')

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                keys = pygame.key.get_pressed()

                gtimer.update(time_passed)
                self.sock.send("{}-{}-{}-{}-{}".format(
                    keys[pygame.K_UP], 
                    keys[pygame.K_DOWN], 
                    keys[pygame.K_LEFT], 
                    keys[pygame.K_RIGHT], 
                    keys[pygame.K_SPACE]).encode())

        if play_sounds:
            for sound in sounds:
                sounds[sound].stop()
            sounds["end"].play()

        self.gameOverScreen()

def join_game(data):

    global sprites, play_sounds, sounds, bullets, gtimer, width, height, address, players

    sprites = data[0]
    play_sounds = data[1]
    sounds = data[2]
    height, width = data[3], data[4]
    address = data[5]
    PORT = data[6]
    bullets = []
    players = []


    gtimer = Timer()

    battle = Battle(PORT)
    battle.game_started()