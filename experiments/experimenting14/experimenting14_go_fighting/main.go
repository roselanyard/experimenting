package experimenting14_go_fighting

import (
	"github.com/EngoEngine/ecs"
	rl "github.com/gen2brain/raylib-go/raylib"
	sdl "github.com/veandco/go-sdl2/sdl"
)
import box2d "github.com/ByteArena/box2d"
// import ecs "github.com/EngoEngine/ecs"

func sdlInit() (*sdl.Window, *sdl.Renderer, func()) {
	err := sdl.Init(sdl.INIT_EVERYTHING)
	if err != nil {
		panic(err)
	}
	window, err := sdl.CreateWindow("black magic wizard ant", sdl.WINDOWPOS_UNDEFINED, sdl.WINDOWPOS_UNDEFINED, 640, 680, sdl.WINDOW_SHOWN)
	if err != nil {
		panic(err)
	}
	renderer, err := sdl.CreateRenderer(window, -1, 0)

	return window, renderer, func() {
		err = renderer.Destroy()
		if err != nil {
			panic(err)
		}
		err = window.Destroy()
		if err != nil {
			panic(err)
		}
	}
}

/*
type textureLoadingSystem struct {}

func (*textureLoadingSystem) Remove(ent ecs.BasicEntity) {}

func (*textureLoadingSystem) Update(dt float32) {

}
*/


type EntityRegistry struct {}
type id uint64

func (e EntityRegistry) newEntity (id id) (ok bool) {


	return ok
}

func main() {

	// ecs boilerplate
	var world = ecs.World{}

	// register entities


	window, renderer, closeRendererAndWindow := sdlInit()
	defer closeRendererAndWindow()

	//loadTextures()

	for !gameEnding {
		switch (gameContext.state)
	}
}
