package main

import (
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/gorilla/websocket"
)

var done chan interface{}
var interrupt chan os.Signal

var serverReadyChan = make(chan bool)

func main() {
	//const string HOST = "127.0.0.1"
	//const int PORT = 5001
	http.HandleFunc("/", handler)
	go http.ListenAndServe("localhost:5001", nil)

	clientMain()
}

func clientMain() {
	done = make(chan interface{})
	interrupt = make(chan os.Signal)

	signal.Notify(interrupt, os.Interrupt)
	socketUrl := "ws://localhost:5001" + "/"
	conn, _, err := websocket.DefaultDialer.Dial(socketUrl, nil)
	if err != nil {
		log.Fatal("Error connecting to Websocket Server:", err)
	}
	defer conn.Close()
	go receiveHandler(conn)

	for {
		select {
		case <-time.After(time.Duration(1) * time.Millisecond * 1000):
			err := conn.WriteMessage(websocket.TextMessage, []byte("client sends hello"))
			if err != nil {
				log.Println("Error during writing to websocket:", err)
				return
			}
		case <-interrupt:
			log.Println("Received signal from OS. Closing all pending connections...")
			err := conn.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseNormalClosure, ""))
			if err != nil {
				log.Println("Error during closing websocket:", err)
			}

			select {
			case <-done:
				log.Println("Server channel closed. Exiting...")
			case <-time.After(time.Duration(1) * time.Second):
				log.Println("Timeout in closing server. Exiting...")
			}
		}
	}

}
func receiveHandler(connection *websocket.Conn) {
	defer close(done)
	for {
		_, msg, err := connection.ReadMessage()
		if err != nil {
			log.Println("Error in receive:", err)
		}
		log.Printf("Received: %s\n", msg)
	}
}

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

func handler(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return
	}

	defer conn.Close()
	for {
		messageType, p, err := conn.ReadMessage()
		if err != nil {
			log.Println(err)
			return
		}
		if err := conn.WriteMessage(messageType, p); err != nil {
			log.Println(err)
			return
		}
	}

}
