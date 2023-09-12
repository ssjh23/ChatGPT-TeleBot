package token

import (
	"testing"
	"time"

	"github.com/golang-jwt/jwt"
	"github.com/ssjh23/Chatgpt-Telebot/util"
	"github.com/stretchr/testify/require"
)

func TestJWTMaker(t *testing.T) {
	maker, err := NewJWTMaker(util.RandomString(32))
	require.NoError(t, err)

	ChatID := util.RandomChatID(20)
	duration := time.Minute
	issuedAt := time.Now()
	expiredAt := issuedAt.Add(duration)

	token, err := maker.CreateToken(ChatID, duration)
	require.NoError(t, err)
	require.NotEmpty(t, token)

	Payload, err := maker.VerifyToken(token)
	require.NoError(t, err)
	require.NotEmpty(t, Payload)

	require.NotZero(t, Payload.ID)
	require.Equal(t, ChatID, Payload.ChatID)
	require.WithinDuration(t, issuedAt, Payload.IssuedAt, time.Second)
	require.WithinDuration(t, expiredAt, Payload.ExpiresAt, time.Second)
}

func TestExpiredJWTToken(t *testing.T){
	maker, err := NewJWTMaker(util.RandomString(32))
	require.NoError(t, err)

	token, err := maker.CreateToken(util.RandomChatID(20), -time.Minute)
	require.NoError(t, err)
	require.NotEmpty(t, token)

	payload, err := maker.VerifyToken(token)
	require.Error(t, err)
	require.EqualError(t, err, ErrExpiredToken.Error())
	require.Nil(t, payload)

}

func TestInvalidJWTTokenAlgNone(t *testing.T) {
	payload, err := NewPayload(util.RandomChatID(20), time.Minute)
	require.NoError(t, err)

	jwtToken := jwt.NewWithClaims(jwt.SigningMethodNone, payload)
	token, err := jwtToken.SignedString(jwt.UnsafeAllowNoneSignatureType)
	require.NoError(t, err)

	maker, err := NewJWTMaker(util.RandomString(32))
	require.NoError(t, err)

	payload, err = maker.VerifyToken(token)
	require.Error(t, err)
	require.EqualError(t, err, ErrInvalidToken.Error())
	require.Nil(t, payload)
}