import pygame
import math
import random
class Square:
    def __init__(self, size, position = [0,0]):
        #not doing any error checking, just implementation
        self.size = size
        self.dim = None
        self.position = position
        self.pixel_position = None
        #walls for the maze
        self.has_right_wall = True
        self.has_left_wall = True
        self.has_bottom_wall = True
        self.has_top_wall = True
        #if the square has been visited
        self.isVisited = False
        #square stuff 
        self.rect = None
        #visual stuff
        self.isCurrent = False
    
    def mapToGrid(self, left, top, col_width,row_width, offset = 0):
        self.position = [int(top),int(left)]
        self.dim = col_width
        self.pixel_position = [offset + math.floor(left*self.size), offset + math.floor(top*self.size)]
        # redundant but makes easier to distinguish difference
        self.rect = pygame.Rect(offset + math.floor(left*self.size), offset + math.floor(top*self.size), col_width, row_width)
    
    def draw(self, screen):
        if(self.isCurrent == True):
            pygame.draw.rect(screen, (255,0,0),self.rect)
        elif(self.isVisited == True):
            pygame.draw.rect(screen, (0,255,0),self.rect)
        else:
            pygame.draw.rect(screen, (0,0,0),self.rect)
        self.drawLines(screen)
    
    def drawLines(self,screen):
        #starting from top left corner of square
        #right left line -- top
        if self.has_top_wall:
            pygame.draw.line(screen, (0,0,0), self.pixel_position, [self.pixel_position[0] + self.dim, self.pixel_position[1]])
        # #up down line -- left
        if self.has_left_wall:
            pygame.draw.line(screen, (0,0,0), self.pixel_position, [self.pixel_position[0], self.pixel_position[1] +  self.dim])

        #starting from bottom left corner of square
        #right left line -- bottom
        if self.has_bottom_wall:
            pygame.draw.line(screen, (0,0,0), [self.pixel_position[0] - 1, self.pixel_position[1] +  self.dim - 1] , [self.pixel_position[0] + self.dim - 1, self.pixel_position[1] + self.dim - 1])
        #top down line -- right
        if self.has_right_wall:
            pygame.draw.line(screen, (0,0,0), [self.pixel_position[0] + self.dim - 1, self.pixel_position[1]], [self.pixel_position[0] + self.dim - 1, self.pixel_position[1] + self.dim - 1])
        

class Maze:
    def __init__(self,dim, background_color, renderer="pygame"):
        self.background_color = background_color
        self.dim = dim
        self.renderer = renderer
        self.previous_ele = None
        self.screen = self.create_screen(self.renderer, self.dim, self.background_color)
        self.ele_in_rows = 20

        #calculate the maze area and set appropriate offset for centering
        self.maze_area = (self.dim ** 2)
        self.maze_dim = int((self.maze_area * 0.9) ** 0.5)
        self.offset =  self.maze_dim * 0.025
        self.maze_rect = pygame.Rect(self.offset, self.offset, self.maze_dim, self.maze_dim)
        self.squares = self.create_squares(self.ele_in_rows,self.maze_dim ,self.offset)
        #recording of each move of the maze for playback I guess
        self.cache = []

    def chooseNeighbor(self, current):
        neighbors = []
        up = current.position[0] - 1
        down = current.position[0] + 1
        #check if up/down is valid
        if up < 0:
            up = 0
        elif down > self.ele_in_rows - 1:
            down = self.ele_in_rows - 1
        #check if left/right is valid
        left = current.position[1] - 1
        right = current.position[1] + 1
        if left < 0:
            left = 0
        elif right > self.ele_in_rows - 1:
            right = self.ele_in_rows - 1

        if self.squares[up][current.position[1]].isVisited == False:
            neighbors.append((self.squares[up][current.position[1]], 'up'))

        if self.squares[down][current.position[1]].isVisited == False:
            neighbors.append((self.squares[down][current.position[1]], 'down'))

        if self.squares[current.position[0]][left].isVisited == False:
            neighbors.append((self.squares[current.position[0]][left],'left'))

        if self.squares[current.position[0]][right].isVisited == False:
            neighbors.append((self.squares[current.position[0]][right],'right'))

        n = len(neighbors)
        if n > 0:
            idx = random.randint(0,n-1)
            return neighbors[idx]
        elif n == 0 and neighbors != []:
            return neighbors[0]

        return None

    def removeWall(self,current_node, chosen_node, direction):
        if direction == 'left':
            self.squares[current_node.position[0]][current_node.position[1]].has_left_wall = False
            self.squares[chosen_node.position[0]][chosen_node.position[1]].has_right_wall = False
        if direction == 'right':
            self.squares[current_node.position[0]][current_node.position[1]].has_right_wall = False
            self.squares[chosen_node.position[0]][chosen_node.position[1]].has_left_wall = False
        if direction == 'up':
            self.squares[current_node.position[0]][current_node.position[1]].has_top_wall = False
            self.squares[chosen_node.position[0]][chosen_node.position[1]].has_bottom_wall = False
        if direction == 'down':
            self.squares[current_node.position[0]][current_node.position[1]].has_bottom_wall = False
            self.squares[chosen_node.position[0]][chosen_node.position[1]].has_top_wall = False

    def generate(self):
        s1 = []
        self.squares[0][0].isVisited = True
        s1.append(self.squares[0][0])
        counter = 0
        current = None
        #save the current state of the squares
        self.cache.append(self.squares)
        
        while s1 != []:
            #initialization
            if counter == 0:
                current = s1.pop()
                self.squares[current.position[0]][current.position[1]].isCurrent = True

            counter += 1
            #choose the next random neighbor
            chosen_node = self.chooseNeighbor(current)
            yield self.squares
            if chosen_node != None:
                #follow the rule for maze generation
                s1.append(current)
                self.removeWall(current, chosen_node[0], chosen_node[1])
                self.squares[chosen_node[0].position[0]][chosen_node[0].position[1]].isVisited = True
                # #append the state to the cache
                # self.cache.append(self.squares)
                #update current and add to stack
                self.squares[current.position[0]][current.position[1]].isCurrent = False
                current = self.squares[chosen_node[0].position[0]][chosen_node[0].position[1]]
                self.squares[current.position[0]][current.position[1]].isCurrent = True
                s1.append(current)
            else:
                self.squares[current.position[0]][current.position[1]].isCurrent = False
                current = s1.pop()
                self.squares[current.position[0]][current.position[1]].isCurrent = True

    def create_squares(self, square_shape, maze_dim,offset):
        '''
        square_shape is how many squares will be rendered on each row
        maze_dim is the true length of the grid
        '''

        #calculate the size of each square
        square_size = maze_dim//square_shape
        #account for the offset of flooring the square_size
        next_offset = (maze_dim % square_shape)/2
        all_squares = []
        for row in range(square_shape):
            row_of_squares = []
            for col in range(square_shape):
                square = Square(square_size, [row,col])
                square.mapToGrid(col,row,square_size,square_size,offset + next_offset)
                row_of_squares.append(square)
            all_squares.append(row_of_squares)
        return all_squares

    def draw(self):
        pygame.draw.rect(self.screen,(255,255,255), self.maze_rect)
        for row in self.squares:
            for ele in row:
                ele.draw(self.screen)
        pygame.display.flip()

    def create_screen(self,renderer, dimension, background_color):
        if renderer == "pygame":
            #pygame specific attributes for the screen and the event system brought in
            screen = pygame.display.set_mode((dimension, dimension))
            pygame.display.set_caption('Maze Algorithm')
            screen.fill(background_color)
            return screen

background_color = (0,0,0)
maze = Maze(800,background_color)
#create the maze once and rerender each pass
mazes = maze.generate()
running = True
pygame.init()
now = pygame.time.get_ticks()
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  if abs(now - pygame.time.get_ticks()) > 10:
      now = pygame.time.get_ticks()
      try:
        next(mazes)
      except:
          pass
      
  maze.draw()