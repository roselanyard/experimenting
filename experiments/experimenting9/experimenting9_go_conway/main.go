package main

import (
	"github.com/veandco/go-sdl2/sdl"
	"image/color"
	"math/rand"
)

const BOARD_X = 150
const BOARD_Y = 100
const BOARD_SCALE_FACTOR = 8
const X_RES = BOARD_X * BOARD_SCALE_FACTOR
const Y_RES = BOARD_Y * BOARD_SCALE_FACTOR

const TARGET_FPS = 15

type boardType [BOARD_Y][BOARD_X]bool

func setupSDLWindowAndRenderer() (*sdl.Window, *sdl.Renderer) {
	// do boilerplate
	window, err := sdl.CreateWindow("conway", sdl.WINDOWPOS_UNDEFINED, sdl.WINDOWPOS_UNDEFINED, X_RES, Y_RES, sdl.WINDOW_SHOWN)
	if err != nil {
		panic(err)
	}
	renderer, err := sdl.CreateRenderer(window, -1, sdl.RENDERER_ACCELERATED)
	if err != nil {
		panic(err)
	}
	return window, renderer
}

func getNeighborsOfCell(row int, col int, array *boardType) int {
	// check all this to make sure the x/y, i/j, row/col is consistent
	var neighborsList = []bool{}
	for i := row - 1; i < row+2; i++ {
		for j := col - 1; j < col+2; j++ {
			if i == row && j == col {
				continue
			}
			if i < 0 || i >= BOARD_Y || j < 0 || j >= BOARD_X {
				continue
			}
			neighborsList = append(neighborsList, (*array)[i][j]) // ai made this, does this just work?
		}
	}
	var count = 0
	for _, val := range neighborsList {
		if val {
			count++
		}
	}
	return count
}

func randomizeCells(factor int, array *boardType, display *sdl.Surface) {
	for i, _ := range array {
		for j, _ := range array[i] {
			array[i][j] = rand.Intn(100)%factor == 0
			if array[i][j] == true {
				display.Set(j, i, color.RGBA{255, 255, 255, 255})
			} else {
				display.Set(j, i, color.RGBA{0, 0, 0, 255})
			}
		}
	}
}

func clearCells(array *boardType, display *sdl.Surface) {
	for i, _ := range array {
		for j, _ := range array[i] {
			array[i][j] = false
			display.Set(j, i, color.RGBA{0, 0, 0, 255})
		}
	}
}

func main() {
	// don't even think about graphics yet
	// setup the board

	gameSurface, err := sdl.CreateRGBSurfaceWithFormat(0, BOARD_X, BOARD_Y, 8, sdl.PIXELFORMAT_RGBA8888)
	if err != nil {
		panic(err)
	}

	var board boardType = [BOARD_Y][BOARD_X]bool{}
	for i, _ := range board {
		for j, _ := range board[i] {
			board[i][j] = rand.Intn(100)%4 == 0
			if board[i][j] == true {
				gameSurface.Set(j, i, color.RGBA{255, 255, 255, 255})
			} else {
				gameSurface.Set(j, i, color.RGBA{0, 0, 0, 255})
			}
		}
	}

	// setup graphics
	// initialize a texture that's the size of BOARD_X x BOARD_Y
	//
	window, renderer := setupSDLWindowAndRenderer()
	defer func() {
		err := window.Destroy()
		if err != nil {
			panic(err)
		}
	}()
	defer func() {
		err := renderer.Destroy()
		if err != nil {
			panic(err)
		}
	}()

	// game loop

	var gameEnding = false
	var playing = false
	for !gameEnding {
		var startTime uint64 = sdl.GetTicks64()
		// check the event loop
		for e := sdl.PollEvent(); e != nil; e = sdl.PollEvent() {
			switch ev := e.(type) {
			case *sdl.QuitEvent:
				_ = ev
				gameEnding = true
			case *sdl.KeyboardEvent:
				if ev.Keysym.Sym == sdl.K_SPACE && ev.State == sdl.PRESSED {
					if playing == false {
						playing = true
					} else {
						playing = false
					}

				}
				if ev.Keysym.Sym == sdl.K_r && ev.State == sdl.PRESSED {
					randomizeCells(4, &board, gameSurface)
				}
				if ev.Keysym.Sym == sdl.K_c && ev.State == sdl.PRESSED {
					clearCells(&board, gameSurface)
				}
				// to check: make sure indexing is consistently [i][j]
			case *sdl.MouseButtonEvent:
				if ev.State == sdl.PRESSED && ev.Button == sdl.BUTTON_LEFT {
					if 0 <= ev.X && ev.X < X_RES && 0 <= ev.Y && ev.Y < Y_RES {
						var xClickPos = ev.X / BOARD_SCALE_FACTOR
						var yClickPos = ev.Y / BOARD_SCALE_FACTOR
						if board[yClickPos][xClickPos] == true { // assured that this is clean
							board[yClickPos][xClickPos] = false
							gameSurface.Set(int(xClickPos), int(yClickPos), color.RGBA{R: 0, G: 0, B: 0, A: 255})
						} else {
							board[yClickPos][xClickPos] = true
							gameSurface.Set(int(xClickPos), int(yClickPos), color.RGBA{R: 255, G: 255, B: 255, A: 255})
						}
					}
				}
			}
		}

		// update the board, with the CPU
		if playing {
			var boardNext = board
			for i, row := range boardNext {
				for j, cell := range row {
					// update each cell based on board
					var neighborCount = getNeighborsOfCell(i, j, &board)
					if cell {
						if neighborCount < 2 {
							boardNext[i][j] = false
							gameSurface.Set(j, i, color.RGBA{R: 0, G: 0, B: 0, A: 255})
						}
						if neighborCount == 2 || neighborCount == 3 {
							boardNext[i][j] = true
							gameSurface.Set(j, i, color.RGBA{R: 255, G: 255, B: 255, A: 255})
						}
						if neighborCount > 3 {
							boardNext[i][j] = false
							gameSurface.Set(j, i, color.RGBA{R: 0, G: 0, B: 0, A: 255})
						}
					} else {
						if neighborCount == 3 {
							boardNext[i][j] = true
							gameSurface.Set(j, i, color.RGBA{R: 255, G: 255, B: 255, A: 255})
						}
					}
				}
			}
			board = boardNext
		}

		// render the board

		// write to the texture, white if on, black if off
		// rescale the texture
		// skip rescale

		// testing the surface
		// gameSurface.FillRect(&sdl.Rect{40, 40, 80, 80}, sdl.MapRGB(gameSurface.Format, 255, 255, 255))

		err = renderer.Clear()
		if err != nil {
			panic(err)
		}
		var renderTexture, err = renderer.CreateTextureFromSurface(gameSurface)
		if err != nil {
			panic(err)
		}

		var srcRect = sdl.Rect{0, 0, BOARD_X, BOARD_Y}
		var destRect = sdl.Rect{0, 0, X_RES, Y_RES}
		err = renderer.Copy(renderTexture, &srcRect, &destRect)
		if err != nil {
			panic(err)
		}
		renderer.Present()
		err = renderTexture.Destroy()
		if err != nil {
			panic(err)
		}
		// time.Sleep(1 * time.Second) // to test it
		// blit the texture onto the main canvas and display
		var endTime = sdl.GetTicks64()
		var oneOverTargetFPS float64 = 1.0 / TARGET_FPS
		var oneOverTargetFPSToMilliseconds = uint64(oneOverTargetFPS * 1000)
		if endTime-startTime < oneOverTargetFPSToMilliseconds {
			sdl.Delay(uint32(oneOverTargetFPSToMilliseconds - (endTime - startTime)))
		}
	}
}
