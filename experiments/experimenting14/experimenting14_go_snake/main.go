package experimenting14_go_snake

import "math/rand"

const (
	titleScreen = iota
	inGame      = iota
	loseScreen  = iota
)

const (
	left  = iota
	right = iota
	up    = iota
	down  = iota
)

const BOARD_X = 40
const BOARD_Y = 30

func handleInputs(gameContext struct{}) {
	gameContext
}

type Context struct{}

type Position struct {
	x int
	y int
}

type Size struct {
	w int
	h int
}

type LinkedListNode struct {
	position Position
	next     *LinkedListNode
}

func main() {
	var exit = false
	var gameState = 0
	for !exit {
		switch gameState {
		case titleScreen:
			// titlescreen
		case inGame:
			var gameContext struct {
				boardSize    Size
				snakeList    *LinkedListNode
				appleCell    Position
				playerInputs struct {
					direction int
					space     bool
				}
				playerLost bool
			}
			// setup
			// spawn snake and apple

			gameContext.appleCell = Position{rand.Intn(BOARD_X), rand.Intn(BOARD_Y)}
			var snakePosition = Position{BOARD_X / 2, BOARD_Y / 2}
			for gameContext.SnakeList == gameContext.appleCell {
				applePosition = [2]int{rand.Intn(BOARD_X), rand.Intn(BOARD_Y)}
			}

			// tick
			var lost = false
			for !lost {
				gameContext = handleInputs(gameContext)
				gameContext = updateSnakePosition(gameContext)
				gameContext = checkforWallCollision()
				checkForAppleCollision()

			}
		case loseScreen:
			//
		}
	}
}
