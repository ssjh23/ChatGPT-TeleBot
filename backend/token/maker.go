package token

import "time"

/* Maker is a token maker interface */
type Maker interface {
	CreateToken(ChatID string, duration time.Duration) (string, error)
	VerifyToken(token string) (*Payload, error)
}