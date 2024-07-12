package types

import (
	"encoding/json"
	"github.com/google/uuid"
)

var HOST = "127.0.0.1"
var PORT = 5001

type PlayerSprite struct {
	Velocity [2]int32 `json:"velocity"`
	Position [2]int32 `json:"position"`
}

type Player struct {
	DisplayName string       `json:"display_name"`
	Score       int32        `json:"score"`
	Sprite      PlayerSprite `json:"sprite"`
}

type GameState struct {
	Players   map[uuid.UUID]Player `json:"players"`
	Timestamp uint64               `json:"timestamp"`
}

type PygameEvent struct {
	PygameType int32          `json:"pygame_type"`
	PygameDict map[string]any `json:"pygame_dict"`
}

type GameStateMessage struct {
	Data GameState `json:"GameState"`
}

type EventMessage struct {
	Data PygameEvent `json:"PygameEvent"`
}

type Message struct {
	MessageType string          `json:"message_type"`
	Data        json.RawMessage `json:"data"`
}
