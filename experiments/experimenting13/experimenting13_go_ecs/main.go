package experimenting13_go_ecs

import (
	"fmt"
	"github.com/bits-and-blooms/bitset"
	"github.com/veandco/go-sdl2/sdl"
	"time"
)
import "github.com/veandco/go-sdl2/img"

// constants for SDL
const WINDOW_H = 640
const WINDOW_W = 480

func main() {

	// example component

	type Transform struct {
		position [3]float64
		rotation [4]float64
		scale    [3]float64
	}

	// typedefs for ecs
	type Entity uint32
	type ComponentType uint8
	type Signature bitset.BitSet

	// constants for ECS
	const MAX_ENTITIES Entity = 5000

	/* var EntityRegistry struct {
		var signatureToEntities = make(map[Signature]Entity)
	}

	func */

	// boilerplate for SDL
	err := sdl.Init(sdl.INIT_EVERYTHING)
	if err != nil {
		panic(err)
	}
	defer sdl.Quit()
	window, err := sdl.CreateWindow("smiley face thing", sdl.WINDOWPOS_UNDEFINED, sdl.WINDOWPOS_UNDEFINED, WINDOW_H, WINDOW_W, sdl.WINDOW_SHOWN)
	if err != nil {
		panic(err)
	}
	defer func() {
		err = window.Destroy()
		if err != nil {
			panic(err)
		}
	}()
	renderer, err := sdl.CreateRenderer(window, -1, sdl.RENDERER_ACCELERATED)
	if err != nil {
		return
	}
	defer renderer.Destroy()
	err = img.Init(img.INIT_PNG)
	if err != nil {
		panic(err)
	}

	// setting up the data for the smiley
	var smileyImagePath string = "C:\\Users\\Alexandra\\Downloads\\epic face.png"
	smileyImageSurface, err := img.Load(smileyImagePath)
	if err != nil {
		panic(err)
	}
	texture, err := renderer.CreateTextureFromSurface(smileyImageSurface)
	if err != nil {
		panic(err)
	}
	defer func(texture *sdl.Texture) {
		err := texture.Destroy()
		if err != nil {
			panic(err)
		}
	}(texture)

	// main loop
	var startTime = time.Now()
	fmt.Println(startTime)

}
