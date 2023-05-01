#!/usr/bin/python
# coding=utf-8

import pygame, sys, os, random, uuid, time, socket, threading, json

from dotenv import load_dotenv
from web3 import Web3

from web3.middleware import geth_poa_middleware

def create_thread(target):
    thread = threading.Thread(target=target)
    thread.daemon = True #this makes is so that these thread will auto quit before the code ends running
    thread.start()

class Timer(object):
    def __init__(self):
        self.timers = []

    def add(self, interval, f, repeat = -1):
        options = {
            "interval": interval,
            "callback": f,
            "repeat": repeat,
            "times": 0,
            "time": 0,
            "uuid": uuid.uuid4()
        }
        self.timers.append(options)

        return options["uuid"]

    def destroy(self, uuid_nr):
        for timer in self.timers:
            if timer["uuid"] == uuid_nr:
                self.timers.remove(timer)
                return

    def update(self, time_passed):
        for timer in self.timers:
            timer["time"] += time_passed
            if timer["time"] > timer["interval"]:
                timer["time"] -= timer["interval"]
                timer["times"] += 1
                if timer["repeat"] > -1 and timer["times"] == timer["repeat"]:
                    self.timers.remove(timer)
                try:
                    timer["callback"]()
                except:
                    try:
                        self.timers.remove(timer)
                    except:
                        pass
                                        
################################################################################
##################################### BATTLE ###################################
################################################################################


class myRect(pygame.Rect):
    def __init__(self, left, top, width, height, type):
        pygame.Rect.__init__(self, left, top, width, height)
        self.type = type
                
class Battle():

    # direction constants
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    
    def __init__(self, _port):
        
        global screen, sprites, play_sounds, sounds, player, address

        self.font = pygame.font.Font("fonts/prstart.ttf", 16)
        self.TILE_SIZE = 32

        os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

        if play_sounds:
            pygame.mixer.pre_init(44100, -16, 1, 512)

        pygame.init()

        size = width, height

        self.clock = pygame.time.Clock()

        self.address_host = address

        if "-f" in sys.argv[1:]:
            screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode(size)

        pygame.display.set_icon(sprites.subsurface(0, 0, 13*2, 13*2))

        self.stage = 1 #### SHOULD BE RANDOM

        self.level = Level(self.stage)

        load_dotenv()
        self.HOST = os.getenv('IP_ADDRESS')
        self.owner_caller = os.getenv('OWNER_WALLET')
        self.private_key = os.getenv('PRIVATE_KEY')
        self.contract_address = os.getenv('OWNER_WALLET')

        self.PORT = _port

        self.ADDR = (self.HOST,self.PORT)
        self.connection_established = False
        self.conn , self.addr = None, None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind(self.ADDR)
        except socket.error as e:
            print(str(e))
            
        self.sock.listen(1)

        self.clock = pygame.time.Clock() 

        self.running = True
        self.data_is_providing = False

        self.gameover = False


        ##### Connect to blockchain:

        self.node_url = 'https://rpc-mumbai.maticvigil.com/'
        self.web3 = Web3(Web3.HTTPProvider(self.node_url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Verify if the connection is successful
        if self.web3.is_connected():
            print("-" * 50)
            print("Connection Successful")
            print("-" * 50)
        else:
            print("Connection Failed")

        create_thread(self.waiting_for_connection)


    def str_to_bool(self, str):
        if str == 'True':
            return True
        if str == 'False':
            return False
        
    def receive_data(self):

        while not self.gameover:

            self.data = self.conn.recv(1024).decode()

            if str(self.data).startswith(str('0x')):
                self.second_wallet = self.data
            else:
                data = self.data.split("-")
                self.player2_key_K_UP = self.str_to_bool(data[0])
                self.player2_key_K_DOWN = self.str_to_bool(data[1])
                self.player2_key_K_LEFT = self.str_to_bool(data[2])
                self.player2_key_K_RIGHT = self.str_to_bool(data[3])
                self.player2_key_K_SPACE = self.str_to_bool(data[4])

                self.data_is_providing = True

    def waiting_for_connection(self):

        self.waiting_for_conn = True

        print("Waiting for connection....")
        
        self.conn , self.addr = self.sock.accept() # it will wait for a connection , also blocks any new threads 
        print("Client is connected!!!")

        self.waiting_for_conn = False
        self.connection_established = True

        self.receive_data()

    def draw(self):
        global screen, players, bullets

        screen.fill([0, 0, 0])

        self.level.draw([self.level.TILE_EMPTY, self.level.TILE_BRICK, self.level.TILE_STEEL, self.level.TILE_FROZE, self.level.TILE_WATER])
        self.level.draw([self.level.TILE_GRASS])

        for player in players:
            player.draw()

        for bullet in bullets:
            bullet.draw()

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


    def send_winner_transaction(self):

        winner_bytes = self.web3.to_checksum_address(self.winner)
        loser_bytes = []
        for address in self.addresses:
            if address != self.winner:
                loser_bytes.append(self.web3.to_checksum_address(address))

        self.nonce = self.web3.eth.get_transaction_count(self.owner_caller)

        with open("solidity/BattleCityABI.txt") as f:
            self.abi = json.load(f)

        self.contract = self.web3.eth.contract(address = self.contract_address, abi = self.abi)

        self.call_function = self.contract.functions.addUser(winner_bytes, loser_bytes).build_transaction(
        {
            "chainId": self.web3.eth.chain_id,
            "from": self.owner_caller,
            "nonce": self.nonce
        })

        self.signed_tx = self.web3.eth.account.sign_transaction(self.call_function, private_key = self.private_key)

        send_tx = self.web3.eth.send_raw_transaction(self.signed_tx.rawTransaction)

        tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
        print("Transaction: ", tx_receipt['transactionHash'].hex())

    def gameOverScreen(self):
        """ Show game over screen """

        global screen, gtimer, play_sounds

        # stop game main loop (if any)
        self.running = False

        screen.fill([0, 0, 0])

        short_wallet = self.winner[:5] + '...' + self.winner[-5:]

        self.writeInBricks("game", [width/3, height/3])
        self.writeInBricks("over", [width/3, height/3 + 150])
        screen.blit(self.font.render("winner:" + short_wallet, True, pygame.Color('white')), [width/3 - 20, height/3 + 300])
        pygame.display.flip()

        self.conn.send("{}".format(self.winner).encode())

        ##### TX to smart contract

        #self.send_winner_transaction()
        
        while self.gameover:
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            gtimer.update(time_passed)

            pygame.display.flip()
             
    def game_started(self):

        global player, play_sounds, sounds, bullets, players

        self.loading_image = pygame.transform.rotate(sprites.subsurface(26, 0, 30, 30), 270)

        x = 0

        screen.fill([0, 0, 0])

        while not self.connection_established:
            screen.blit(self.font.render("LOADING...", True, pygame.Color('white')), [width/3 + 80, 370])
            screen.blit(self.loading_image, [x, width/2])
            pygame.display.update()

            time.sleep(0.01)
            x += 1

            if x == width:
                x = 0

        screen.fill([0, 0, 0])

        time.sleep(0.02)

        self.addresses = [self.address_host, self.second_wallet]

        del bullets[:]
        del players[:]
        del gtimer.timers[:]

        if play_sounds:
            sounds["start"].play()
            gtimer.add(4330, lambda :sounds["bg"].play(-1), 1)

        player_number = 0

        for address in self.addresses:
            players.append(Player(self.level, address, player_number))
            player_number += 1

        self.draw()

        self.player2_key_K_UP = False
        self.player2_key_K_DOWN = False
        self.player2_key_K_LEFT = False
        self.player2_key_K_RIGHT = False
        self.player2_key_K_SPACE = False

        # Game loop
        while self.running:
            if self.connection_established:
                time_passed = self.clock.tick(50)

                if len(players) == 1:
                    self.winner = players[0].wallet
                    self.running = False

                    self.gameover = True

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                for player in players:
                    if player.wallet == self.address_host and player.state != player.STATE_DEAD:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_UP]:
                            player.move(self.DIR_UP)
                        elif keys[pygame.K_DOWN]:
                            player.move(self.DIR_DOWN)
                        elif keys[pygame.K_LEFT]:
                            player.move(self.DIR_LEFT)
                        elif keys[pygame.K_RIGHT]:
                            player.move(self.DIR_RIGHT)
                        if keys[pygame.K_SPACE]:
                            if player.fire() and play_sounds:
                                sounds["fire"].play()
                    if player.wallet == self.second_wallet and self.data_is_providing and player.state != player.STATE_DEAD:
                        if self.player2_key_K_UP == True:
                            player.move(self.DIR_UP)
                        elif self.player2_key_K_DOWN == True:
                            player.move(self.DIR_DOWN)
                        elif self.player2_key_K_LEFT == True:
                            player.move(self.DIR_LEFT)
                        elif self.player2_key_K_RIGHT == True:
                            player.move(self.DIR_RIGHT)
                        if self.player2_key_K_SPACE == True:
                            if player.fire() and play_sounds:
                                sounds["fire"].play()

                for bullet in bullets:
                    if bullet.state == bullet.STATE_REMOVED:
                        bullets.remove(bullet)
                    else:
                        bullet.update()

                gtimer.update(time_passed)

                screen_bytes = pygame.image.tostring(screen, 'RGB')
                self.conn.sendall(screen_bytes)

                self.draw()
                pygame.display.flip()


        if play_sounds:
            for sound in sounds:
                sounds[sound].stop()
            sounds["end"].play()

        self.gameOverScreen()
                        
class Level():

    (TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)

    TILE_SIZE = 16

    def __init__(self, level_nr = None):

        global sprites

        tile_images = [
            pygame.Surface((8*2, 8*2)),
            sprites.subsurface(48*2, 64*2, 8*2, 8*2),
            sprites.subsurface(48*2, 72*2, 8*2, 8*2),
            sprites.subsurface(56*2, 72*2, 8*2, 8*2),
            sprites.subsurface(64*2, 64*2, 8*2, 8*2),
            sprites.subsurface(64*2, 64*2, 8*2, 8*2),
            sprites.subsurface(72*2, 64*2, 8*2, 8*2),
            sprites.subsurface(64*2, 72*2, 8*2, 8*2)
        ]
        self.tile_empty = tile_images[0]
        self.tile_brick = tile_images[1]
        self.tile_steel = tile_images[2]
        self.tile_grass = tile_images[3]
        self.tile_water = tile_images[4]
        self.tile_water1= tile_images[4]
        self.tile_water2= tile_images[5]
        self.tile_froze = tile_images[6]

        level_nr = 1 

        self.loadLevel(level_nr)
        self.obstacle_rects = []
        self.updateObstacleRects()


    def updateObstacleRects(self):

        for tile in self.mapr:
            if tile.type in (self.TILE_BRICK, self.TILE_STEEL, self.TILE_WATER):
                self.obstacle_rects.append(tile)
                                
    def toggleWaves(self):
        if self.tile_water == self.tile_water1:
            self.tile_water = self.tile_water2
        else:
            self.tile_water = self.tile_water1


    def loadLevel(self, level_nr = 1):
        filename = "levels/" + str(level_nr)
        if (not os.path.isfile(filename)):
            return False
        f = open(filename, "r")
        data = f.read().split("\n")

        self.mapr = []
        x, y = 0, 0
        for row in data:
            for ch in row:
                if ch == "#":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_BRICK))
                elif ch == "@":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_STEEL))
                elif ch == "~":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_WATER))
                elif ch == "%":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_GRASS))
                elif ch == "-":
                    self.mapr.append(myRect(x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_FROZE))
                x += self.TILE_SIZE
            x = 0
            y += self.TILE_SIZE
        return True

    def hitTile(self, pos, power = 1, sound = False):

        global play_sounds, sounds

        for tile in self.mapr:
            if tile.topleft == pos:
                if tile.type == self.TILE_BRICK:
                    if play_sounds and sound:
                        sounds["brick"].play()
                    self.mapr.remove(tile)
                    self.updateObstacleRects()
                    return True
                elif tile.type == self.TILE_STEEL:
                    if play_sounds and sound:
                        sounds["steel"].play()
                    if power == 2:
                        self.mapr.remove(tile)
                        self.updateObstacleRects()
                    return True
                else:
                    return False

    def draw(self, tiles = None):
        global screen

        if tiles == None:
            tiles = [TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE]

        for tile in self.mapr:
            if tile.type in tiles:
                if tile.type == self.TILE_BRICK:
                    screen.blit(self.tile_brick, tile.topleft)
                elif tile.type == self.TILE_STEEL:
                    screen.blit(self.tile_steel, tile.topleft)
                elif tile.type == self.TILE_WATER:
                    screen.blit(self.tile_water, tile.topleft)
                elif tile.type == self.TILE_FROZE:
                    screen.blit(self.tile_froze, tile.topleft)
                elif tile.type == self.TILE_GRASS:
                    screen.blit(self.tile_grass, tile.topleft)


class Tank():

    # possible directions
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

    (STATE_SPAWNING, STATE_DEAD, STATE_ALIVE, STATE_EXPLODING) = range(4)
    
    (SIDE_PLAYER, SIDE_ENEMY) = range(2)

    def __init__(self, level, address, player_number, speed = 2, direction = None):
        
        self.health = 100

        self.image = sprites.subsurface(32, 0, 30, 30)
        self.rect = self.image.get_rect()

        self.speed = speed
        self.level = level
        self.max_active_bullets = 1
        self.wallet = address

        self.bullet_damage = 100

        self.image_up = self.image
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

        self.controls = [pygame.K_SPACE, pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]

        self.pressed = [False] * 4

        if player_number == 0:
            self.rect = pygame.Rect(200, 300, 26, 26)
        elif player_number == 1:
            self.rect = pygame.Rect(400, 300, 26, 26)

        if direction == None:
            self.direction = random.choice([self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT])
        else:
            self.direction = direction

        self.state = self.STATE_ALIVE

                        
    def move(self, direction):

        if self.direction != direction:
            self.rotate(direction)

        if direction == self.DIR_UP:
            new_position = [self.rect.left, self.rect.top - self.speed]
            if new_position[1] < 0:
               return
        elif direction == self.DIR_RIGHT:
            new_position = [self.rect.left + self.speed, self.rect.top]
            if new_position[0] > (960 - 26):
               return
        elif direction == self.DIR_DOWN:
            new_position = [self.rect.left, self.rect.top + self.speed]
            if new_position[1] > (832 - 26):
               return
        elif direction == self.DIR_LEFT:
            new_position = [self.rect.left - self.speed, self.rect.top]
            if new_position[0] < 0:
               return
            
        player_rect = pygame.Rect(new_position, [26, 26])

        # collisions with tiles
        if player_rect.collidelist(self.level.obstacle_rects) != -1:
            return

        # collisions with other players
        for player in players:
            if player != self and player.state == player.STATE_ALIVE and player_rect.colliderect(player.rect) == True:
                return
        
        self.rect.topleft = (new_position[0], new_position[1])
    
    def nearest(self, num, base):

        return int(round(num / (base * 1.0)) * base)

    def rotate(self, direction, fix_position = True):

        self.direction = direction

        if direction == self.DIR_UP:
            self.image = self.image_up
        elif direction == self.DIR_RIGHT:
            self.image = self.image_right
        elif direction == self.DIR_DOWN:
            self.image = self.image_down
        elif direction == self.DIR_LEFT:
            self.image = self.image_left

        if fix_position:
            new_x = self.nearest(self.rect.left, 8) + 3
            new_y = self.nearest(self.rect.top, 8) + 3

            if (abs(self.rect.left - new_x) < 5):
                self.rect.left = new_x

            if (abs(self.rect.top - new_y) < 5):
                self.rect.top = new_y

    def fire(self, forced = False):

        global bullets, labels

        if not forced:
            active_bullets = 0
            for bullet in bullets:
                if bullet.owner_class == self and bullet.state == bullet.STATE_ACTIVE:
                    active_bullets += 1
            if active_bullets >= self.max_active_bullets:
                return False

        bullet = Bullet(self.level, self.rect.topleft, self.direction)

        bullet.speed = 8

        bullet.owner = self.SIDE_PLAYER

        bullet.owner_class = self
        bullets.append(bullet)
        return True
    
    def bulletImpact(self):

        global play_sounds, sounds

        self.health -= self.bullet_damage
        if self.health < 1:
            if play_sounds:
                sounds["explosion"].play()
            self.explode()

        return True
    
    def explode(self):

        global players

        if self.state != self.STATE_DEAD:
            self.state = self.STATE_EXPLODING
            self.explosion = Explosion(self.rect.topleft)

            gtimer.add(500, lambda :self.destroy(), 1)
    def destroy(self):
        self.state = self.STATE_DEAD
        players.remove(self)
                                
    def draw(self):

        global screen
        if self.state == self.STATE_ALIVE:
            screen.blit(self.image, self.rect.topleft)
        elif self.state == self.STATE_EXPLODING:
            self.explosion.draw()

class Player(Tank):

    def __init__(self, level, address, player_number, direction = None):

        Tank.__init__(self, level, address, player_number, direction = None)

        global sprites

        #self.start_position = position
        self.start_direction = direction


        self.wallet = address

        # total score
        self.score = 0

        self.image_up = self.image;
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

        if direction == None:
            self.rotate(self.DIR_UP, False)
        else:
            self.rotate(direction, False)

class Bullet():
    # direction constants
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

    # bullet's stated
    (STATE_REMOVED, STATE_ACTIVE, STATE_EXPLODING) = range(3)

    (OWNER_PLAYER, OWNER_ENEMY) = range(2)
        

    def __init__(self, level, position, direction, speed = 5, damage = 100):

        global sprites

        self.level = level
        self.direction = direction
        self.owner = None
        self.owner_class = None
        self.damage = damage

        # 1-regular everyday normal bullet
        # 2-can destroy steel
        self.power = 1

        self.image = sprites.subsurface(75*2, 74*2, 3*2, 4*2)

        if direction == self.DIR_UP:
            self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
        elif direction == self.DIR_RIGHT:
            self.image = pygame.transform.rotate(self.image, 270)
            self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
        elif direction == self.DIR_DOWN:
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
        elif direction == self.DIR_LEFT:
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = pygame.Rect(position[0] - 8 , position[1] + 11, 8, 6)

        self.explosion_images = [
            sprites.subsurface(0, 80*2, 32*2, 32*2),
            sprites.subsurface(32*2, 80*2, 32*2, 32*2),
        ]

        self.speed = speed

        self.state = self.STATE_ACTIVE

    def draw(self):
        global screen
        if self.state == self.STATE_ACTIVE:
            screen.blit(self.image, self.rect.topleft)
        elif self.state == self.STATE_EXPLODING:
            self.explosion.draw()

    def update(self):
        global bullets

        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.destroy()
                del self.explosion

        if self.state != self.STATE_ACTIVE:
            return

        """ move bullet """
        if self.direction == self.DIR_UP:
            self.rect.topleft = [self.rect.left, self.rect.top - self.speed]
            if self.rect.top < 0:
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_RIGHT:
            self.rect.topleft = [self.rect.left + self.speed, self.rect.top]
            if self.rect.left > (960 - self.rect.width):
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_DOWN:
            self.rect.topleft = [self.rect.left, self.rect.top + self.speed]
            if self.rect.top > (832 - self.rect.height):
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_LEFT:
            self.rect.topleft = [self.rect.left - self.speed, self.rect.top]
            if self.rect.left < 0:
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return

        has_collided = False

        # check for collisions with walls. one bullet can destroy several (1 or 2)
        # tiles but explosion remains 1
        rects = self.level.obstacle_rects
        collisions = self.rect.collidelistall(rects)
        if collisions != []:
            for i in collisions:
                if self.level.hitTile(rects[i].topleft, self.power, self.owner == self.OWNER_PLAYER):
                    has_collided = True
        if has_collided:
            self.explode()
            return

        # check for collisions with other bullets
        for bullet in bullets:
            if self.state == self.STATE_ACTIVE and bullet.owner != self.owner and bullet != self and self.rect.colliderect(bullet.rect):
                self.destroy()
                self.explode()
                return

        # check for collisions with players
        for player in players:
            if player.state == player.STATE_ALIVE and self.rect.colliderect(player.rect):
                if player.bulletImpact():
                    self.destroy()
                    return
                

    def explode(self):
        global screen
        if self.state != self.STATE_REMOVED:
            self.state = self.STATE_EXPLODING
            self.explosion = Explosion([self.rect.left-13, self.rect.top-13], None, self.explosion_images)

    def destroy(self):
        self.state = self.STATE_REMOVED


class Explosion():
    def __init__(self, position, interval = None, images = None):

        global sprites

        self.position = [position[0]-16, position[1]-16]
        self.active = True

        if interval == None:
            interval = 100

        if images == None:
            images = [
                sprites.subsurface(0, 80*2, 32*2, 32*2),
                sprites.subsurface(32*2, 80*2, 32*2, 32*2),
                sprites.subsurface(64*2, 80*2, 32*2, 32*2)
            ]

        images.reverse()

        self.images = [] + images

        self.image = self.images.pop()

        gtimer.add(interval, lambda :self.update(), len(self.images) + 1)

    def draw(self):
        global screen
        screen.blit(self.image, self.position)

    def update(self):
        if len(self.images) > 0:
            self.image = self.images.pop()
        else:
            self.active = False

                        
def start_game(data):

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