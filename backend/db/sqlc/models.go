// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.20.0

package db

import (
	"time"
)

type ChatgptPrompt struct {
	ID        int64     `json:"id"`
	Prompt    string    `json:"prompt"`
	UserID    int64     `json:"userId"`
	CreatedAt time.Time `json:"createdAt"`
}

type User struct {
	ID        int64     `json:"id"`
	ChatID    string    `json:"chatId"`
	Password  string    `json:"password"`
	CreatedAt time.Time `json:"createdAt"`
}