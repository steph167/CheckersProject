import time
import pygame
import sys # used for getting the max and min integers
from copy import deepcopy
pygame.init()


class Counter:
    """
    A class to represent each counter on a board

    ...
    Attributes
    -----------
    colour : string
        The colour of the counter as a string
    king : Boolean
        If the counter is a king this value is True
    pos : list
        Contains the row and column of the counter


    Methods
    -------
    updatePos(row, col)
        updates the counters pos (position) to the new row and column
    makeKing()
        changes king to True
    """
    def __init__(self, colour, row, col):
        self.colour = colour
        self.king = False
        self.pos = [row,col]

    def updatePos(self, row, col):
        self.pos = [row, col]

    def makeKing(self):
        self.king = True

class Board:
    """
    A class to represent the checkers board and to find the moves for the checkers

    ...
    Attributes
    -----------
    board : list
        Is a list of lists that represents the board in list form, when initialised all the counter objects are initialised too
    reds : int
        The number of red counters
    redKings : int
        The number of red kings
    blacks : int
        The number of black counters
    blackKings : int
        The number of black kings
    validMoves : list
        Contains the list of valid moves that the current selected counter may take
    deleltedCheckers : list
        Contains 2 values, one value is the position of the valid move after the hop, the other is the object of the counter which is deleted

    Methods
    -------
    checkerPresent(row, cow)
        checks to see if there is a counter present in the position - row , col in board, returns None or the counter object if counter present
    checkWinner()
        returns the colour of the player if they have won (due to looking at the checkers left on the board) or returns None if there is not yet a winner
    checkValidMoves(counter)
        takes a counter as the parameter and finds the valid moves by traversing left and right, blacks can only go down, reds can only go up and kings can go either
    searchMove( row, col, oppColour, validRow, leftOrRight, hopped)
        looks to see if a hop is avaliable using validRow and leftOrRight to find new positions, can only hop a counter if it is an oppositions colour (oppColour)
    movePiece (self, counter, row, col)
        This method takes a counter updates it into the position row, col, if the counter lands on a kings row, the counter becomes a king
    delPiece(self, delChecker, fromChecker)
        This method runs when a hop has occured, the delChecker object is deleted and if this deleted counter is a king, the checker fromChecker is made into a king
    returnNoCounters()
        returns the number of counters for each player, it is used in the minimax evaluation function
    """
    def __init__(self):
        self.board = [[None,Counter("black", 0, 1), None, Counter("black", 0, 3), None,Counter("black", 0, 5), None, Counter("black", 0, 7)],
                      [Counter("black", 1, 0), None, Counter("black", 1, 2), None, Counter("black", 1, 4), None, Counter("black", 1, 6), None],
                      [None, Counter("black", 2, 1), None, Counter("black", 2, 3), None, Counter("black", 2, 5), None, Counter("black", 2, 7)],
                      [None,None,None,None,None,None,None,None],
                      [None,None,None,None,None,None,None,None],
                      [Counter("red", 5, 0), None, Counter("red", 5, 2), None, Counter("red", 5, 4), None, Counter("red", 5, 6), None],
                      [None,Counter("red", 6, 1), None, Counter("red", 6, 3), None,Counter("red", 6, 5), None, Counter("red", 6, 7)],
                      [Counter("red", 7, 0), None, Counter("red", 7, 2), None, Counter("red", 7, 4), None, Counter("red", 7, 6), None]]
        self.reds = 12
        self.redKings = 0
        self.blacks = 12
        self.blackKings = 0
        self.validMoves = []
        self.deletedCheckers = []


    def checkerPresent(self, row, col):
        return self.board[row][col]

    def checkWinner(self):
        if self.reds <= 0:
            return "black"
        elif self.blacks <= 0:
            return "red"
        return None

    def checkValidMoves(self, counter):
        row, col = counter.pos
        if counter.colour == "black": # find the oppostions counter colour
            opp = "red"
        else:
            opp = "black"

        #players can only move in their direction, kings can move in both
        if counter.colour == "black" or counter.king == True:  # black counters can only move down
            validRow = 1 
            self.searchMove(row, col, opp, validRow, -1, []) # traverses left and down the board from current position
            self.searchMove(row, col, opp, validRow, 1, []) # traverses right and down the board from current position
        if counter.colour == "red" or counter.king == True: # red counters can only move up
            validRow = -1 
            self.searchMove(row, col, opp, validRow, -1, []) # traverses left and up the board from current position
            self.searchMove(row, col, opp, validRow, 1, []) # traverses right and up the board from current position
            
        if len(self.deletedCheckers) > 0: #ensures forced capture - the player must choose a capture if there is an opportunity
            chooseDel = []
            for pos, hopped in self.deletedCheckers: # for the position of the valif move, the object that will be deleted
                if pos in self.validMoves:
                    chooseDel.append(pos)
            self.validMoves = chooseDel # override the valid moves due to forced capture
        return self.validMoves, self.deletedCheckers

        
    
    def searchMove(self, row, col, oppColour, validRow, leftOrRight, hopped):
        newRow = row + validRow # the potential new row position of a valid move
        newCol = col + leftOrRight # the potential new column position of a valid move
        if (0 <= newRow <= 7) and (0 <= newCol <= 7):  #if the move would not go over the board dimentions
            counterPresent = self.checkerPresent(newRow, newCol) # what counter is present at this new position
            if hopped == [] and counterPresent == None: # if there has not yet been a hop and their is no counter present, this square is valid with no hops
                self.validMoves.append([newRow, newCol])
            elif hopped != [] and counterPresent == None: # if there is no counter in a position, and a hop has taken place, the square is invalid due to after one hop can only complete another hop, not a normal valid move
                return
            elif counterPresent.colour == oppColour: # if the counter is equal to the oppositions counter, another hop could take place if the next square is valid
                hopRow = newRow + validRow # a new position of the potential hop after passing the oppositions counter
                hopCol = newCol + leftOrRight
                if (0 <= hopRow <= 7) and (0 <= hopCol <= 7): # if the new hop is within the board dimentions
                    newHopSquare = self.checkerPresent(hopRow, hopCol) 
                    if newHopSquare == None: # if the square to hope to is empty, a hop can take place
                        self.validMoves.append([hopRow, hopCol]) # this hop is valid
                        newHop = hopped.copy() # had to copy as if not it rewrites hopped in other places
                        newHop.append(counterPresent) # added to the list of hops for possible multiple hops
                        self.deletedCheckers += [[[hopRow, hopCol], newHop]]
                        if (0 < hopRow < 7) or (counterPresent.king != True): # at the kings line or a counter can be made into a king therefore the turn hults 
                            self.searchMove(hopRow, hopCol, oppColour, validRow, -1, newHop) # if not then we can traverse again for another hop in both directions
                            self.searchMove(hopRow, hopCol, oppColour, validRow, 1, newHop)
    
        return


    def movePiece(self, counter, row, col): # moving the counter to its new position located at row, col
        self.board[row][col] = counter # updates self.baord position to its new place, leaving its old position as a None value
        self.board[counter.pos[0]][counter.pos[1]] = None 
        counter.updatePos(row, col) # updates the counter object
        if (row == 7 or row == 0) and (counter.king == False): # doesn't matter which row as cannot move backwards until is a king anyway
            counter.makeKing() # new counter becomes a king
            if counter.colour == "black":
                self.blackKings += 1
            else:
                self.redKings += 1


    def delPiece(self, delChecker, fromChecker):
        self.board[delChecker.pos[0]][delChecker.pos[1]] = None # resets the deleted counter's position on the board to None
        if delChecker.colour == "black": # other board parameters are updated
            self.blacks -= 1
            if delChecker.king == True:  
                self.blackKings -= 1
                if fromChecker.king == False: #Regicide - if the counter that has been deleted is a king the new counter becomes one (if not already)
                    self.redKings += 1
                    fromChecker.makeKing()
        else:
            self.reds -=1
            if delChecker.king == True: 
                self.redKings -= 1
                if fromChecker.king == False: #Regicide - if the counter that has been deleted is a king the new counter becomes one (if not already)
                    self.blackKings += 1
                    fromChecker.makeKing()

    def returnNoCounters(self):
        return self.reds, self.blacks



class Minimax:
    """
    A class to represent the minimax algorithm with alpha beta pruning

    ...
    Attributes
    -----------
    maxsize : int
        represents the highest integer
    minsize : int
        represents the lowest integer
        
    Methods
    -------
    minimaxMain(board, depth, player, alpha, beta)
        This method is used to be the base before the search branches out, it also checks to see if we are at the lowest depth (0) or if there is a win, therfore no more moves can be made
    maxEvaluation(self, board, depth, player, alpha, beta)
        A method that searches for the maximum evaluation of the possible nodes and updates the max evaluation every time. alpha and beta are used to optimise the evaluation
    minEvaluation(self, board, depth, player, alpha, beta)
        A method that searches for the minimum evaluation of the possible nodes and updates the min evaluation  every time. alpha and beta are used to optimise the evaluation
    getChildNone(board, player)
        Gets all the counters on the board that the player owns and simulates each valid move, each valid move is simulated on a board and this method returns them all
    getCounters(board, player)
        Retrieves all the player's counters from the board
    tryMove(board, counter, validMove, deletedCheckers)
        This method simulates the valid move (validMove) on the board and returns the board with the counters new positions on them
    evaluate(board)
        This method is used to evaluate the board parameter, AI is trying to maximise the cost of red-black, where as the human player will want to minimise the cost of black-red
    """
    def __init__(self):
        self.maxsize = sys.maxsize
        self.minsize = -sys.maxsize -1

    def minimaxMain(self, board, depth, player, alpha, beta): # player = True if AI therfore finding the max, player = False if human therefore finding the min
        if depth == 0 or board.checkWinner()!= None: # if we are at the last depth of the tree, if game is won so is at a bottom leaf
            return board, self.evaluate(board) # returns the minimax evaluation and the board with the best move
        if player == True: # if this is an AI player
            return self.maxEvaluation(board, depth, player, alpha, beta)
        else:
            return self.minEvaluation(board, depth, player, alpha, beta)


    def maxEvaluation(self, board, depth, player, alpha, beta):
        bestScore = self.minsize # sets to the smallest integer as this is the lowest max it can be to start with
        bestMove = None
        # for each child of the node
        for child in self.getChildNode(board, player): # for each valid board simulaion, recursively call to
            maxMove, maxEval = self.minimaxMain(child, depth-1, False, alpha, beta) # False as going to Human player
            if maxEval > bestScore: # find the max of best score compared to maxEval
                bestMove = child # best move is updated to child (the board) if evaluation is the best
            if maxEval > alpha: #alpha-beta pruning -  find the max value of alpha compared to the evaluation
                alpha = maxEval
            if alpha >= beta: # stop exploring
                break
        return bestMove, bestScore # return the board and the evaluation
        

    def minEvaluation(self, board, depth, player, alpha, beta):
        bestScore = self.maxsize # sets to the largest integer as this is the highest min it can be to start with
        # for each child of the node
        bestMove = None
        for child in self.getChildNode(board, player):
            minMove, minEval = self.minimaxMain(child, depth-1, True, alpha, beta) #True as going to AI player
            if minEval < bestScore:# find the min of best score compared to minEval
                bestMove = child  #best move is updated to child (the board) if evaluation is the best
            if minEval < beta:
                beta = minEval
            if alpha >= beta: # stop exploring
                break
        return bestMove, bestScore # return the board and the evaluation


    def getChildNode(self, board, player): # get the valid moves for each counter in either list of counters
        validBoards = [] 
        counters = self.getCounters(board, player) # gets all counters the player owns
        for counter in counters: # for each counter of the player we are interested in, we find all valid moves, along with valid hopped moves
            board.validMoves = []
            board.deletedCheckers = []
            validMoves, delCounters = board.checkValidMoves(counter) # get the valid moves along with the counters that might be hopped over
            experimentBoard = None
            for validMove in validMoves: # for each valid move of that checker
                experimentBoard = deepcopy(board) # to save a new board that will not effect the current board that the players are playing on
                experimentCounter = experimentBoard.checkerPresent(counter.pos[0], counter.pos[1]) # get the counter's position on the new board
                newBoard = self.tryMove(experimentBoard, experimentCounter, validMove, delCounters) # try the valid position on a new board
                validBoards.append(newBoard)
        return validBoards
                
    
    def getCounters(self, board, player): #returns all the counters from the player that is on the board
        counters = []
        for row in board.board:
            for space in row:
                if space != None:    
                    if space.colour == "black" and player == False:
                        counters.append(space)
                    elif space.colour == "red" and player == True:
                        counters.append(space)
        return counters
    

    def tryMove(self, board, counter, validMove, deletedCheckers):
        board.movePiece(counter, validMove[0], validMove[1]) # moves the piece on the new board
        for pos, hopped in deletedCheckers: # each hopped over piece is deleted
            if validMove == pos:
                board.delPiece(hopped[0], counter)
        return board


    def evaluate(self, board):
        reds, blacks = board.returnNoCounters()
        return reds - blacks



class Play:
    """
    A class to represent the overall game the players are playing

    ...
    Attributes
    -----------
    currentPlayer : string
        the colour of the current player's counters
    checkersBoard : Board() object
        Used as the board that the players are playing on in this and related class/s
    checkerSelected: Boolean
        To show that a player has already selected a counter throught the GUI
    pickedChecker : None/Counter()
        To show that a sqaure has been clicked on to be moved to
        
    Methods
    -------
    chosen(row, col)
        Allows the user to select a valid counter and move it to a correct place
    move(row, col)
        Returns True if the user's counter can be moved to the selected board place
    changePlayer()
        Changes turns of the players
    updateBoard()
        Used after an AI player takes its turn to set the board equal to the board that they found has the best evaluation on it. The players are then switched.
    """
    def __init__(self):
        self.currentPlayer = "black"
        self.checkersBoard = Board()
        self.checkerSelected = False
        self.pickedChecker = None

    def chosen(self, row, col):
        if self.checkerSelected == False: # if a counter is yet to be selected, identify it with the row and col parameter
            selectedChecker = self.checkersBoard.checkerPresent(row, col)
            if selectedChecker != None and selectedChecker.colour == self.currentPlayer: # if there is the player's counter present
                self.checkerSelected = True # then select this counter
                self.pickedChecker = selectedChecker
                v, d = self.checkersBoard.checkValidMoves(self.pickedChecker) #identify the valid moves
        else: # when a counter has been selected
            if self.move(row, col) == False:  # see if the counter has any valid moves so it can move
                self.checkerSelected = False # if it can't then we reselect our checker by recursively running this method
                self.chosen(row, col)
            else:
                self.changePlayer() # opposition has moved thier piece successfully, so rotate the players


    def move(self, row, col):
        newPos = self.checkersBoard.checkerPresent(row,col)
        if newPos == None and [row,col] in self.checkersBoard.validMoves:
            self.checkersBoard.movePiece(self.pickedChecker, row, col)
            for pos, hopped in self.checkersBoard.deletedCheckers:
                if [row, col] == pos:
                    for hop in hopped:
                        self.checkersBoard.delPiece(hop, self.pickedChecker)
            return True
        return False
            

    def changePlayer(self):
        if self.currentPlayer == "red":
            self.currentPlayer = "black"
        else:
            self.currentPlayer = "red"
        self.checkersBoard.validMoves = []
        self.checkersBoard.deletedCheckers = []
        

    def updateBoard(self, board):
        self.checkersBoard = board # updates the AI board
        self.changePlayer()
            
    

class GUI:
    def __init__(self, hints):
        self.startWindow = pygame.display.set_mode((500,500))
        self.gameDisplay = pygame.display.set_mode((800,800))
        self.bgColour = (255,255,255) # the colour of the side window
        self.sidePos = [0,0,0,0] # the dimentions of the side screen
        self.blackCounter = pygame.image.load('counter1.png')
        self.bKing = pygame.image.load('kingcounter1.png')
        self.redCounter = pygame.image.load('counter2.png')
        self.rKing = pygame.image.load('kingcounter2.png')
        self.counterSize = 90
        self.boardPos = [[(105,5),(305, 5), (505,5), (705,5)],
                        [(5, 105), (205, 105), (405,105), (605,105)],
                        [(105,205),(305, 205), (505,205), (705,205)],
                        [(5, 305), (205, 305), (405,305), (605,305)],
                        [(105,405),(305, 405), (505,405), (705,405)],
                        [(5, 505), (205, 505), (405,505), (605,505)],
                        [(105,605),(305, 605), (505,605), (705,605)],
                        [(5, 705), (205, 705), (405,705), (605,705)]]
        self.boardImg = pygame.image.load('board.png')
        self.boardHeight = 800
        self.boardWidth = 800
        self.hints = hints
        

    def setWindow(self, board):
        pygame.display.set_caption('Checkers') # sets windows title
        pygame.draw.rect(self.gameDisplay, self.bgColour, self.sidePos) # draws the side display window
        self.updateBoard(board)


    def updateBoard(self, board):
        self.gameDisplay.blit(pygame.transform.scale(self.boardImg, (self.boardWidth, self.boardHeight)), (0,0)) # displays the checkers board
        for checker in self.getCounters(board, "black"): # displayes each black counter
            row, col = self.getCounterPos(checker.pos)
            boardPos = self.boardPos[row][col]
            if checker.king == True:
                self.gameDisplay.blit(pygame.transform.scale(self.bKing, (90, 90)), (boardPos[0], boardPos[1]))
            else:
                self.gameDisplay.blit(pygame.transform.scale(self.blackCounter, (90, 90)), (boardPos[0], boardPos[1]))
        for checker in self.getCounters(board, "red"): # displays each red counter
            row, col = self.getCounterPos(checker.pos)
            boardPos = self.boardPos[row][col]
            if checker.king == True:
                self.gameDisplay.blit(pygame.transform.scale(self.rKing, (90, 90)), (boardPos[0], boardPos[1]))
            else:
                self.gameDisplay.blit(pygame.transform.scale(self.redCounter, (90, 90)), (boardPos[0], boardPos[1]))

    def getCounters(self, board, player):
        counters = []
        for row in board.board:
            for space in row:
                if space != None:    
                    if space.colour == "black" and player == "black":
                        counters.append(space)
                    elif space.colour == "red" and player == "red":
                        counters.append(space)
        return counters

    def getCounterPos(self, pos):
        r = pos[0]
        c = int(pos[1]/2)
        return r, c

    def showValidMoves(self, valid):
        for move in valid: # indicate each valid move to the user by green circles
            x = (move[1] *100) +50
            y = (move[0] *100) +50
            pygame.draw.circle(self.gameDisplay, (0,255,0), (x,y), 20)


    def updatePlay(self, board, valid):
        self.updateBoard(board) # updates all the counters on the board
        if self.hints == True:
            self.showValidMoves(valid) # shows all the valid moves on the board
        pygame.display.update() # updates the entire window


    
class Main:
    """
    A class to tie the other classes together and to all for the GUI to be used

    ...
    Attributes
    -----------
    depth: int
        The specified depth given by the user
    gui : object
        So main can interact with the GUI class
    play : object
        So main can interact with the Play class
     minimax: object
         So main can interact with the Minimax class

    Methods
    -------
    main()
        Where the players take turns and where the GUI receives its events from
    """
    def __init__(self, level, hints):
        self.depth = level
        self.gui = GUI(hints)
        self.play = Play()
        self.gui.setWindow(self.play.checkersBoard)
        self.minimax = Minimax()
        self.main()

    def main(self):
        valid = True
        while valid:
            if self.play.checkersBoard.checkWinner() != None:
                print("Welldone", self.play.checkersBoard.checkWinner(), "you have won")
                valid = False

            if self.play.currentPlayer == "red":
                board, evaluation = self.minimax.minimaxMain(self.play.checkersBoard, self.depth, True, -sys.maxsize-1, sys.maxsize)
                time.sleep(1)
                self.play.updateBoard(board)
                self.gui.updateBoard(board)
                pygame.display.update()
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    valid = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    col = int(x/100) # column
                    row = int(y/100) # row
                    self.play.chosen(row,col)
            self.gui.updatePlay(self.play.checkersBoard, self.play.checkersBoard.validMoves)
        pygame.quit()


print("Welcome to Checkers!")
level = int(input("What level would you like to play at? (1-5) 1 is easy, 5 is hardest: "))
hints = input("Would you like the valid moves at that counter to turned on? (yes/no)")
if hints == "yes":
    hints = True
else:
    hints = False
rule = input("Would you like to see the rules before you begin the game? (yes/no)")
if rule == "yes":
    print("Rules")

print("Game starting...")

if __name__ == "__main__":
    Main(level, hints)

