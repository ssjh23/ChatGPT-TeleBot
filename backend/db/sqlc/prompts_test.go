package db

import (
	"context"
	"database/sql"
	"testing"

	"github.com/ssjh23/Chatgpt-Telebot/util"
	"github.com/stretchr/testify/require"
)

func createRandomPrompt(t *testing.T) Prompt {
	testUser, err := testQueries.CreateUser(context.Background(), CreateUserParams{
		ChatID: util.RandomChatID(20),
		Password: util.RandomPassword(20),
	})
	require.NoError(t, err)
	
	arg := CreatePromptParams{
		Prompt: util.RandomPrompt(20),
		UserID: testUser.ID,
	}

	prompt, err := testQueries.CreatePrompt(context.Background(), arg)
	require.NoError(t, err)
	require.NotEmpty(t, prompt)

	require.Equal(t, arg.Prompt, prompt.Prompt)
	require.Equal(t, arg.UserID, prompt.UserID)
	
	require.NotZero(t, prompt.ID)
	require.NotZero(t, prompt.CreatedAt)

	return prompt
}

func TestCreatePrompt(t *testing.T) {
	createRandomPrompt(t)
}
func TestGetPrompt(t *testing.T) {
	promptOne := createRandomPrompt(t)
	promptTwo, err := testQueries.GetPrompt(context.Background(), promptOne.ID)
	require.NoError(t, err)
	require.NotEmpty(t, promptTwo)

	require.Equal(t, promptOne.ID, promptTwo.ID)
	require.Equal(t, promptOne.Prompt, promptTwo.Prompt)
	require.Equal(t, promptOne.UserID, promptTwo.UserID)
}

func TestDeletePrompt(t *testing.T) {
	promptOne := createRandomPrompt(t)
	err := testQueries.DeletePrompts(context.Background(), promptOne.ID)
	require.NoError(t, err)

	promptTwo, err := testQueries.GetPrompt(context.Background(), promptOne.ID)
	require.Error(t, err)
	require.EqualError(t, err, sql.ErrNoRows.Error())
	require.Empty(t, promptTwo)
}

func TestListPrompts(t *testing.T) {
	for i := 0; i < 10; i++ {
		createRandomPrompt(t)
	}
	arg := ListPromptsParams{
		Limit:  5,
		Offset: 5,
	}
	allPrompts, err := testQueries.ListPrompts(context.Background(), arg)
	require.NoError(t, err)
	require.Len(t, allPrompts, 5)

	for _, prompt := range allPrompts {
		require.NotEmpty(t, prompt)
	}
}

func TestUpdatePrompt(t *testing.T) {
	promptOne := createRandomPrompt(t)
	arg := UpdatePromptParams{
		ID:     promptOne.ID,
		Prompt: util.RandomPrompt(20),
	}
	promptTwo, err := testQueries.UpdatePrompt(context.Background(), arg)
	require.NoError(t, err)
	require.NotEmpty(t, promptTwo)

	require.Equal(t, promptOne.ID, promptTwo.ID)
	require.Equal(t, arg.Prompt, promptTwo.Prompt)
	require.Equal(t, promptOne.UserID, promptTwo.UserID)
}