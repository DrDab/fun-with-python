"""
LESSON: 3.4 - Program Structure
EXERCISE: Code Your Own

TITLE: [Your Title Here]
DESCRIPTION: [Your Description Here]
"""

import pygame
pygame.init()

# 8x8 2D array to hold starting and ending positions, initialized with start on top left and end on bottom right
# 0 = hallways
# 1 = wall
# 2 = start
# 3 = exit
maze = [[2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 3]]

explored = [[0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]]

# rgb color presets for tile colors.
# colors[0] = black, color for unexplored hallways
# colors[1] = white, color for walls
# colors[2] = cyan, color for starting area
# colors[3] = orange, color for finish area
# colors[4] = pink, color for discovered hallways
colors = [(0, 0, 0),
          (255, 255, 255),
          (0, 120, 255),
          (253, 102, 0),
          (241, 156, 187)]

# a method to draw the contents of the 8x8 maze to an 800x800 window.
def draw_maze():
    # check for quit command while drawing maze as well, 
    # as drawing is time intensive and we don't want a delayed quit
    # in the main loop.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit
    w.fill([0, 0, 0])
    
    # iterate through each element in the map array.
    i = 0
    while i < 8:
        j = 0
        while j < 8:
            # draw a square corresponding to our current array coordinates.
            # set the colors based on whether the array location was explored.
            # if explored, make it amaranth pink.
            # otherwise, set it to the corresponding color for the obstacle.
            rekt = pygame.Rect(j * 100, i * 100, 100, 100)
            color = None
            if explored[i][j] == 1:
                color = colors[4]
            else:
                color = colors[maze[i][j]]
            pygame.draw.rect(w, color, rekt)
            j += 1
        i += 1
    pygame.display.flip()

# function to get the mouse position and add a corresponding wall
def mark_wall():
    x, y = pygame.mouse.get_pos()
    i = int(y / 100)
    j = int(x / 100)
    maze[i][j] = 1 # draw a wall there.
    draw_maze()
    
def unmark_wall():
    x, y = pygame.mouse.get_pos()
    i = int(y / 100)
    j = int(x / 100)
    maze[i][j] = 0 # destroy a wall there.
    draw_maze()

# recursive function to search the maze for an exit.
def floodfill(cur_i, cur_j):
    # make sure not to exceed array index bounds.
    if cur_i < 0 or cur_i > 7:
        return False
    if cur_j < 0 or cur_j > 7:
        return False
    
    # we have hit our finish line. terminate.
    # terminate and report back to previous recursive iteration
    # that the specific path branch was successful to end all recursion.
    if maze[cur_i][cur_j] == 3:
        return True
    
    # this area is a wall.
    # terminate and report back to previous recursive iteration
    # that the specific path branch was unsuccesful to end recursion
    # for that branch, but keep recurring for other branches.
    if maze[cur_i][cur_j] == 1:
        return False
    
    # we've explored the area already.
    # terminate and report back to previous recursive iteration
    # that the specific path branch was unsuccesful to end recursion
    # for that branch, but keep recurring for other branches.
    if explored[cur_i][cur_j] == 1:
        return False
    
    # mark the area as explored so future iterations will terminate 
    # if they hit explored spots to prevent infinite recursion
    explored[cur_i][cur_j] = 1
    
    draw_maze()
    # try going east
    if floodfill(cur_i, cur_j + 1) == True:
        return True
    
    # try going south
    if floodfill(cur_i + 1, cur_j) == True:
        return True
    
    # try going west
    if floodfill(cur_i, cur_j - 1) == True:
        return True
    
    # try going north
    if floodfill(cur_i - 1, cur_j) == True:
        return True
     
    # if none of the paths on this branch called go to the finish, 
    # then terminate this branch, returning that this branch
    # failed to find the finish.
    return False
        
w = pygame.display.set_mode([800, 800])

# draw the initial maze with nothing in it.
done = False
floodfill_running = False
draw_maze()

# main program loop.
while done == False:
    # check each event that comes in.
    # if user wants to quit, end the program loop.
    # if user clicks somewhere, add a wall to the array
    # in the corresponding position.
    # if user presses space bar, start maze solver algorithm.
    for event in pygame.event.get():
        etype = event.type
        if etype == pygame.QUIT:
            done = True
            break
        if etype == pygame.MOUSEBUTTONUP:
            mark_wall()
        if etype == pygame.KEYUP:
            if event.key == pygame.K_SPACE and floodfill_running == False:
                floodfill_running = True
                if floodfill(0, 0):
                    print("*notices ur exit route* UwU")
                else:
                    print("*blushes* o///o sowwy i can't find an exit OwO")
            elif event.key == pygame.K_a:
                mark_wall()
            elif event.key == pygame.K_d:
                unmark_wall()



# Turn in your Coding Exercise.
