"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wntroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.  
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

# Hamed Rabah (hr277) and Erick Salvador Rocha (eis29)
# 12.8.17
"""

from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted 
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.
    
    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen. 
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you 
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of 
    aliens.
    
    If you want to pause the game, tell this controller to draw, but do not update.  See 
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.
    
    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None] 
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]
    
    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS 
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that 
    you need to access in Invaders.  Only add the getters and setters that you need for 
    Invaders. You can keep everything else hidden.
    
    You may change any of the attributes above as you see fit. For example, may want to 
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.
    
    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY        
        _move_left: 
        _time_alien_step:
        _last_time_fired:
        _alien_time_fire: 
        _alien_speed: The alien speed
        _alien_fire_rate: 
        _pause: 
        _victory: False until the player beats the game
        _aliens_killed: 
        _alien_steps: 
        _random_steps: 
    """
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    
    def getLives(self):
        return self._lives
    
    def getPause(self):
        return self._pause
    
    def setPause(self, value):
        self._pause = value

    def getVictory(self):
        return self._victory

    def getAliensKilled(self):
        return self._aliens_killed


    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    
    def __init__(self):
        """Initializer for Wave objects """ 
        self._ship = Ship()
        self._aliens = self.createAliens()
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],linewidth=2, linecolor='black')
        self._time=0
        self._move_left = 0
        self._bolts = []
        self._time_alien_step = 0
        self._last_time_fired = 0
        self._alien_time_fire = 0
        self._alien_speed = ALIEN_SPEED
        self._alien_fire_rate = random.randint(1,BOLT_RATE)
        self._lives = SHIP_LIVES
        self._pause = 0
        self._victory=False
        self._aliens_killed= 0
        self._alien_steps=0
        self._random_steps=0
    
    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self,input,dt):
        """
        Animates the ship, aliens, and lasers.
        
        Parameter dt: The time since the last animation frame.
        Precondition: dt is a float.
        Parameter input: the user input, used to control the ship and change state
        [instance of GInput; it is inherited from GameApp]
        Precondition: Must be an instance of GInput
        """
        if (self._ship is not None):
            self._updateShip(input)
        self._updateBolt(input)
        self._time+=dt
        self._MoveAliens(dt)
        self._collision_detection()
        self._crossed_the_line()
        self._aliens_defeated()
        self._text=self.Aliens_Killed()
        self._text2=self.Ships_Killed()
        self._updateList_Aliens()
        

    def _updateList_Aliens(self):
        """ If an alien is no longer in the list it becomes deleted"""
        for n in range(len(self._aliens)-1):
            col=self._aliens[n]
            if col.count(None) == len(col):
                del self._aliens[n]
    
    
    def _updateShip(self,input):
        """ 
        Updates the position of the ship based on the player input

        Parameter input: the user input, used to control the ship and change state
        [instance of GInput; it is inherited from GameApp]
        Precondition: Must be an instance of GInput 
        """ 
        da = self._ship.x
        if input.is_key_down('left'):
            da = max(da-SHIP_MOVEMENT,0+(0.5*SHIP_WIDTH ))
        if input.is_key_down('right'):
            da = min(da+SHIP_MOVEMENT,GAME_WIDTH-(0.5*SHIP_WIDTH ))
        self._ship.x=da




        
    def _MoveAliens(self,dt):
        """ 
        Moves the aliens right first, and then left once they hit the wall, and so forth... 

        Parameter dt: The time since the last animation frame.
        Precondition: dt is a float.
        """  
        if self._time>=self._alien_speed:
            self._time = 0
            if self._move_left==1:
                self._MoveAliensLeft()
            elif self._move_left==0:
                self._MoveAliensRight()
            self._alien_steps+=1

            
    def _MoveAliensRight(self):
        """ 
        Moves the aliens right (and down once they hit the wall) 
        """  
        right_end = GAME_WIDTH-(ALIEN_H_SEP+(0.5*ALIEN_WIDTH))
        left_end = 0+ALIEN_H_SEP+(0.5*ALIEN_WIDTH)
        future_pos = 0
        
        for row in range(len(self._aliens)):
            for col in range(len(self._aliens[row])):
                alien=self._aliens[row][col]
                if (alien is not None):
                    future_pos = alien.x+ALIEN_H_WALK
                    if future_pos > right_end:
                        self._move_left = 1
        
        
        for row in range(len(self._aliens)):
            for col in range(len(self._aliens[row])):
                alien=self._aliens[row][col]
                if (alien is not None):
                    if self._move_left==0 and alien.x<=(right_end):
                        alien.x=alien.x+ALIEN_H_WALK
                    elif self._move_left == 1:
                        alien.y=alien.y-ALIEN_V_WALK
                    
                    
    def _MoveAliensLeft(self):
        """ 
        Moves the aliens left (and down once they hit the wall) 
        """  
        right_end = GAME_WIDTH-(ALIEN_H_SEP+(0.5*ALIEN_WIDTH))
        left_end = 0+ALIEN_H_SEP+(0.5*ALIEN_WIDTH)
        
        
        for row in range(len(self._aliens)):
            for col in range(len(self._aliens[row])):
                    alien=self._aliens[row][col]
                    if (alien is not None):
                        if self._move_left==1 and  alien.x>(left_end):
                            alien.x=alien.x-ALIEN_H_WALK
                        else:
                           self._move_left=0
                           alien.y=alien.y-ALIEN_V_WALK
                            
    def _ShipBolt(self, input):
        """ 
        Creates a list and appends player bolts to that list

        Parameter input: the user input, used to control the ship and change state
        [instance of GInput; it is inherited from GameApp]
        Precondition: Must be an instance of GInput 
        """  
        list=[]
        for x in self._bolts:
            if x.isPlayerBolt() == True:
                list.append(1)
        if len(list)==0:
            if input.is_key_down('up'):
                self._bolts.append(Bolt(self._ship.x,SHIP_HEIGHT, BOLT_UP, 'blue'))
                pewSound = Sound('pew2.wav')
                pewSound.play()
                
    def _updateBolt(self, input):
        """ 
        Calls the functions that create alien and player bolts. Also calls the functions that 
        move bolts up or down. 

        Parameter input: the user input, used to control the ship and change state
        [instance of GInput; it is inherited from GameApp]
        Precondition: Must be an instance of GInput 
        """  
        self._ShipBolt(input)
        self._AlienBolts()    
        
        i = 0
        while i < (len(self._bolts)):
            if self._bolts[i].isPlayerBolt() == True:
                    self._MoveBoltsUp()
            i+=1                   

        i = 0
        while i < (len(self._bolts)):
             if self._bolts[i].isPlayerBolt() == False:
                    self._MoveBoltsDown()
             i+=1

            
    def  _AlienBolts(self):
        """ 
        Creates and appends alien bolts to the list of bolts
        """          
        if self._alien_steps== 0:
            self._random_steps=random.randint(1,BOLT_RATE)
            
        if self._alien_steps == self._random_steps:
            random_column=random.randint(0,len(self._aliens)-1)
            list_y=[]
            lenght= len(self._aliens[random_column])
            if self._aliens[random_column].count(None) != lenght:
                for n in range(len(self._aliens[random_column])):
                    alien=self._aliens[random_column][n]
                    if (alien is not None):
                        list_y.append(alien.y)
                        x=alien.x  
            if len(list_y)!=0:
                min_y=min(list_y)
                self._bolts.append(Bolt(x,min_y,BOLT_DOWN, 'red'))
            
            self._alien_steps=0
    
    def _MoveBoltsUp(self):
        """ 
        Moves player bolts up
        """     
        for bolt in self._bolts:
            if bolt.isPlayerBolt() == True:
                bolt.y += BOLT_SPEED
                if bolt.y-(0.5*BOLT_HEIGHT) > GAME_HEIGHT:
                    self._bolts.remove(bolt)
    
    def _MoveBoltsDown(self):
        """ 
        Moves alien bolts down
        """             
        for bolt in self._bolts:
            if bolt.isPlayerBolt() == False:
                bolt.y -= BOLT_SPEED
                if bolt.y+(0.5*BOLT_HEIGHT)< 0:
                    self._bolts.remove(bolt)
    
    def createAliens(self):
        """
        Creates the list of aliens in their respective positions.
        """
        self._aliens =[]
        left=(ALIEN_H_SEP+(0.5*ALIEN_WIDTH))
        top=GAME_HEIGHT-ALIEN_CEILING
        aliens_height=((ALIEN_ROWS-1)*ALIEN_V_SEP)+(ALIEN_ROWS*ALIEN_HEIGHT)
        bottom=(top-aliens_height)+(0.5*ALIEN_HEIGHT)
        for col in range(ALIENS_IN_ROW):
            subset = []
            for row in range(ALIEN_ROWS):
                rem=row%6
                if rem ==0 or rem==1:
                    source=ALIEN_IMAGES[0]
                elif rem==2 or rem==3:
                    source=ALIEN_IMAGES[1]
                else:
                    source=ALIEN_IMAGES[2]
                subset.append(Alien(left+(ALIEN_WIDTH+ALIEN_H_SEP)*col,bottom+(ALIEN_HEIGHT+ALIEN_V_SEP)*row,source))
            self._aliens.append(subset)       
        return self._aliens
    
    
    def _collision_detection(self):
        """ 
        Detects if a bolt hits either an alien or the player ship
        """     
        for bolt in self._bolts:
            if (self._ship is not None and self._ship.collides(bolt) and bolt.isPlayerBolt() == False):
                self._lives -= 1
                self._pause = 1
                if self._lives == 0:
                    self._ship = None
                self._bolts.remove(bolt)
            elif (bolt.isPlayerBolt() == True):
                for row in range(len(self._aliens)):
                    for col in range(len(self._aliens[row])):
                        alien = self._aliens[row][col]
                        if (alien is not None and alien.collides(bolt)):
                            self._aliens[row][col] = None
                            boomSound = Sound('blast1.wav')
                            boomSound.play()
                            self._aliens_killed +=int(100/(col+1))
                            self._alien_speed=(self._alien_speed*0.97)
                            if bolt in self._bolts:
                                self._bolts.remove(bolt)

    
    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    
    def draw(self,view):
        """
        Calls the functions that draw the aliens, ship, dline, bolts, and text (score and lives)
        """
        #draw aliens
        self._drawShip(view)
        self._drawAliens(view)
        self._drawDline(view)
        self._drawBolts(view)
        self._text.draw(view)
        self._text2.draw(view)
    
        
    def _drawAliens(self, view):
        """
        Draw the aliens
        """
        for col in range(len(self._aliens[0])):
            #print (col)
            for row in range(len(self._aliens)):
               alien=self._aliens[row][col]
               if (alien is not None):
                    alien.draw(view)

                    
        #Draw ship
    def _drawShip(self, view):
        """
        Draw the ship
        """
        if (self._ship is not None):
            self._ship.draw(view)
        
        #Draw dline
    def _drawDline(self, view):
        """
        Draw the dline
        """
        self._dline.draw(view)

        
        #draw bolts
    def _drawBolts(self, view):
        """
        Draw the bolts
        """
        for i in range(len(self._bolts)):
            bolt=self._bolts[i]
            bolt.draw(view)

        
    def Aliens_Killed(self):
        """
        Glabel that shows the player their score from killing aliens
        """
        return GLabel(text='Score: '+str(self.getAliensKilled()), x=(GAME_WIDTH-90.0),y=(GAME_HEIGHT-40.0),
        font_size=30,font_name="Arcade.ttf", linecolor=cornell.RGB(255,255,0))

    def Ships_Killed(self):
        """
        Glabel that shows the player how many lives they have left
        """
        return GLabel(text='Lives: '+str(self.getLives()), x=(0+90.0),y=(GAME_HEIGHT-40.0),
        font_size=30,font_name="Arcade.ttf", linecolor=cornell.RGB(255,255,255))

    
    # HELPER METHODS FOR COLLISION DETECTION
    # COLLISION DETECTION
    def _crossed_the_line(self):
        """
        Causes the ship lives to become 0 (the player loses) if an alien touches the dline
        """
        for row in range(len(self._aliens)):
            for col in range(len(self._aliens[row])):
                alien=self._aliens[row][col]                 
                if (alien is not None) and (alien.y-(0.5*ALIEN_HEIGHT)) <= DEFENSE_LINE:
                    self._lives = 0
    
    def _aliens_defeated(self):
        """
        Changes the victory attribrute to True if all aliens have been killed
        """
        list=[]
        for row in range(len(self._aliens)):
            for col in range(len(self._aliens[row])):
                alien=self._aliens[row][col]
                if (alien is not None):
                    list.append(alien)
        if len(list)==0:
            self._victory=True
                    