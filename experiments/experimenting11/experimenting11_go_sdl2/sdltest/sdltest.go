package sdltest

import (
	"experimenting11_go_sdl2/data"
	"fmt"
	"github.com/veandco/go-sdl2/img"
	"github.com/veandco/go-sdl2/sdl"
	"log"
	"os"
)

var xRes int32 = 640
var yRes int32 = 480
var imgPath = "C:\\Users\\Alexandra\\PycharmProjects\\game_learning\\assets\\piano\\note.png"

func gameInit() (window *sdl.Window, renderer *sdl.Renderer, err error) {
	var initFlags uint32 = sdl.INIT_EVERYTHING
	if err := sdl.Init(initFlags); err != nil {
		panic(err)
	}

	var windowPosUndefined int32 = sdl.WINDOWPOS_UNDEFINED

	window, err = sdl.CreateWindow("test", windowPosUndefined, windowPosUndefined, xRes, yRes, sdl.WINDOW_SHOWN)
	if err != nil {
		log.Fatal("Error initializing SDL2 window")
		return nil, nil, err
	}

	err = img.Init(img.InitFlags(img.INIT_PNG))
	if err != nil {
		log.Fatal("Failed to initialize SDL2 IMG extension")
		return nil, nil, err
	}

	renderer, err = sdl.CreateRenderer(window, -1, sdl.RENDERER_ACCELERATED)
	if err != nil {
		log.Fatal("Error initializing SDL2 renderer")
		return nil, nil, err
	}
	return window, renderer, nil
}

func SDLTest() {

	message := data.Data()
	fmt.Printf("%v", message)

	window, renderer, err := gameInit()
	defer sdl.Quit()
	defer func(window *sdl.Window) {
		err := window.Destroy()
		if err != nil {
			log.Println("Failed to destroy SDL2 Window")
		}
	}(window)

	imgTexture, err := img.LoadTexture(renderer, imgPath)
	if err != nil {
		log.Fatal("Error loading texture")
	}

	_, _, w, h, err := imgTexture.Query()
	if err != nil {
		log.Fatal("Error querying texture properties")
	}
	var imgTextureRect = sdl.Rect{
		X: 0,
		Y: 0,
		W: w,
		H: h,
	}

	var displayRect = sdl.Rect{X: 0, Y: 0, W: 640, H: 480}
	displayRectDownsampleByFour := sdl.Rect{
		X: 0,
		Y: 0,
		W: displayRect.W / 4,
		H: displayRect.H / 4,
	}

	var ticks uint32 = 1000 / 60
	var position = [2]int32{0, 0}
	var minPos [2]int32 = [2]int32{0, 0}
	var maxPos [2]int32 = [2]int32{int32(displayRectDownsampleByFour.W) - int32(imgTextureRect.W), int32(displayRectDownsampleByFour.H) - int32(imgTextureRect.H)}

	for {
		// handle events
		for event := sdl.PollEvent(); event != nil; event = sdl.PollEvent() {
			switch e := event.(type) {
			case sdl.QuitEvent:
				os.Exit(0)
			case sdl.KeyboardEvent:
				switch e.Keysym.Sym {
				case sdl.K_d:
					if position[0]+5 < maxPos[0] {
						position[0] += 5
					}
				case sdl.K_a:
					if position[0]-5 > minPos[0] {
						position[0] -= 5
					}
				case sdl.K_s:
					if position[1]+5 < maxPos[1] {
						position[1] += 5
					}
				case sdl.K_w:
					if position[1]-5 > minPos[1] {
						position[1] -= 5
					}
				}
			}
		}

		// prepare to render
		imgTextureRectTranspose := sdl.Rect{
			X: 0 + position[0],
			Y: 0 + position[1],
			W: imgTextureRect.W,
			H: imgTextureRect.H,
		}

		// render to small version
		pixelRenderTarget, err := renderer.CreateTexture(sdl.PIXELFORMAT_RGBA8888, sdl.TEXTUREACCESS_TARGET, displayRectDownsampleByFour.W, displayRectDownsampleByFour.H)
		if err != nil {
			log.Fatal("Error creating PixelRenderTarget")
		}
		err = renderer.SetRenderTarget(pixelRenderTarget)
		if err != nil {
			log.Fatal("Error setting renderer target")
		}
		err = renderer.SetDrawColor(255, 255, 255, 0)
		if err != nil {
			log.Fatal("Error setting draw color")
		}
		err = renderer.FillRect(&displayRectDownsampleByFour)
		if err != nil {
			log.Fatal("Error filling displayRect")
		}
		err = renderer.Copy(imgTexture, &imgTextureRect, &imgTextureRectTranspose)
		if err != nil {
			log.Fatal("Error copying texture")
		}
		err = renderer.SetRenderTarget(nil)
		if err != nil {
			log.Fatal("Error setting renderer target back to window")
		}

		// resize to full screen
		err = renderer.Copy(pixelRenderTarget, &displayRectDownsampleByFour, &displayRect)
		renderer.Present()
		sdl.Delay(ticks)
	}

}
