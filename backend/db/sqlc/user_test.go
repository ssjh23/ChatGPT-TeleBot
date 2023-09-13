package db

import (
	"context"
	"database/sql"
	"testing"
	"time"

	"github.com/ssjh23/Chatgpt-Telebot/util"
	"github.com/stretchr/testify/require"
)

func createRandomUser(t *testing.T) User {
	hashedPassword, err := util.HashPassword(util.RandomPassword(20))
	require.NoError(t, err)

	arg := CreateUserParams{
		ChatID: util.RandomChatID(20),
		Password: hashedPassword,
	}

	user, err := testQueries.CreateUser(context.Background(), arg)
	require.NoError(t, err)
	require.NotEmpty(t, user)

	require.Equal(t, arg.ChatID, user.ChatID)
	require.Equal(t, arg.Password, user.Password)
	
	require.NotZero(t, user.ID)
	require.NotZero(t, user.CreatedAt)

	return user
}
func TestCreateUser(t *testing.T) {
	createRandomUser(t)
}

func TestGetUser(t *testing.T) {
	user1 := createRandomUser(t)
	user2, err := testQueries.GetUser(context.Background(), user1.ChatID)
	require.NoError(t, err)
	require.NotEmpty(t, user2)

	require.Equal(t, user1.ID, user2.ID)
	require.Equal(t, user1.ChatID, user2.ChatID)
	require.Equal(t, user1.Password, user2.Password)
	require.WithinDuration(t, user1.CreatedAt, user2.CreatedAt, time.Second)
}

func TestDeleteAccount(t *testing.T) {
	userOne := createRandomUser(t)
	deletedUser, err := testQueries.DeleteUser(context.Background(), userOne.ChatID)
	require.NoError(t, err)

	require.NotEmpty(t, deletedUser)
	require.Equal(t, userOne.ID, deletedUser.ID)
	require.Equal(t, userOne.ChatID, deletedUser.ChatID)
	require.Equal(t, userOne.Password, deletedUser.Password)
	require.WithinDuration(t, userOne.CreatedAt, deletedUser.CreatedAt, time.Second)

	userTwo, err := testQueries.GetUser(context.Background(), userOne.ChatID)
	require.Error(t, err)
	require.EqualError(t, err, sql.ErrNoRows.Error())
	require.Empty(t, userTwo)
}

func TestListAccounts(t *testing.T) {
	for i := 0; i < 10; i++ {
		createRandomUser(t)
	}

	arg := ListUsersParams {
		Limit: 5, 
		Offset: 5,
	}

	users, err := testQueries.ListUsers(context.Background(), arg)
	require.NoError(t ,err)
	require.Len(t, users, 5)

	for _, user := range users {
		require.NotEmpty(t, user)
	}
}

func TestUpdatePassword(t *testing.T) {
	userOne := createRandomUser(t)
	updatedPassword := util.RandomPassword(20)
	arg := UpdateUserPasswordParams {
		ChatID: userOne.ChatID,
		Password: updatedPassword,
	}
	updatedUserOne, err := testQueries.UpdateUserPassword(context.Background(), arg)
	require.NoError(t, err)
	require.NotEmpty(t, updatedUserOne)

	require.NotEqualValues(t, userOne.Password, updatedUserOne.Password)
	require.Equal(t, updatedPassword, updatedUserOne.Password)
	require.Equal(t, updatedUserOne.ID, userOne.ID)
	require.Equal(t, userOne.ChatID, updatedUserOne.ChatID)
	require.WithinDuration(t, time.Now(), updatedUserOne.CreatedAt, time.Second)
}