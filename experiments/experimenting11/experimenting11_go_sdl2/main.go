package main

import (
	"log"

	"github.com/veandco/go-sdl2/img"
	"github.com/veandco/go-sdl2/sdl"
)

var done = make(chan bool)

func main() {
	var init_flags uint32 = sdl.INIT_EVERYTHING
	if err := sdl.Init(init_flags); err != nil {
		panic(err)
	}
	defer sdl.Quit()

	var windowpos_undefined int32 = sdl.WINDOWPOS_UNDEFINED

	window, err := sdl.CreateWindow("test", windowpos_undefined, windowpos_undefined, 800, 600, sdl.WINDOW_SHOWN)
	if err != nil {
		log.Fatal("Error initializing SDL2 window")
		panic(err)
	}

	img.Init(img.InitFlags(img.INIT_PNG))

	defer window.Destroy()

	renderer, err := sdl.CreateRenderer(window, -1, sdl.RENDERER_ACCELERATED)
	if err != nil {
		log.Fatal("Error initializing SDL2 renderer")
		panic(err)
	}
	if renderer != nil {
		for {

		}
	}

	<-done

}
