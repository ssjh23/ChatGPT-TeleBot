
-- name: CreatePrompt :one
INSERT INTO prompts 
(id, prompt, user_id, created_at)
VALUES 
($1, $2, $3, $4) 
RETURNING *;


-- name: GetPrompt :one
SELECT * FROM prompts
WHERE id = $1 LIMIT 1;

-- name: ListPrompts :many
SELECT * FROM prompts
ORDER BY id
LIMIT $1
OFFSET $2;

-- name: DeletePrompts :exec
DELETE FROM prompts 
WHERE id = $1;

-- name: UpdatePrompt :one
UPDATE prompts
SET prompt = $2
WHERE id = $1
RETURNING *;


