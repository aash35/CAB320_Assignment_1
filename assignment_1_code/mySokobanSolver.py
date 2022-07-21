
'''

    Sokoban assignment


The functions and classes defined in this module will be called by a marker script. 
You should complete the functions and classes according to their specified interfaces.

No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.

You are NOT allowed to change the defined interfaces.
In other words, you must fully adhere to the specifications of the 
functions, their arguments and returned values.
Changing the interfacce of a function will likely result in a fail 
for the test of your code. This is not negotiable! 

You have to make sure that your code works with the files provided 
(search.py and sokoban.py) as your code will be tested 
with the original copies of these files. 

Last modified by 2022-03-27  by f.maire@qut.edu.au
- clarifiy some comments, rename some functions
  (and hopefully didn't introduce any bug!)

'''

# You have to make sure that your code works with 
# the files provided (search.py and sokoban.py) as your code will be tested 
# with these files
import search
from search import Problem, Node, FIFOQueue
import itertools
import sys


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    '''
    Return the team members and their student codes for this assignment submission as a list 
    of tuples in the form (student_number, first_name, last_name)
    
    @param: 
        N/A

    @return:
       A list of the 3 members of our team:
        - Adrian Ash: n10624937
        - Chiran Walisundara: n10454012
        - Don Kaluarachchi: n10496262 

    '''
    return [ (10624937, 'Adrian', 'Ash'), (10454012, 'Chiran', 'Walisundara'), 
            (10496262, 'Don', 'Kaluarachchi') ]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def taboo_graph_search(problem, frontier):
    """
    A modified graph search method that search through the successors 
    of a problem adding the state (grid locations) of each node to an explored variable.

    Used by taking a SokobanPuzzle (problem subclass) object
    and an empty queue object.

    Returns all the grid locations that are within the walls of the
    SokobanPuzzles warehouse object.
    
    @params: 
        problem - a problem (or subclass) object
        frontier - a queue object (whether it be FIFOQueue or LIFOQueue)

    @return:
       explored - a set of all the visited states
    """
    #ensure the problem object is the same as the problem class (we use a subclass called SokobanPuzzle)
    assert isinstance(problem, Problem)

    #append the initial state from the problem object (see SokobanPuzzle for state definition)
    frontier.append(Node(problem.initial))

    explored = set() # initial empty set of explored states
    while frontier:
        node = frontier.pop()
        explored.add(node.state)
        # use the queue objects .extend() function to add the child states
        # of the current state if they have not been explored before
        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored
                        and child not in frontier)
    # return explored set which has all the grid locations visited by the agent
    return explored


def taboo_cells(warehouse):
    '''  
    A method used to discover all the taboo cells located within a warehouse object.
    Will return a string representation of all the taboo locations and wall locations
    marked as "#" for walls and "X" for taboo cells.

    A "taboo cell" is by definition:
        - a cell inside a warehouse such that whenever a box get pushed on such 
          a cell then the puzzle becomes unsolvable. 
    
    Cells outside the warehouse are not taboo. It is a failure to tag an 
    outside cell as taboo. Additionally, we will ignore all the existing boxes, 
    only consider the walls and the target cells. 

    
    With the above definition, we can determine the rules that define a taboo cell as:
        Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
        Rule 2: all the cells between two corners along a wall are taboo if none of 
                these cells are a target.

    @params: 
        warehouse - a Warehouse object with the worker inside the warehouse

    @return:
        returnString - A string representing the warehouse with only the wall cells marked with 
                      a '#' and all the discovered taboo cells marked with an 'X'.  
    '''
    #string representation of the warehouse
    warehouseString = warehouse.__str__()
    
    #creates a list of each row of our warehouse
    warehouseArray = warehouseString.split("\n")
    
    #extract the worker, wall and target locations from the warehouse object
    workerLocation = warehouse.worker
    wallLocations = warehouse.walls
    targetLocations = warehouse.targets
    
    #reverse the grid locations into a (row, column) format instead of (column, row) format
    #For example (4,6) will be (6,4)
    #NOTE: done purely for our own visualisation of the problems
    targetLocations = [x[::-1] for x in targetLocations]
    workerLocation = workerLocation[::-1]
    wallLocations = [x[::-1] for x in wallLocations]


    #loops through the rows removing everything but the walls ("#")
    for x in range(warehouse.nrows):                
        warehouseArray[x] = warehouseArray[x].replace('$',' ')
        warehouseArray[x] = warehouseArray[x].replace('@',' ')  
        
        warehouseArray[x] = warehouseArray[x].replace('!',' ')
        warehouseArray[x] = warehouseArray[x].replace('*',' ')
        warehouseArray[x] = warehouseArray[x].replace('.',' ')                       

    #create the SokobanPuzzle object with the warehouse and the emptyWarehouseFlag set to 1
    #NOTE: emptyWarehouseFlag explained in SokobanPuzzle class
    wh = SokobanPuzzle(warehouse=warehouse, emptyWarehouseFlag=1)
    
    # Uses a modified graph_search algorithm to return a set of all the grid cells within
    # the walls ("#") of the warehouse object
    exploredCells = taboo_graph_search(problem = wh, frontier = FIFOQueue())

    tabooCells = []    
    #loops through the exploredCells and adds all corner (non-goal) cells to the tabooCells list
    for cells in exploredCells:
        row = cells[0][0]
        column = cells[0][1]
        if (row,column) not in targetLocations:
            if (row+1, column) in wallLocations or (row-1, column) in wallLocations:
                if (row, column+1) in wallLocations or (row, column-1) in wallLocations:
                    tabooCells.append(cells[0])

    #uses itertools.combinations to get all possible combinations of corners in groups of 2
    # For example:
    #       tabooCells = [(4,6), (2,3), (5,3)]
    #       then combinationOfCorners = [((4,6),(2,3)), ((4,6),(5,3)), ((2,3),(5,3))]
    combinationOfCorners = itertools.combinations(tabooCells, 2)
    
    sameLineCorners = []
    # get a list of all the corner combinations that are on the same column or row
    for x in combinationOfCorners:
        leftCorner = x[0]
        rightCorner = x[1]
        #if same row
        if leftCorner[0] == rightCorner[0]:
            #ensure the lowest row number is positioned on the left for next section
            if leftCorner[1] < rightCorner[1]:
                sameLineCorners.append(x)
            else:
                sameLineCorners.append((rightCorner, leftCorner))
        #if same column
        if leftCorner[1] == rightCorner[1]:
            #ensure the lowest row number is positioned on the left for next section
            if leftCorner[0] < rightCorner[0]:
                sameLineCorners.append(x)
            else:
                sameLineCorners.append((rightCorner, leftCorner))


    inbetweenTabooCorners = []
    # get a list of all the corner combinations that have taboo cells between them
    for x in sameLineCorners:
        leftCorner = x[0]
        rightCorner = x[1]
        # on same row
        if leftCorner[0] == rightCorner[0]:
            tabooBoolean = 0
            row = leftCorner[0]
            #check all the column cell inbetween two row corners
            for col in range(leftCorner[1], rightCorner[1]):
                #if it is either a wall or goal location, break and set tabooBoolean to 1
                if (row,col) in targetLocations or (row, col) in wallLocations:
                    tabooBoolean = 1
                    break
                #if all surrounding cells are not wall, break and set tabooBoolean to 1
                if (row+1, col) not in wallLocations and (row-1, col) not in wallLocations and (row, col+1) not in wallLocations and (row, col-1) not in wallLocations:
                    tabooBoolean = 1
                    break
            #if none of the above conditions are met then add the corners that have taboo cells inbetween them into inbetweenTabooCorners
            if tabooBoolean == 0:
                inbetweenTabooCorners.append(x)
        # on same column (same as above except checks all the rows inbetween two matching columns)
        if leftCorner[1] == rightCorner[1]:
            tabooBoolean = 0
            col = leftCorner[1]
            for row in range(leftCorner[0], rightCorner[0]):
                if (row,col) in targetLocations or (row, col) in wallLocations:
                    tabooBoolean = 1
                    break
                if (row+1, col) not in wallLocations and (row-1, col) not in wallLocations and (row, col+1) not in wallLocations and (row, col-1) not in wallLocations:
                    tabooBoolean = 1
                    break
            if tabooBoolean == 0:
                inbetweenTabooCorners.append(x)

    #adds all the cells inbetween the corner cells to our tabooCells variable
    #NOTE: for the stake of clarity this section was created seperatly from the above loop
    for cornerPair in inbetweenTabooCorners:
        leftCorner = cornerPair[0]
        rightCorner = cornerPair[1]
        #if same row
        if leftCorner[0] == rightCorner[0]:
            row = leftCorner[0]
            #loop through inbetween cells
            for col in range(leftCorner[1]+1, rightCorner[1]):
                #add to tabooCells
                tabooCells.append((row,col))
        #if same column
        if leftCorner[1] == rightCorner[1]:
            col = leftCorner[1]
            #loop through inbetween cells
            for row in range(leftCorner[0]+1, rightCorner[0]):
                #add to tabooCells
                tabooCells.append((row,col))

    # set all the taboo cells within the warehouseArray variable to "X"
    for row in range(len(warehouseArray)):
        for column in range(len(warehouseArray[row])):
            if (row,column) in tabooCells:
                # splits the original strings into left and right and adding the taboo "X"
                # in the correct location
                warehouseArray[row] = warehouseArray[row][:column] + "X" + warehouseArray[row][column+1:]
    
    returnString = "\n".join(warehouseArray)

    #NOTE: for testing purposes - to test all correct cells have been set
    #print(returnString)
    
    return returnString
    
        
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class SokobanPuzzle(search.Problem):
    '''
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the box weights,
    various helper flags and the initial box locations and worker location.

    This class is a subclass of the Problem class from the search file and overwrites multiple
    functions that require unique implementations for solving the Sokoban Puzzle.

    This object is compatible with multiple search algorithms that are also present in the search file
    and which will be used to find potential solutions to a given warehouse.      
    '''
    def __init__(self, warehouse, emptyWarehouseFlag = 0, tabooFlag = 0):
        '''  
        Using the Warehouse object passed into this constructor various important information is extracted
        and set of SokobanPuzzle object variables. 
        
        Additionally, two separate flags are set that modify the behaviour of the objects, 
        with emptyWarehouseFlag used by taboo_cells() and tabooFlag used by check_elem_action_seq()

        This is also where the initial state is set. Will take the form of a tuple of tuples. The first
        tuple is the location of the worker. All following tuples will represent the locations of the boxes.
        This is how the state will be represented for the rest of the functions as well.
            An Example: ((4,6),(2,3),(1,2))
                - Here the worker is located in row 4 column 6
                - The boxes are located in rows 2 and 1 and columns 3 and 2 respectively
                - NOTE: the rows and columns are flipped from the original warehouse object so as
                        to match our initial taboo_cells() design. No significant reason but our own
                        continuity

        @params: 
            warehouse - a valid Warehouse object

            emptyWarehouseFlag - a flag used for setting the initial state without box locations
                                    - Used by taboo_cells() which does not make use of box locations

            tabooFlag - a flag used by actions() to define if the taboo cells should be checked
                        when searching are legal actions to take
                                    - Used by check_elem_action_seq() which does not need to check taboo cells for
                                    legal moves 
        '''
        #extract the useful information from warehouse object
        workerLocation = warehouse.worker
        boxLocations = warehouse.boxes
        wallLocations = warehouse.walls
        targetLocations = warehouse.targets
        
        workerLocation = workerLocation[::-1]
        # The Initial State - all dynamic elements of the warehouse
        # if emptyWarehouseFlag = 0, the initial will be set with the player plus all box locations
        if emptyWarehouseFlag == 0:
            boxLocations =  tuple([x[::-1] for x in boxLocations])
            self.initial = (workerLocation,) + boxLocations
        #else initial will be set with just a workerLocation
        else:
            self.initial = (workerLocation,)

        #set the remaining object variables (the static elements of the warehouse)
        self.weights = warehouse.weights
        self.targetLocations = [x[::-1] for x in targetLocations]
        self.wallLocations = [x[::-1] for x in wallLocations]
        self.warehouse = warehouse
        self.tabooFlag = tabooFlag

    def tabooCellFinder(self):
        '''  
        An auxiliary helper function used by solve_weighted_sokoban() to extract the taboo cell locations from
        the warehouse and set them as SokobanPuzzle variables. 
        
        This function will make use of the taboo_cells() function to return of string of a warehouse
        with the taboo cells defined.
        
        The tabooCells that are set will take the form of a tuple of tuples depicting all the taboo cells
        grid locations.
            An Example: ((1, 3), (2, 7), (5, 9))
                - Here the taboo cells are located at rows 1, 2 and 5 and columns 3,7 and 9 respectively
        '''
        #use our taboo_cells function to get a string representation of the taboo cells
        warehouseString = taboo_cells(self.warehouse)
        warehouseArray = warehouseString.split("\n")
        tabooCellsWarehouse = []
        #loop through all the rows and columns and add all the grid locations of the taboo cells
        # to tabooCellsWarehouse list
        for x in range(len(warehouseArray)):
            for y in range(len(warehouseArray[x])):
                if warehouseArray[x][y] == "X":
                    tabooCellsWarehouse.append((x,y))
        
        #set the cells as tuple of tuples denoting the tabooCells grid locations
        self.tabooCells = tabooCellsWarehouse
        self.tabooCells = tuple(self.tabooCells)

    def actions(self, state):
        '''  
        Uses the state variable provided, which is a tuple of tuples in the same format as the 
        initial variable set in __init__ with the first tuple defining the worker location and the following
        tuples defining the box locations.

        Given this state variable, it calculates all the possible moves that the agent can perform. The behaviour of this
        function is also modified based on if the emptyWarehouseFlag and tabooFlag were set in the constructor (__init__):
            
            emptyWarehouseFlag = 1 - means that the state will only contain the worker location and will only search based on if the
                                 worker will hit a wall "#" or not
            tabooFlag = 1 - will ignore if the worker move will push a box into a taboo cell or not
        
        Without the flags the function will check:
            1) will a worker's movement result in hitting the wall
            2) will a workers movement result in hitting a box
                if so
                2.a) will the box movement result in hitting the wall or another box
                2.b) will the box movement result in the box entering a tabooCells or not
        
        Depending on which above conditions are met different actions are added to legalActions which results
        in this function finally returning all possible moves the agent (worker) can make from their current location

        @param: 
            state - a tuple of tuples defining the worker and box locations 
                    defined the same as the __init__ function sets the initial variable
        @return:
            legalActions - a list of legal actions that can be taken given the current state

        '''
        # worker locations (row and column respectively)
        workerRow = state[0][0]
        workerColumn = state[0][1]

        legalActions = []

        # Up
        #if the up location of the worker is not a wall
        if (workerRow-1, workerColumn) not in self.wallLocations:
            #if the up location of the worker is a box
            if(workerRow-1, workerColumn) in state[1:]:
                #if the up location of the box is not a box or wall
                if(workerRow-2, workerColumn) not in self.wallLocations and (workerRow-2, workerColumn) not in state[1:]:
                    if self.tabooFlag != 1:
                        #if the up location of the box is not a taboo cell
                        if(workerRow-2, workerColumn) not in self.tabooCells:
                            #add "Up" as a legal action
                            legalActions.append("Up")
                    else:
                        #add "Up" as a legal action
                        legalActions.append("Up")
            else:
                #add "Up" as a legal action
                legalActions.append("Up")
            

        # Down
        # NOTE: same layout as "Up" but with "Down"
        if (workerRow+1, workerColumn) not in self.wallLocations:
            if(workerRow+1, workerColumn) in state[1:]:
                if(workerRow+2, workerColumn) not in self.wallLocations and (workerRow+2, workerColumn) not in state[1:]:
                    if self.tabooFlag != 1:
                        if(workerRow+2, workerColumn) not in self.tabooCells:
                            legalActions.append("Down")
                    else:
                        legalActions.append("Down")
            else:
                legalActions.append("Down")

        # Left
        # NOTE: same layout as "Up" but with "Left"
        if (workerRow, workerColumn-1) not in self.wallLocations:
            if(workerRow, workerColumn-1) in state[1:]:
                if(workerRow, workerColumn-2) not in self.wallLocations and (workerRow, workerColumn-2) not in state[1:]:
                    if self.tabooFlag != 1:
                        if(workerRow, workerColumn-2) not in self.tabooCells:
                            legalActions.append("Left")
                    else:
                        legalActions.append("Left")
            else:
                legalActions.append("Left")
            
        # Right
        # NOTE: same layout as "Up" but with "Right"
        if (workerRow, workerColumn+1) not in self.wallLocations:
            if(workerRow, workerColumn+1) in state[1:]:
                if(workerRow, workerColumn+2) not in self.wallLocations and (workerRow, workerColumn+2) not in state[1:]:
                    if self.tabooFlag != 1:
                        if(workerRow, workerColumn+2) not in self.tabooCells:
                            legalActions.append("Right")
                    else:
                        legalActions.append("Right")
            else:
                legalActions.append("Right")
        return legalActions

    def result(self, state, action):
        '''  
        Uses the state and action variable provided this function will move the worker's location and if the
        action results in the worker pushing a box then the location of said box will also be moved.

        It will define these changes as the next_state and will return a tuple of next_state

        @params: 
            state - a tuple of tuples defining the worker and box locations 
            action - a single action from the list returned from the actions() function
                        For Example: if actions() returns ['Up', 'Right']
                                     then the action passed maybe 'Up' or 'Right' 
        @return:
            tuple(next_state) - a tuple representation of the next state
                                    NOTE: the same format as all states. A tuple of tuples with the
                                    first tuple denoting the worker location and the remaining tuples
                                    denoting the box's locations

        '''
        #get the next_state as the current state (that will be modified based on action)
        next_state = list(state)

        # worker locations (row and column respectively)
        workerRow = state[0][0]
        workerColumn = state[0][1]
        assert action in self.actions(state)  # double check the action received is a legal action

        # UP
        if action == 'Up':
            #if the up location of the worker is a box
            if(workerRow-1, workerColumn) in state[1:]:
                #loop through the boxes
                for x in range(len(state[1:])):
                    #if the box location is the new worker location
                    if next_state[x+1] == (workerRow-1, workerColumn):
                        #set that box in the next state up by one
                        #NOTE: actions() does the preprocessing, thus we know this move is legal
                        next_state[x+1] = (workerRow-2, workerColumn)

            agentLocation = (workerRow-1, workerColumn)
            #set the next state worker location up by one
            next_state[0] = agentLocation
        
        # DOWN
        # NOTE: same layout as "Up" but with "Down"
        if action == 'Down':  
            if(workerRow+1, workerColumn) in state[1:]:
                for x in range(len(state[1:])):
                    if next_state[x+1] == (workerRow+1, workerColumn):
                        next_state[x+1] = (workerRow+2, workerColumn)

            agentLocation = (workerRow+1, workerColumn)
            next_state[0] = agentLocation

        # Left
        # NOTE: same layout as "Up" but with "Left"
        if action == 'Left':
            if(workerRow, workerColumn-1) in state[1:]:
                for x in range(len(state[1:])):
                    if next_state[x+1] == (workerRow, workerColumn-1):
                        next_state[x+1] = (workerRow, workerColumn-2)

            agentLocation = (workerRow, workerColumn-1)
            next_state[0] = agentLocation
        
        # RIGHT
        # NOTE: same layout as "Up" but with "Right"
        if action == 'Right':
            if(workerRow, workerColumn+1) in state[1:]:
                for x in range(len(state[1:])):
                    if next_state[x+1] == (workerRow, workerColumn+1):
                        next_state[x+1] = (workerRow, workerColumn+2)

            agentLocation = (workerRow, workerColumn+1)
            next_state[0] = agentLocation

        #make sure the next_state is a tuple (required for search algorithms)
        return tuple(next_state)  # use tuple to make the state hashable

    def goal_test(self, state):
        '''  
        Uses the state provided return true of all the locations of the boxes are on the targetLocations

        For Example -
                   currentBoxLocations = ((4,6), (2,3))
                   targetLocations = ((4,6), (2,3))
                   Will return true

                   Whereas

                   currentBoxLocations = ((4,5), (2,3))
                   targetLocations = ((4,6), (2,3))
                   Will return false
        
        NOTE: since we are using set representations of both currentBoxLocations and targetLocations
              the order of the locations will not matter

              For Example -
                   currentBoxLocations = ((4,6), (2,3))
                   targetLocations = ((2,3), (4,6))
                   Will still return true
        @param: 
            state - a tuple of tuples defining the worker and box locations
        @return:
            result - a boolean value (true or false) denoting if the goal condition has been met
                     Defined by all currentBoxLocation being positioned on all the targetLocations
        '''
        #gets the box locations from the states
        currentBoxLocations = state[1:]
        # returns true or false based on if all the currentBoxLocations are on the targetLocations
        result = set(currentBoxLocations) == set(self.targetLocations)
        return result

    def path_cost(self, c, state1, action, state2):
        '''  
        Using the state1 and state2 we determine if a box location, stored in all the tuples of the state but the first,
        has changed between the states and if it has then add the weight of the box to the result variable.

        The result will be a combination of the cost of the previous actions up till state2 (c) + the default cost of an
        action (1) + the cost of moving a box (if there is one)

        @params:
            c - the cost of the solution path up to state1
            state1 - a tuple of tuples defining the worker and box locations before the action
            action - the action taken from state1 to get to state2 
                        NOTE: not used for our solution
            state2 - a tuple of tuples defining the worker and box locations after the action

        @return:
            result - the cost of the solution path up to state2 coming from state1
                     given the action
        '''
        cost = 0
        costOfWorkerMove = 1
        #loop through the boxes of state1 and state2 (same index)
        for x in range(len(state1[1:])):
            #if the box in state1 does not equal the box in state2
            if state1[x+1] != state2[x+1]:
                # this means the box has moved and as such the cost equals the weight of that box
                cost = self.weights[x]
        result = c + costOfWorkerMove + cost
        return result

    def h(self, n):
        '''  
        Uses the input n (a node object) to calculate a heuristic to help determine the best action the worker
        can take to reach the goal state.
        
        The heuristic is defined as:
            1.) Worker to box
                - The manhattan distance from the worker to a box
            2.) Box to goal
                - The minimum manhattan distance from the box to a goal (shortest path to goal)
            3.) After each box iteration the maximum of these combined values is set as the return value
            4.) Boxes that have reached the goal state are not checked
                - This essentially turns the heuristic into the smaller admissible subproblems of getting the box to the nearest goal
                - Within these subproblems, the heuristic is admissible and consistent
                    - NOTE: that is means however that for the larger problem as a whole the heuristic
                            is not consistent, this consistency is the main issue with multi-goal problems

        @param:
            n - a node object (contains the current state)

        @return:
            completeToGoal - the calculated heuristic used to guide the agent to the goal state
        '''
        #extracts the worker and box locations from the state
        workerLocation = n.state[0]
        boxLocation = n.state[1:]
        goalLocation = self.targetLocations
        
        #NOTE: Solution 1 (main solution) - works, decent speed      
        completeToGoal = 0
        #loops through each box in boxLocation
        for box in boxLocation:
            #sets minBoxToGoal to a maximum integer value so that min() will always be updated
            minBoxToGoal = sys.maxsize
            #ignores boxes that are on the goal location
            if box not in goalLocation:
                #manhattan distance from worker to the box
                workerDistance = abs(workerLocation[0] - box[0]) + abs(workerLocation[1] - box[1]) - 1
                #loops through each goal location and calculating the minimum manhattan distance to the box
                for y in range(len(goalLocation)):
                    boxDistance = abs(box[0] - goalLocation[y][0]) + abs(box[1] - goalLocation[y][1])
                    minBoxToGoal = min(boxDistance, minBoxToGoal)
                # set the return value to the maximum of the combination of minBoxToGoal and workerDistance values
                completeToGoal = max(completeToGoal, minBoxToGoal + workerDistance)

        #print(completeToGoal) #for testing purposes
        return completeToGoal
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    '''
    Determine if the sequence of actions listed in 'action_seq' is legal or not.
    This does not necessarily mean solving the puzzle or pushing a box into a taboo cell.

    This is to check if the set of actions can be performed legally. The illegal moves are:
        - If the worker tries to move into a wall
        - If the worker tries to push a box into another box
        - If the worker tries to push a box into a wall

    Will return the state if all actions are successful and will return "Impossible" if an action
    is an illegal move

    @params: 
        warehouse - a valid Warehouse object
        action_seq - a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
           
    @return:
        result - The string 'Impossible', if one of the actions was not valid.
                    - For example, if the agent tries to push two boxes at the same time,
                                    or push a box into a wall.
                Otherwise, if all actions were successful, return                 
                    A string representing the state of the puzzle after applying
                    the sequence of actions.
    '''
    #create the SokobanPuzzle object with the warehouse and the tabooFlag set to 1
    #NOTE: tabooFlag explained in SokobanPuzzle class
    wh = SokobanPuzzle(warehouse=warehouse, tabooFlag=1)
    state = wh.initial
    #loop through the given actions
    for action in action_seq:
        #get the legal actions from the action() function
        legalActions = wh.actions(state=state)

        #if the action is with the legal actions
        if action in legalActions:
            #change the state
            state = wh.result(state=state, action=action)
        else:
            #otherwise the return is "Impossible"
            return "Impossible"

    #if it makes it through all the action_seq then it is legal
    #extract the important information from the state and return it to (column,row) format
    worker = state[0]
    worker = worker[::-1]
    boxes =  tuple([x[::-1] for x in state[1:]])

    #use the warehouse .copy() to create the new warehouse object with the new positions
    warehouseFinish = warehouse.copy(worker=worker, boxes=boxes, weights = wh.weights)
    result = warehouseFinish.__str__()
    return result


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_weighted_sokoban(warehouse):
    '''
    This function analyses the given warehouse. It will use the A Star Graph Search algorithm
    to search our problem space for a solution that fits our goal state (which is defined by all
    boxes on a goal/target location).

    It returns the two items. The first item is an action sequence solution. 
    The second item is the total cost of this action sequence.
    
    @param:
        warehouse - a valid Warehouse object

    @returns:
        If a puzzle cannot be solved
            answer - a string of "Impossible
            cost - None

        If a solution was found 
            answer - A list of actions that solve the puzzle
                For example: ['Left', 'Down', Down','Right', 'Up', 'Down']
            cost - The total cost of actions taken to get the solution
                For example: 26
    '''
    #create the SokobanPuzzle object with the warehouse
    wh = SokobanPuzzle(warehouse=warehouse)

    #use the SokobanPuzzle .tabooCellFinder() function set the tabooCells within our SokobanPuzzle object
    wh.tabooCellFinder()

    #use A Star Graph Search which returns a node if there is a solution or None if there is no solution
    result = search.astar_graph_search(problem = wh)

    #if the result is None then no possible solution was found
    if result == None:
        return "Impossible", None

    # if there was a solution found, use the .path() function 
    # from the node class to get the path (node objects) that led to the solution  
    path = result.path()
    actionsTaken = []

    #loop through all those nodes and extract the action that was taken for that node
    for node in path[1:]:
        actionsTaken.append(node.action)
    
    #NOTE: for testing purposes - quick check to see if the goal state 
    #was reached and the path it took to get there
    # print("This is the path: ")
    # print(actionsTaken)
    # print("This is state")
    # print(result.state)
    # print(wh.targetLocations)

    answer, cost = actionsTaken, result.path_cost
    
    return answer, cost


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -