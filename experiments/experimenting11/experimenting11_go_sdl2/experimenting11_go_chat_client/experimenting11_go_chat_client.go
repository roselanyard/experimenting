package experimenting11_go_chat_client

import (
	"encoding/json"
	"experimenting11_go_sdl2/data"
	"experimenting11_go_sdl2/render"
	"experimenting11_go_sdl2/types"
	"fmt"
	"github.com/gorilla/websocket"
	"log"
	"strconv"
	"sync"
)

var outboundChannel = make(chan types.Message)
var inboundMessages = make(chan []byte)
var connClosed = make(chan bool)
var done = make(chan bool)

func ChatClient() {
	go client()
	render.RunGame()
	<-done
}

func client() {
	var uri = "ws://" + types.HOST + ":" + strconv.Itoa(types.PORT)
	for {
		var conn, httpResponse, err = websocket.DefaultDialer.Dial(uri, nil)
		if err != nil {
			log.Fatal("failed to dial websocket server: dialer", err)
		}
		fmt.Println(strconv.Itoa(httpResponse.StatusCode))
		handler(conn)
	}
}

func handler(conn *websocket.Conn) {
	var handlerWaitGroup sync.WaitGroup
	defer func() {
		err := conn.Close()
		if err != nil {
			log.Println("failed to close connection: ", err)
		}
	}()
	handlerWaitGroup.Add(3)
	go consumerHandler(&handlerWaitGroup)
	go producerHandler(conn, &handlerWaitGroup)
	go getMessagesFromWebSock(conn, &handlerWaitGroup)
	handlerWaitGroup.Wait()
}
func getMessagesFromWebSock(conn *websocket.Conn, handlerWaitGroup *sync.WaitGroup) {
	defer handlerWaitGroup.Done()
	for {
		var messageType, bytes, err = conn.ReadMessage()
		if err != nil {
			log.Println("failed to read message: ", err)
		}
		if messageType == websocket.TextMessage {
			//var message = string(bytes)
			inboundMessages <- bytes
		}
	}
}

func consumerHandler(handlerWaitGroup *sync.WaitGroup) {
	defer handlerWaitGroup.Done()
	for {
		select {
		case message := <-inboundMessages:
			fmt.Println(string(message))
			messageObj, err := data.MessageUnmarshal(message)
			if err != nil {
				log.Println("failed to unmarshal message: ", string(message), "\n", err)
			}
			switch messageObj.MessageType {
			case "GameStateMessage":
				fmt.Println("got GameStateMessage")
			}
		}
	}
}

func producerHandler(conn *websocket.Conn, handlerWaitGroup *sync.WaitGroup) {
	defer handlerWaitGroup.Done()
	for {
		select {
		case message := <-render.OutboundNetworkMessages:
			produce(conn, message)
		}
	}
}
func produce(conn *websocket.Conn, message types.Message) {
	messageJson, err := json.Marshal(message)
	if err != nil {
		log.Println("failed to marshal message: ", err)
	}
	err = conn.WriteMessage(websocket.TextMessage, messageJson)
	if err != nil {
		log.Println("failed to write message: ", err)
	}
}

func updateGameState(newGameState types.GameState) {
	data.NextGameStateChannel <- newGameState
}
