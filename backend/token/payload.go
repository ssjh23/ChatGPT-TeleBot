package token

import (
	"errors"
	"time"

	"github.com/gofrs/uuid"
)

var (
	ErrExpiredToken = errors.New("token has expired")
	ErrInvalidToken = errors.New("token is invalid")
)

type Payload struct {
	ID uuid.UUID `json:"id"`
	ChatID string `json:"chat_id"`
	IssuedAt time.Time `json:"issued_at"`
	ExpiresAt time.Time `json:"expires_at"`
}

func NewPayload(ChatID string, duration time.Duration) (*Payload, error) {
	tokenID, err := uuid.NewV7()
	if err != nil {
		return nil, err
	}

	payload := &Payload{
		ID: tokenID,
		ChatID: ChatID,
		IssuedAt: time.Now(),
		ExpiresAt: time.Now().Add(duration),
	}
	return payload, nil
}

/* Valid checks if the token payload is valid or not */
func (payload *Payload) Valid() error {
	if time.Now().After(payload.ExpiresAt) {
		return ErrExpiredToken
	}
	return nil
}
