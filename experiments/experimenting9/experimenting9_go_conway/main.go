package main

import (
	"github.com/veandco/go-sdl2/mix"
	"github.com/veandco/go-sdl2/sdl"
	"github.com/veandco/go-sdl2/ttf"
	"image/color"
	"math"
	"math/rand"
)

const BOARD_X = 150
const BOARD_Y = 100
const BOARD_SCALE_FACTOR = 8
const LOWER_BAR_Y = 100
const UPPER_BAR_Y = 100
const LEFT_BAR_X = 50
const RIGHT_BAR_X = 50
const BOARD_SCALED_X_RES = BOARD_X * BOARD_SCALE_FACTOR
const BOARD_SCALED_Y_RES = BOARD_Y * BOARD_SCALE_FACTOR
const WINDOW_X_RES = BOARD_SCALED_X_RES + LEFT_BAR_X + RIGHT_BAR_X
const WINDOW_Y_RES = BOARD_SCALED_Y_RES + LOWER_BAR_Y + UPPER_BAR_Y

const MIN_BOARD_SCALED_X_RES = 480 // this needs to be reformulated
const MIN_BOARD_SCALED_Y_RES = 640

const TARGET_FPS = 15

const (
	// game loop status codes
	exiting    = iota
	menu       = iota
	game       = iota
	songSelect = iota
	gameConfig = iota
	about      = iota
)

const (
	buttonInactive = iota
	buttonActive   = iota
	buttonClicked  = iota
)

type boardType [BOARD_Y][BOARD_X]bool

type gameContext struct {
	gameBoard   boardType
	gameSurface *sdl.Surface
	renderer    *sdl.Renderer
	font        *ttf.Font
}

func setupSDLWindowAndRenderer() (*sdl.Window, *sdl.Renderer) {
	// do boilerplate
	window, err := sdl.CreateWindow("conway", sdl.WINDOWPOS_UNDEFINED, sdl.WINDOWPOS_UNDEFINED, WINDOW_X_RES, WINDOW_Y_RES, sdl.WINDOW_SHOWN)
	if err != nil {
		panic(err)
	}
	renderer, err := sdl.CreateRenderer(window, -1, sdl.RENDERER_ACCELERATED)
	if err != nil {
		panic(err)
	}
	return window, renderer
}

func doConfigurationSanityChecks() (status bool) {
	if BOARD_SCALED_X_RES < MIN_BOARD_SCALED_X_RES || BOARD_SCALED_Y_RES < MIN_BOARD_SCALED_Y_RES {
		return false
	}
	return true
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

func audioHandleUpdates(ctx *audioContext) {
	mix.VolumeMusic(ctx.volume)
	if ctx.musicPaused && !mix.PausedMusic() {
		mix.PauseMusic()
	}
	if !ctx.musicPaused && mix.PausedMusic() {
		mix.ResumeMusic()
	}
	var currentVolume = mix.VolumeMusic(0)
	mix.VolumeMusic(currentVolume) // this feels like a hack but also so does a lot of this
	if ctx.musicEnabled && currentVolume == 0 {
		mix.VolumeMusic(ctx.volume)
	}
	if !ctx.musicEnabled && currentVolume != 0 {
		mix.VolumeMusic(0)
	}
}

type button struct {
	title       string
	clickAction func()
	rect        sdl.Rect
	state       int
	texture     *sdl.Texture // i could have done this better probably
}

type menuContext struct {
	menuSurface    *sdl.Surface
	menuExiting    bool
	allExiting     bool
	buttonRegistry map[string]button
	renderer       *sdl.Renderer
	menuFont       *ttf.Font
}

type audioContext struct {
	musicPaused  bool
	musicEnabled bool
	volume       int
	music        *mix.Music
}

func (ctx *audioContext) raiseVolume(amt int) {
	if ctx.volume+8 < mix.MAX_VOLUME {
		ctx.volume += 8
	}
}
func (ctx *audioContext) lowerVolume(amt int) {
	if ctx.volume-8 >= 0 {
		ctx.volume -= 8
	}
}

func main() {

	// do sanity checks
	var sanityChecksPass = doConfigurationSanityChecks()
	if !sanityChecksPass {
		panic("Configuration sanity checks failed")
	} // this guarantees our menu is always above some minimum X and Y size

	// setup audio and construct audio context
	err := mix.Init(mix.INIT_OGG)
	if err != nil {
		panic(err)
	}
	var _ *mix.Music
	mix.OpenAudio(mix.DEFAULT_FREQUENCY, mix.DEFAULT_FORMAT, mix.DEFAULT_CHANNELS, mix.DEFAULT_CHUNKSIZE)
	music, err := mix.LoadMUS("C:\\Users\\Alexandra\\PycharmProjects\\game_learning\\assets\\mamizou.ogg")
	if err != nil {
		panic(err)
	}

	var audioContextInstance = audioContext{
		musicPaused:  false,
		musicEnabled: true,
		volume:       mix.MAX_VOLUME,
		music:        music,
	}

	err = music.Play(math.MaxInt)
	if err != nil {
		panic(err)
	}
	audioHandleUpdates(&audioContextInstance)

	// setup the surface, board, and renderer
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

	// setup graphics and construct menu context
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
	err = ttf.Init()
	if err != nil {
		panic(err)
	}
	font, err := ttf.OpenFont("C:\\Users\\Alexandra\\PycharmProjects\\game_learning\\assets\\m6x11.ttf", 36)
	if err != nil {
		panic(err)
	}

	menuSurface, err := sdl.CreateRGBSurfaceWithFormat(0, WINDOW_X_RES, WINDOW_Y_RES, 8, sdl.PIXELFORMAT_RGBA8888)

	var context gameContext = gameContext{gameSurface: gameSurface, gameBoard: board, renderer: renderer, font: font}
	var mainMenuContext menuContext = menuContext{
		menuSurface:    menuSurface,
		buttonRegistry: make(map[string]button),
		menuExiting:    false,
		renderer:       renderer,
		menuFont:       font,
	}
	// buttons passed to the menu loop and the draw loop without a click action function
	mainMenuContext.buttonRegistry["enter"] = button{
		title:       "enter >:3",
		clickAction: nil,
		rect: sdl.Rect{
			X: (WINDOW_X_RES / 2) - 100, Y: (WINDOW_Y_RES / 2) - 25, W: 200, H: 50, // check that this is the right constant
		},
		state: buttonInactive,
	}
	mainMenuContext.buttonRegistry["exit"] = button{
		title:       "exit game",
		clickAction: nil,
		rect: sdl.Rect{
			X: (WINDOW_X_RES / 2) - 100, Y: ((WINDOW_Y_RES / 2) - 25) + 75, W: 200, H: 50,
		},
		state: buttonInactive,
	}
	mainMenuContext.buttonRegistry["toggle sound"] = button{
		title:       "toggle sound ^_^",
		clickAction: nil,
		rect: sdl.Rect{
			X: (WINDOW_X_RES / 2) - 100, Y: ((WINDOW_Y_RES / 2) - 25) - 75, W: 200, H: 50,
		},
		state: buttonInactive,
	}

	// setup the main loop, composed of alternating between other loops based on the exit codes (finite state machine?)
	var gameExiting = false
	var inMenu = true
	for !gameExiting {
		if !inMenu {
			var status = gameLoop(&context, &audioContextInstance)
			if status == exiting {
				gameExiting = true
				break
			}
			if status == menu {
				inMenu = true
			}
		}
		var menuExitStatus = menuLoop(&mainMenuContext, &audioContextInstance)
		if menuExitStatus == game {
			inMenu = false
		}
		if menuExitStatus == exiting {
			gameExiting = true
			break
		}
	}
}

func menuLoop(context *menuContext, audioCtx *audioContext) int {

	// this defeats the purpose of the thing i was trying to do. this is an architecture issue i think
	// set the functions that each button will have during the loop (does this make sense?)

	var localScopeButtonToFunctionRegistry = make(map[string]func())
	localScopeButtonToFunctionRegistry["enter"] = func() {
		context.menuExiting = true
	}
	localScopeButtonToFunctionRegistry["exit"] = func() {
		context.allExiting = true
	}
	localScopeButtonToFunctionRegistry["toggle sound"] = func() {
		if audioCtx.musicPaused {
			audioCtx.musicPaused = false
			audioHandleUpdates(audioCtx)
		} else {
			audioCtx.musicPaused = true
			audioHandleUpdates(audioCtx)
		}
	}

	var mousePosition = sdl.Rect{
		X: 0,
		Y: 0,
	}

	// menu loop
	for !context.menuExiting && !context.allExiting {
		// for capping fps
		var startTime = sdl.GetTicks64()

		var mousePositionHasUpdate = false
		var mouseClickHasUpdate = false

		// reset clicked buttons every loop iteration since they get processed always
		for id, b := range context.buttonRegistry {
			if b.state == buttonClicked {
				b.state = buttonActive
				context.buttonRegistry[id] = b
			}
		}

		// check for input and act on it
		for e := sdl.PollEvent(); e != nil; e = sdl.PollEvent() {
			switch t := e.(type) {
			case *sdl.QuitEvent:
				return exiting
			case *sdl.KeyboardEvent:
				switch t.Keysym.Sym {
				case sdl.K_m:
					if t.State == sdl.PRESSED {
						return game
					}
				case sdl.K_o:
					{
						if audioCtx.volume <= mix.MAX_VOLUME-8 {
							audioCtx.volume = audioCtx.volume + 8
						}
						audioHandleUpdates(audioCtx)
					}
				case sdl.K_i:
					{
						if audioCtx.volume >= 8 {
							audioCtx.volume = audioCtx.volume - 8
						}
						audioHandleUpdates(audioCtx)
					}
				}

			case *sdl.MouseMotionEvent:
				mousePositionHasUpdate = true
				mousePosition = sdl.Rect{
					X: e.(*sdl.MouseMotionEvent).X,
					Y: e.(*sdl.MouseMotionEvent).Y,
				}
			case *sdl.MouseButtonEvent:
				if e.(*sdl.MouseButtonEvent).Button == sdl.BUTTON_LEFT && e.(*sdl.MouseButtonEvent).State == sdl.PRESSED {
					mouseClickHasUpdate = true
				}
			}
		}

		// update the buttons based on mouse position and state (does this make sense?)
		if mousePositionHasUpdate {
			for id, b := range context.buttonRegistry {
				if mousePosition.X > b.rect.X && mousePosition.X < b.rect.X+b.rect.W &&
					mousePosition.Y > b.rect.Y && mousePosition.Y < b.rect.Y+b.rect.H {
					b.state = buttonActive // not assuming that buttons can't overlap
					context.buttonRegistry[id] = b
				} else {
					b.state = buttonInactive
					context.buttonRegistry[id] = b
				}
			}

			mousePositionHasUpdate = false
		}

		if mouseClickHasUpdate {
			for id, b := range context.buttonRegistry {
				if mousePosition.X > b.rect.X && mousePosition.X < b.rect.X+b.rect.W &&
					mousePosition.Y > b.rect.Y && mousePosition.Y < b.rect.Y+b.rect.H {
					b.state = buttonClicked // this overrides buttonActive, sanity check performed also for good measure
					context.buttonRegistry[id] = b
				} else {
					b.state = buttonInactive
					context.buttonRegistry[id] = b
				}
			}
		}
		mouseClickHasUpdate = false

		// based on button states (from click/hover), run their functions and set them to active if they're clicked
		for id, b := range context.buttonRegistry {
			if b.state == buttonClicked {
				val, ok := localScopeButtonToFunctionRegistry[id]
				if !ok {
					panic("err: attempted to fun button onclick function without assigning one first")
				}
				val()
				b.state = buttonActive // this is such a hack and not how i intended to use these
			}
		}

		// display the menu
		// this might be too expensive (?)

		var menuSurfaceRect = sdl.Rect{
			X: 0,
			Y: 0,
			W: context.menuSurface.W,
			H: context.menuSurface.H,
		}
		var windowRect = sdl.Rect{
			X: 0,
			Y: 0,
			W: WINDOW_X_RES,
			H: WINDOW_Y_RES,
		}

		// start to draw the menu
		// clear the screen - is this even necessary?

		err := context.renderer.SetDrawColor(0, 0, 0, 255)
		if err != nil {
			panic(err)
		}
		err = context.renderer.FillRect(&windowRect)
		if err != nil {
			panic(err)
		}
		err = context.renderer.SetDrawColor(255, 255, 255, 255)
		if err != nil {
			panic(err)
		}

		// create the texture for the menu on which to draw the buttons
		menuTexture, err := context.renderer.CreateTexture(sdl.PIXELFORMAT_RGBA8888, sdl.TEXTUREACCESS_TARGET, WINDOW_X_RES, WINDOW_Y_RES)

		var defaultRenderTarget = context.renderer.GetRenderTarget()
		err = context.renderer.SetRenderTarget(menuTexture)
		if err != nil {
			panic(err)
		}
		err = context.renderer.SetDrawColor(0, 0, 0, 255)
		if err != nil {
			panic(err)
		}
		err = context.renderer.Clear()
		if err != nil {
			panic(err)
		}

		// display title
		var titleTextSurface *sdl.Surface
		titleTextSurface, err = context.menuFont.RenderUTF8Solid("conway's gawme ov wife uncentered edition", sdl.Color{R: 255, G: 128, B: 128, A: 255})
		var titleTextSurfaceSourceRect = sdl.Rect{
			W: titleTextSurface.W,
			H: titleTextSurface.H,
		}
		var titleTextSurfaceDestRect = sdl.Rect{
			X: (WINDOW_X_RES / 2) - 100,
			Y: (WINDOW_Y_RES / 2) - 150,
			W: titleTextSurface.W,
			H: titleTextSurface.H,
		}
		titleTextSurfaceTexture, err := context.renderer.CreateTextureFromSurface(titleTextSurface)
		err = context.renderer.Copy(titleTextSurfaceTexture, &titleTextSurfaceSourceRect, &titleTextSurfaceDestRect)
		if err != nil {
			panic(err)
		}
		err = titleTextSurfaceTexture.Destroy()
		if err != nil {
			panic(err)
		}

		// display all the buttons
		for _, b := range context.buttonRegistry {
			if b.state == buttonActive { // there's a hack i could do here but i'm not going to
				err = context.renderer.SetDrawColor(128, 128, 255, 255)
			} else if b.state == buttonClicked {
				err = context.renderer.SetDrawColor(0, 0, 255, 255)
			} else {
				err = context.renderer.SetDrawColor(255, 255, 255, 255)
			}
			if err != nil {
				panic(err)
			}
			err = context.renderer.FillRect(&b.rect) // has no impact on the program
			if err != nil {
				panic(err)
			}
			// not checking for size in bounds yet
			var textSurface *sdl.Surface
			textSurface, err = context.menuFont.RenderUTF8Solid(b.title, sdl.Color(color.RGBA{A: 255}))
			if err != nil {
				panic(err)
			}
			var textSurfaceRect = sdl.Rect{
				X: b.rect.X,
				Y: b.rect.Y,
				W: textSurface.W,
				H: textSurface.H,
			}
			var textTexture, err = context.renderer.CreateTextureFromSurface(textSurface)
			if err != nil {
				panic(err)
			}
			var textSurfaceSourceRect = sdl.Rect{
				X: 0,
				Y: 0,
				W: textSurface.W,
				H: textSurface.H,
			}
			err = context.renderer.Copy(textTexture, &textSurfaceSourceRect, &textSurfaceRect) // fix naming
			if err != nil {
				panic(err)
			}
			textSurface.Free()
			err = textTexture.Destroy()
			if err != nil {
				panic(err)
			}
		}

		// copy everything onto the render surface and clean up
		err = context.renderer.SetRenderTarget(defaultRenderTarget)
		if err != nil {
			panic(err)
		}

		err = context.renderer.Copy(menuTexture, &menuSurfaceRect, &windowRect)
		if err != nil {
			panic(err)
		}
		context.renderer.Present()
		err = menuTexture.Destroy()
		if err != nil {
			panic(err)
		}

		// cap menu fps

		var endTime = sdl.GetTicks64()
		var oneOverTargetFPS float64 = 1.0 / TARGET_FPS
		var oneOverTargetFPSToMilliseconds = uint64(oneOverTargetFPS * 1000)
		if endTime-startTime < oneOverTargetFPSToMilliseconds {
			sdl.Delay(uint32(oneOverTargetFPSToMilliseconds - (endTime - startTime)))
		}

	}
	// exit to appropriate place based on state
	context.menuExiting = false
	if !context.allExiting {
		return game
	} else {
		return exiting
	}
}

func gameLoop(context *gameContext, audioCtx *audioContext) (status int) {

	// game loop

	var gameEnding = false
	var playing = false
	var buttonRegistry = []button{
		{
			title: "clear (c)",
			clickAction: func() {
				clearCells(&context.gameBoard, context.gameSurface)
			},
			rect: sdl.Rect{
				X: 0,
				Y: 0,
				W: 200,
				H: 50,
			},
			state: buttonInactive,
		},
		{
			title: "randomize (r)",
			clickAction: func() {
				randomizeCells(4, &context.gameBoard, context.gameSurface)
			},
			rect: sdl.Rect{
				X: 300,
				Y: 0,
				W: 200,
				H: 50,
			},
			state: buttonInactive,
		},
		{
			title: "play/pause (space)",
			clickAction: func() {
				if playing == false {
					playing = true
				} else {
					playing = false
				}
			},
			rect: sdl.Rect{
				X: 600,
				Y: 0,
				W: 200,
				H: 50,
			},
			state: buttonInactive, // defaults to inactive
		},
	}
	for !gameEnding {
		var startTime uint64 = sdl.GetTicks64()

		// reset all the buttons
		for id, b := range buttonRegistry {
			if b.state == buttonClicked {
				b.state = buttonActive
				buttonRegistry[id] = b
			}
		}

		// check the event loop and act based on what event occurred
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
				if ev.Keysym.Sym == sdl.K_m && ev.State == sdl.PRESSED {
					return menu
				}
				if ev.Keysym.Sym == sdl.K_r && ev.State == sdl.PRESSED {
					randomizeCells(4, &context.gameBoard, context.gameSurface)
				}
				if ev.Keysym.Sym == sdl.K_c && ev.State == sdl.PRESSED {
					clearCells(&context.gameBoard, context.gameSurface)
				}
				if ev.Keysym.Sym == sdl.K_i && ev.State == sdl.PRESSED {
					audioCtx.lowerVolume(8)
					audioHandleUpdates(audioCtx)
				}
				if ev.Keysym.Sym == sdl.K_o && ev.State == sdl.PRESSED {
					audioCtx.raiseVolume(8)
					audioHandleUpdates(audioCtx)
				}
				// to check: make sure indexing is consistently [i][j]
			case *sdl.MouseButtonEvent:
				if ev.State == sdl.PRESSED && ev.Button == sdl.BUTTON_LEFT { // check this
					if LEFT_BAR_X <= ev.X && ev.X < BOARD_SCALED_X_RES+LEFT_BAR_X && LOWER_BAR_Y <= ev.Y && ev.Y < LOWER_BAR_Y+BOARD_SCALED_Y_RES {
						var xClickPos = (ev.X - LEFT_BAR_X) / BOARD_SCALE_FACTOR
						var yClickPos = (ev.Y - LOWER_BAR_Y) / BOARD_SCALE_FACTOR
						if context.gameBoard[yClickPos][xClickPos] == true { // assured that this is clean
							context.gameBoard[yClickPos][xClickPos] = false
							context.gameSurface.Set(int(xClickPos), int(yClickPos), color.RGBA{R: 0, G: 0, B: 0, A: 255})
						} else {
							context.gameBoard[yClickPos][xClickPos] = true
							context.gameSurface.Set(int(xClickPos), int(yClickPos), color.RGBA{R: 255, G: 255, B: 255, A: 255})
						}
					}
					for id, b := range buttonRegistry {
						if b.rect.X < ev.X && ev.X < b.rect.X+b.rect.W &&
							b.rect.Y < ev.Y && ev.Y < b.rect.Y+b.rect.H {
							if ev.State == sdl.PRESSED && ev.Button == sdl.BUTTON_LEFT {
								b.state = buttonClicked
								buttonRegistry[id] = b
							} else {
								b.state = buttonActive
								buttonRegistry[id] = b
							}
						}
					}
				}
			case *sdl.MouseMotionEvent:
				for id, b := range buttonRegistry {
					if b.rect.X < ev.X && ev.X < b.rect.X+b.rect.W &&
						b.rect.Y < ev.Y && ev.Y < b.rect.Y+b.rect.H {
						b.state = buttonActive // this is probably introducing a bug
						buttonRegistry[id] = b
					} else {
						b.state = buttonInactive
						buttonRegistry[id] = b
					}
				}
			}
		}

		// handle clicks
		for id, b := range buttonRegistry {
			if b.state == buttonClicked {
				var val = b.clickAction
				val()
				// reset button state
				b.state = buttonActive
				buttonRegistry[id] = b
			}
		}

		// update the board, with the CPU
		if playing {
			var boardNext = context.gameBoard
			for i, row := range boardNext {
				for j, cell := range row {
					// update each cell based on board
					var neighborCount = getNeighborsOfCell(i, j, &context.gameBoard)
					if cell {
						if neighborCount < 2 {
							// note that the board and the game surface are being updated separately
							boardNext[i][j] = false
							context.gameSurface.Set(j, i, color.RGBA{R: 0, G: 0, B: 0, A: 255})
						}
						if neighborCount == 2 || neighborCount == 3 {
							boardNext[i][j] = true
							context.gameSurface.Set(j, i, color.RGBA{R: 255, G: 255, B: 255, A: 255})
						}
						if neighborCount > 3 {
							boardNext[i][j] = false
							context.gameSurface.Set(j, i, color.RGBA{R: 0, G: 0, B: 0, A: 255})
						}
					} else {
						if neighborCount == 3 {
							boardNext[i][j] = true
							context.gameSurface.Set(j, i, color.RGBA{R: 255, G: 255, B: 255, A: 255})
						}
					}
				}
			}
			context.gameBoard = boardNext
		}

		// render the board
		context.renderer.SetDrawColor(0, 0, 0, 255)
		err := context.renderer.Clear()
		if err != nil {
			panic(err)
		}
		// draw buttons
		for _, b := range buttonRegistry {
			if b.state == buttonClicked {
				context.renderer.SetDrawColor(0, 0, 255, 255)
			}
			if b.state == buttonActive {
				context.renderer.SetDrawColor(128, 128, 255, 255)
			}
			if b.state == buttonInactive {
				context.renderer.SetDrawColor(192, 192, 255, 255)
			}
			var drawRect = sdl.Rect{
				X: b.rect.X, Y: b.rect.Y, W: b.rect.W, H: b.rect.H,
			}
			context.renderer.FillRect(&drawRect)
			var buttonTextSurface, err = context.font.RenderUTF8Solid(b.title, sdl.Color{255, 255, 255, 255})
			if err != nil {
				panic(err)
			}
			var buttonTextSourceRect = sdl.Rect{
				W: buttonTextSurface.W,
				H: buttonTextSurface.H,
			}
			var buttonTextDestRect = sdl.Rect{
				X: b.rect.X,
				Y: b.rect.Y,
				W: buttonTextSurface.W,
				H: buttonTextSurface.H,
			}

			var buttonTextTexture *sdl.Texture
			buttonTextTexture, err = context.renderer.CreateTextureFromSurface(buttonTextSurface)
			if err != nil {
				panic(err)
			}
			context.renderer.Copy(buttonTextTexture, &buttonTextSourceRect, &buttonTextDestRect)

			buttonTextTexture.Destroy()
			buttonTextSurface.Free()
		}

		renderTexture, err := context.renderer.CreateTextureFromSurface(context.gameSurface)
		if err != nil {
			panic(err)
		}
		// present everything and clean up
		// rescale based on the scale factor (there is probably a cleaner way of doing this)
		var srcRect = sdl.Rect{0, 0, BOARD_X, BOARD_Y}
		var destRect = sdl.Rect{0 + LEFT_BAR_X, 0 + LOWER_BAR_Y, BOARD_SCALED_X_RES, BOARD_SCALED_Y_RES}
		err = context.renderer.Copy(renderTexture, &srcRect, &destRect)
		if err != nil {
			panic(err)
		}
		context.renderer.Present()
		err = renderTexture.Destroy()
		if err != nil {
			panic(err)
		}

		// throttle the FPS
		var endTime = sdl.GetTicks64()
		var oneOverTargetFPS float64 = 1.0 / TARGET_FPS
		var oneOverTargetFPSToMilliseconds = uint64(oneOverTargetFPS * 1000)
		if endTime-startTime < oneOverTargetFPSToMilliseconds {
			sdl.Delay(uint32(oneOverTargetFPSToMilliseconds - (endTime - startTime)))
		}
	}
	// exit status 0 (closing)
	return exiting
}
