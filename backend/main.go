package main

import (
	"database/sql"
	"log"

	_ "github.com/lib/pq"
	"github.com/ssjh23/Chatgpt-Telebot/api"
	db "github.com/ssjh23/Chatgpt-Telebot/db/sqlc"
	"github.com/ssjh23/Chatgpt-Telebot/util"
)

func main() {
	config, err := util.LoadConfig(".")
	if err != nil {
		log.Fatal("Cannot load config file")
	}
	conn, err := sql.Open(config.DBDriver, config.DBSource)
	if err != nil {
		log.Fatal("Connection to database FAILED")
	}
	
	queries := db.New(conn)
	server := api.NewServer(queries)

	err = server.Start(config.ServerAddress)
	if err != nil {
		log.Fatal("Server FAILED TO START")
	}
}