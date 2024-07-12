package render

import (
	"encoding/json"
	"experimenting11_go_sdl2/data"
	"experimenting11_go_sdl2/types"
	"fmt"
	"github.com/veandco/go-sdl2/img"
	"github.com/veandco/go-sdl2/ttf"
	"log"
	"os"
	"sync"
)
import "github.com/veandco/go-sdl2/sdl"

var localGameState types.GameState
var localGameStateRWLock sync.RWMutex
var timeOfLastServerMessage uint64
var timeOfLastPrediction uint64
var OutboundNetworkMessages = make(chan types.Message)
var windowRect = sdl.Rect{
	X: 0,
	Y: 0,
	W: 640,
	H: 480,
}

var msSansSerifPath = "C:/Windows/Fonts/micross.ttf"
var playerImagePath = "C:\\Users\\Alexandra\\PycharmProjects\\game_learning\\assets\\piano\\note.png"

type fontMap struct {
	fonts map[string]*ttf.Font
}

func loadFonts() fontMap {
	var err = ttf.Init()
	if err != nil {
		log.Fatal("failed to initialize fonts: ", err)
	}
	msSansSerif, err := ttf.OpenFont(msSansSerifPath, 12)
	fontMap := fontMap{fonts: make(map[string]*ttf.Font)}
	fontMap.fonts[msSansSerifPath] = msSansSerif
	if err != nil {
		log.Fatal("failed to open font: ", err)
	}
	return fontMap
}

func RunGame() {
	localGameState := <-data.NextGameStateChannel
	fontMap := loadFonts()
	window, renderer, err := getInitRenderContext()
	if err != nil {
		log.Fatal(err)
	}
	for {
		handleEvents()
		select {
		case gameState := <-data.NextGameStateChannel:
			localGameStateRWLock.Lock()
			localGameState = gameState
			localGameStateRWLock.Unlock()
		default:
			tick()
		}

		localGameStateRWLock.RLock()
		renderGame(localGameState, window, renderer, fontMap)
		localGameStateRWLock.RUnlock()
	}
}

func tick() {
	// update the local game state with a prediction
	currentTime := sdl.GetTicks64()
	var deltaTime = currentTime - timeOfLastPrediction
	localGameStateRWLock.Lock()
	var updatedGameState = localGameState
	updatedGameState.Timestamp = currentTime
	for player := range localGameState.Players {
		var position = localGameState.Players[player].Sprite.Position
		var velocity = localGameState.Players[player].Sprite.Velocity
		// velocity in units of pixels per second
		position[0] += velocity[0] * int32(deltaTime/1000)
		position[1] += velocity[1] * int32(deltaTime/1000)
	}
	localGameState = updatedGameState
	localGameStateRWLock.Unlock()
}

func handleEvents() {
	sdl.PumpEvents()
	for event := sdl.PollEvent(); event != nil; event = sdl.PollEvent() {
		switch event.(type) {
		case sdl.QuitEvent:
			os.Exit(0)
		case sdl.KeyboardEvent:
			switch event.(sdl.KeyboardEvent).Keysym.Sym {
			case sdl.K_w, sdl.K_d, sdl.K_a, sdl.K_s:
				handleMovement(event.(sdl.KeyboardEvent))
			}
		}
	}
}

func handleMovement(event sdl.KeyboardEvent) {
	var pressedKey = ""
	var eventType = 0

	switch event.State {
	case sdl.PRESSED:
		eventType = 768
		switch event.Keysym.Sym {
		case sdl.K_a:
			fmt.Printf("pressed a")
		case sdl.K_w:
			pressedKey = "w"
		case sdl.K_d:
			pressedKey = "d"
		case sdl.K_s:
			pressedKey = "s"
		}
	case sdl.RELEASED:
		eventType = 769
		switch event.Keysym.Sym {
		case sdl.K_a:
			pressedKey = "a"
		case sdl.K_w:
			pressedKey = "w"
		case sdl.K_d:
			pressedKey = "d"
		case sdl.K_s:
			pressedKey = "s"
		}
	}

	var pygameDictToSend = map[string]any{}
	pygameDictToSend["unicode"] = pressedKey
	pygameDictToSend["key"] = event.Keysym.Sym
	pygameDictToSend["mod"] = 4096
	pygameDictToSend["window"] = nil
	pygameEventToSend := types.PygameEvent{
		PygameType: int32(eventType),
		PygameDict: pygameDictToSend, // the dict pygame would send
	}
	pygameEventToSendJson, err := json.Marshal(pygameEventToSend)
	if err != nil {
		log.Fatal("failed to serialize pygameEventToSend")
	}
	messageToSend := types.Message{
		MessageType: "EventMessage",
		Data:        pygameEventToSendJson,
	}
	OutboundNetworkMessages <- messageToSend

	// then handle predictions
}

func getInitRenderContext() (*sdl.Window, *sdl.Renderer, error) {
	var initFlags uint32 = sdl.INIT_EVERYTHING
	var windowFlags = sdl.WINDOW_SHOWN
	var err = sdl.Init(initFlags)
	if err != nil {
		log.Fatal("failed to initialize sdl: ", err)
	}
	window, err := sdl.CreateWindow("window", sdl.WINDOWPOS_UNDEFINED, sdl.WINDOWPOS_UNDEFINED, windowRect.W, windowRect.H, windowFlags)
	if err != nil {
		log.Fatal("failed to create window: ", err)
	}

	renderer, err := sdl.CreateRenderer(window, -1, sdl.RENDERER_ACCELERATED)
	if err != nil {
		log.Fatal("failed to create renderer: ", err)
	}
	return window, renderer, nil
}

func renderGame(localGameState types.GameState, window *sdl.Window, renderer *sdl.Renderer, fontMap fontMap) {
	localGameStateRWLock.RLock()
	localGameStateJSON, err := json.Marshal(localGameState)
	localGameStateText := string(localGameStateJSON)
	localGameStateRWLock.RUnlock()
	fontSurface, err := fontMap.fonts[msSansSerifPath].RenderUTF8Solid(localGameStateText, sdl.Color{255, 255, 255, 0})
	if err != nil {
		log.Fatal("failed to render text", err)
	}
	defer fontSurface.Free()
	err = renderer.SetDrawColor(0, 0, 0, 0)
	if err != nil {
		log.Fatal("failed to set color", err)
	}
	err = renderer.FillRect(&windowRect)
	err = renderer.SetDrawColor(0, 0, 255, 255)
	if err != nil {
		log.Fatal("failed to fill display rect", err)
	}
	fontTexture, err := renderer.CreateTextureFromSurface(fontSurface)
	if err != nil {
		log.Fatal("failed to create texture from text", err)
	}
	defer func() {
		err = fontTexture.Destroy()
		if err != nil {
			log.Fatal("failed to destroy texture", err)
		}
	}()
	_, _, w, h, err := fontTexture.Query()
	fontTextureRect := sdl.Rect{W: w, H: h}
	err = renderer.Copy(fontTexture, &fontTextureRect, &fontTextureRect)
	if err != nil {
		log.Fatal("failed to copy font texture to display", err)
	}
	playerTexture, err := img.LoadTexture(renderer, playerImagePath)
	if err != nil {
		log.Fatal("failed to load player texture", err)
	}
	defer func() {
		err := playerTexture.Destroy()
		if err != nil {
			log.Fatal("failed to destroy player texture", err)
		}
	}()
	_, _, w, h, err = playerTexture.Query()
	if err != nil {
		log.Fatal("failed to query player texture", err)
	}
	var playerTextureRect = sdl.Rect{
		X: 0,
		Y: 0,
		W: w,
		H: h,
	}

	for player := range localGameState.Players {
		position := localGameState.Players[player].Sprite.Position
		playerTextureRectTranspose := sdl.Rect{
			X: 0 + position[0],
			Y: 0 + position[1],
			W: w,
			H: h,
		}
		err = renderer.Copy(playerTexture, &playerTextureRect, &playerTextureRectTranspose)
		if err != nil {
			log.Fatal("failed to copy player texture to display", err)
		}
	}

	renderer.Present()
	err = renderer.Clear()
	if err != nil {
		log.Fatal("failed to clear renderer", err)
	}
}
