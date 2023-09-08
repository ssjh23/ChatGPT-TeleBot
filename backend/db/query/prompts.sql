
-- name: CreatePrompt :one
INSERT INTO chatgpt_prompts 
(prompt, user_id)
VALUES 
($1, $2)
RETURNING *;


-- name: GetPrompt :one
SELECT * FROM chatgpt_prompts
WHERE id = $1 LIMIT 1;

-- name: ListPrompts :many
SELECT * FROM chatgpt_prompts
ORDER BY id
LIMIT $1
OFFSET $2;

-- name: DeletePrompts :exec
DELETE FROM chatgpt_prompts 
WHERE id = $1;

-- name: UpdatePrompt :one
UPDATE chatgpt_prompts
SET prompt = $2
WHERE id = $1
RETURNING *;


