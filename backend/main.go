package main

import (
	"database/sql"
	"log"

	"github.com/ssjh23/Chatgpt-Telebot/api"
	db "github.com/ssjh23/Chatgpt-Telebot/db/sqlc"
	_"github.com/lib/pq"
)

const (
	dbDriver = "postgres"
	dbSource = "postgresql://root:secret@localhost:5439/telebot_db?sslmode=disable"
	serverAddress = "localhost:8080"
)

func main() {
	conn, err := sql.Open(dbDriver, dbSource)
	if err != nil {
		log.Fatal("Connection to database FAILED")
	}
	
	queries := db.New(conn)
	server := api.NewServer(queries)

	err = server.Start(serverAddress)
	if err != nil {
		log.Fatal("Server FAILED TO START")
	}
}