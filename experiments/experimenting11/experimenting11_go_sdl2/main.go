package main

import (
	"experimenting11_go_sdl2/experimenting11_go_chat_client"
)

import _ "net/http/pprof"

func main() {
	//go http.ListenAndServe("localhost:8080", nil)
	experimenting11_go_chat_client.ChatClient()
	//sdltest.SDLTest()
}
