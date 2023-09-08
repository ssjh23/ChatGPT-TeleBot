// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.20.0
// source: prompts.sql

package db

import (
	"context"
	"time"
)

const createPrompt = `-- name: CreatePrompt :one
INSERT INTO prompts 
(prompt, user_id, created_at)
VALUES 
($1, $2, $3) 
RETURNING id, prompt, user_id, created_at
`

type CreatePromptParams struct {
	Prompt    string    `json:"prompt"`
	UserID    int64     `json:"userId"`
	CreatedAt time.Time `json:"createdAt"`
}

func (q *Queries) CreatePrompt(ctx context.Context, arg CreatePromptParams) (Prompt, error) {
	row := q.db.QueryRowContext(ctx, createPrompt, arg.Prompt, arg.UserID, arg.CreatedAt)
	var i Prompt
	err := row.Scan(
		&i.ID,
		&i.Prompt,
		&i.UserID,
		&i.CreatedAt,
	)
	return i, err
}

const deletePrompts = `-- name: DeletePrompts :exec
DELETE FROM prompts 
WHERE id = $1
`

func (q *Queries) DeletePrompts(ctx context.Context, id int64) error {
	_, err := q.db.ExecContext(ctx, deletePrompts, id)
	return err
}

const getPrompt = `-- name: GetPrompt :one
SELECT id, prompt, user_id, created_at FROM prompts
WHERE id = $1 LIMIT 1
`

func (q *Queries) GetPrompt(ctx context.Context, id int64) (Prompt, error) {
	row := q.db.QueryRowContext(ctx, getPrompt, id)
	var i Prompt
	err := row.Scan(
		&i.ID,
		&i.Prompt,
		&i.UserID,
		&i.CreatedAt,
	)
	return i, err
}

const listPrompts = `-- name: ListPrompts :many
SELECT id, prompt, user_id, created_at FROM prompts
ORDER BY id
LIMIT $1
OFFSET $2
`

type ListPromptsParams struct {
	Limit  int32 `json:"limit"`
	Offset int32 `json:"offset"`
}

func (q *Queries) ListPrompts(ctx context.Context, arg ListPromptsParams) ([]Prompt, error) {
	rows, err := q.db.QueryContext(ctx, listPrompts, arg.Limit, arg.Offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var items []Prompt
	for rows.Next() {
		var i Prompt
		if err := rows.Scan(
			&i.ID,
			&i.Prompt,
			&i.UserID,
			&i.CreatedAt,
		); err != nil {
			return nil, err
		}
		items = append(items, i)
	}
	if err := rows.Close(); err != nil {
		return nil, err
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return items, nil
}

const updatePrompt = `-- name: UpdatePrompt :one
UPDATE prompts
SET prompt = $2
WHERE id = $1
RETURNING id, prompt, user_id, created_at
`

type UpdatePromptParams struct {
	ID     int64  `json:"id"`
	Prompt string `json:"prompt"`
}

func (q *Queries) UpdatePrompt(ctx context.Context, arg UpdatePromptParams) (Prompt, error) {
	row := q.db.QueryRowContext(ctx, updatePrompt, arg.ID, arg.Prompt)
	var i Prompt
	err := row.Scan(
		&i.ID,
		&i.Prompt,
		&i.UserID,
		&i.CreatedAt,
	)
	return i, err
}
