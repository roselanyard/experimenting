package data

import (
	"encoding/json"
	"experimenting11_go_sdl2/types"
	"fmt"
	"log"
)

var NextGameStateChannel = make(chan types.GameState)

func MessageUnmarshal(message []byte) (types.Message, error) {
	var msg types.Message
	fmt.Println(string(message))
	err := json.Unmarshal(message, &msg)
	if err != nil {
		log.Println("failed to unmarshal json as Message", err)
	}
	if msg.MessageType == "GameStateMessage" {
		var gameState types.GameState
		err = json.Unmarshal(msg.Data, &gameState)
		if err != nil {
			log.Println("failed to unmarshal json as GameState", err)
		}
		fmt.Println("GameState:", gameState)
		NextGameStateChannel <- gameState
	}
	return msg, err
}

func Data() types.Message {
	message := "{\"message_type\":\"GameStateMessage\",\"data\":{\"players\":{\"8e501af0-87cb-4159-be71-3980a98f7f52\":{\"display_name\":\"Anonymous Player\",\"score\":0,\"sprite\":{\"velocity\":[0,0],\"position\":[185,-250]}}}}}"
	messageBytes := []byte(message)
	messageObj := types.Message{}
	err := json.Unmarshal(messageBytes, &messageObj)
	if err != nil {
		log.Fatal("failed to unmarshal json")
	}
	return messageObj
}
