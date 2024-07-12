package main

import (
	"github.com/veandco/go-sdl2/sdl"
	"math"
	"os"
)

var mapX int32 = 8
var mapY int32 = 8
var mapS int32 = 64
var windowRect = sdl.Rect{X: 0, Y: 0, W: mapX * mapS, H: mapY * mapS}
var raycasterMap = [][]int32{
	{1, 1, 1, 1, 1, 1, 1, 1},
	{1, 0, 0, 0, 0, 0, 0, 1},
	{1, 0, 0, 0, 0, 1, 0, 1},
	{1, 0, 0, 1, 0, 0, 0, 1},
	{1, 0, 0, 0, 0, 0, 0, 1},
	{1, 0, 1, 0, 0, 0, 0, 1},
	{1, 0, 0, 0, 0, 0, 0, 1},
	{1, 1, 1, 1, 1, 1, 1, 1},
}

var playerPosition = []int32{mapS * 5, mapS * 5}
var playerVelocity = 0.0
var playerSize = 6
var playerRaySize = 20
var playerAngle = 0.0
var playerAngularVelocity = 0.0

func initRaycaster() (*sdl.Window, *sdl.Renderer, error) {
	var sdlInitFlags uint32 = sdl.INIT_EVERYTHING
	var err = sdl.Init(sdlInitFlags)
	if err != nil {
		panic(err)
	}
	window, err := sdl.CreateWindow("testing window 3D", sdl.WINDOWPOS_UNDEFINED, sdl.WINDOWPOS_UNDEFINED, windowRect.W, windowRect.H, sdl.WINDOW_SHOWN)
	if err != nil {
		panic(err)
	}
	renderer, err := sdl.CreateRenderer(window, -1, sdl.RENDERER_ACCELERATED)
	if err != nil {
		panic(err)
	}
	return window, renderer, err
}

func drawMap2D(renderer *sdl.Renderer) {
	// double for loop
	var err = renderer.SetDrawColor(255, 255, 255, 0)
	if err != nil {
		panic(err)
	}
	for x := range raycasterMap {
		for y := range raycasterMap[x] {
			if raycasterMap[x][y] == 1 {
				var rect = sdl.Rect{
					X: (int32(x) * mapS) + 1,
					Y: (int32(y) * mapS) + 1,
					W: mapS - 1,
					H: mapS - 1,
				}
				var err = renderer.FillRect(&rect)
				if err != nil {
					panic(err)
				}
			}
		}
	}
}

func drawPlayer(renderer *sdl.Renderer) {
	var err = renderer.SetDrawColor(255, 255, 0, 0)
	if err != nil {
		panic(err)
	}
	var playerRect = sdl.Rect{
		X: playerPosition[0] - int32(playerSize/2),
		Y: playerPosition[1] - int32(playerSize/2),
		W: int32(playerSize),
		H: int32(playerSize),
	}
	err = renderer.FillRect(&playerRect)
	if err != nil {
		panic(err)
	}
	var x1, y1 = playerPosition[0], playerPosition[1]
	var x2, y2 = x1 + int32(float64(playerRaySize)*math.Cos(float64(playerAngle))), y1 + int32(float64(playerRaySize)*math.Sin(float64(playerAngle)))
	err = renderer.DrawLine(x1, y1, x2, y2) // player ray
	if err != nil {
		panic(err)
	}

}

func drawRays3D(renderer *sdl.Renderer) {
	var rayCount, mx, my, dof int32
	var rayX, rayY, rayAngle, xOffset, yOffset float64
	var horizontalX, horizontalY float64
	var verticalX, verticalY float64
	var oneDegreeInRadians = 0.01745329 // magic number
	//rayAngle = playerAngle
	rayAngle = playerAngle - oneDegreeInRadians*30
	if rayAngle < 0 {
		rayAngle += 2 * math.Pi
	}
	if rayAngle > 2*math.Pi {
		rayAngle -= 2 * math.Pi
	}

	renderer.SetDrawColor(0, 255, 0, 0)
	for rayCount = 0; rayCount < 60; rayCount++ {
		// check horizontal lines
		dof = 0
		xOffset = 0
		yOffset = 0
		var aTan = -1 / math.Tan(rayAngle)
		if rayAngle > math.Pi {
			horizontalY = float64(((playerPosition[1] >> 6) << 6)) - 0.0001
			horizontalX = (float64(playerPosition[1])-horizontalY)*(aTan) + float64(playerPosition[0])
			yOffset = -64
			xOffset = -yOffset * (aTan)
		}
		if rayAngle < math.Pi && rayAngle != 0 {
			horizontalY = float64(((playerPosition[1] >> 6) << 6) + 64)
			horizontalX = (float64(playerPosition[1])-horizontalY)*(aTan) + float64(playerPosition[0])
			yOffset = 64
			xOffset = -yOffset * (aTan)
		}
		if rayAngle == 0 || rayAngle == math.Pi {
			horizontalX = float64(playerPosition[0])
			horizontalY = float64(playerPosition[1])
			dof = 8
		}

		for dof < 8 {
			mx = (int32)(horizontalX) >> 6
			my = (int32)(horizontalY) >> 6
			if 0 <= mx && mx < mapX && 0 <= my && my < mapY {
				if raycasterMap[mx][my] == 1 {
					dof = 8
				} else {
					horizontalX += xOffset
					horizontalY += yOffset
					dof += 1
				}
			} else {
				dof = 8
			}
		}
		// check vertical lines
		dof = 0
		xOffset = 0
		yOffset = 0
		var nTan = -math.Tan(rayAngle)
		var piOverTwo = math.Pi / 2
		var threePiOverTwo = 3 * math.Pi / 2
		if rayAngle > piOverTwo && rayAngle < threePiOverTwo {
			verticalX = float64(((playerPosition[0] >> 6) << 6)) - 0.0001
			verticalY = (float64(playerPosition[0])-verticalX)*nTan + float64(playerPosition[1])
			xOffset = -64
			yOffset = -xOffset * nTan
		} else if rayAngle == threePiOverTwo || rayAngle == piOverTwo {
			verticalY = float64(playerPosition[1])
			verticalX = float64(playerPosition[0])
			dof = 8
		} else if rayAngle < piOverTwo || rayAngle > threePiOverTwo {
			verticalX = float64(((playerPosition[0] >> 6) << 6) + 64)
			verticalY = (float64(playerPosition[0])-verticalX)*nTan + float64(playerPosition[1])
			xOffset = 64
			yOffset = -xOffset * nTan
		}
		for dof < 8 {
			my = (int32)(verticalY) >> 6
			mx = (int32)(verticalX) >> 6
			if 0 <= mx && mx < mapX && 0 <= my && my < mapY {
				if raycasterMap[mx][my] == 1 {
					dof = 8
				} else {
					verticalY += yOffset
					verticalX += xOffset
					dof += 1
				}
			} else {
				dof = 8
			}
		}
		var distanceHorizontal = getLineDistance(playerPosition[0], playerPosition[1], int32(horizontalX), int32(horizontalY))
		var distanceVertical = getLineDistance(playerPosition[0], playerPosition[1], int32(verticalX), int32(verticalY))
		if distanceVertical > distanceHorizontal {
			rayX, rayY = horizontalX, horizontalY
		} else {
			rayX, rayY = verticalX, verticalY
		}
		math.Cos(rayX) // noop
		math.Sin(rayY)
		if horizontalX > math.MaxUint-1 {
			horizontalX = 1
		}
		//renderer.DrawLine(playerPosition[0], playerPosition[1], int32(rayX), int32(rayY))
		//renderer.DrawLine(playerPosition[0], playerPosition[1], int32(verticalX), int32(verticalY))
		renderer.DrawLine(playerPosition[0], playerPosition[1], int32(horizontalX), int32(horizontalY))
		//renderer.Present()
		rayAngle += oneDegreeInRadians
		if rayAngle >= 2*math.Pi {
			rayAngle -= 2 * math.Pi
		}
	}

}

func getLineDistance(x1, y1, x2, y2 int32) float64 {
	return math.Sqrt(math.Pow(float64(x2-x1), 2) + math.Pow(float64(y2-y1), 2))
}

func handleKeys(event sdl.KeyboardEvent) {
	switch event.State {
	case sdl.PRESSED:
		switch event.Keysym.Sym {
		case sdl.K_w:
			playerVelocity = 5
		case sdl.K_s:
			playerVelocity = -5
		case sdl.K_d:
			playerAngularVelocity = 0.2
		case sdl.K_a:
			playerAngularVelocity = -0.2
		}
	case sdl.RELEASED:
		switch event.Keysym.Sym {
		case sdl.K_w:
			playerVelocity = 0
		case sdl.K_s:
			playerVelocity = 0
		case sdl.K_a:
			playerAngularVelocity = 0
		case sdl.K_d:
			playerAngularVelocity = 0
		}
	}
}

func drawBlank(renderer *sdl.Renderer) {
	err := renderer.SetDrawColor(0, 0, 0, 0)
	if err != nil {
		panic(err)
	}
	err = renderer.FillRect(&windowRect)
	if err != nil {
		panic(err)
	}
}

func handleKeyEvents() {
	sdl.PumpEvents()
	for event := sdl.PollEvent(); event != nil; event = sdl.PollEvent() {
		switch event.(type) {
		case sdl.QuitEvent:
			os.Exit(0)
		case sdl.KeyboardEvent:
			handleKeys(event.(sdl.KeyboardEvent))
		}
	}
}
func tick() {
	playerPosition[0] += int32(math.Cos(playerAngle) * float64(playerVelocity))
	playerPosition[1] += int32(math.Sin(playerAngle) * float64(playerVelocity))
	playerAngle = (math.Mod((float64(playerAngle) + playerAngularVelocity), (2 * math.Pi)))
	if playerAngle < 0 {
		playerAngle += 2 * math.Pi
	}
	if playerAngle > 2*math.Pi {
		playerAngle -= 2 * math.Pi
	}
}

func main() {
	// using a model-view-controller architecture
	var window, renderer, err = initRaycaster()
	if err != nil {
		panic(err)
	}
	defer func() {
		err = window.Destroy()
		err = renderer.Destroy()
		if err != nil {
			panic(err)
		}
	}()
	for {
		handleKeyEvents()
		tick()
		drawBlank(renderer)
		drawMap2D(renderer)
		drawPlayer(renderer)
		drawRays3D(renderer)
		renderer.Present()
		sdl.Delay(50)
	}
}
