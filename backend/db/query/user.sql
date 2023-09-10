-- name: CreateUser :one
INSERT INTO users (
    chat_id,
    password
) VALUES (
    $1, $2
) RETURNING *;

-- name: GetUser :one
SELECT * FROM users
WHERE id = $1 LIMIT 1;

-- name: ListUsers :many
SELECT * FROM users
ORDER BY id
LIMIT $1
OFFSET $2;

-- name: UpdateUserPassword :one
UPDATE users 
SET password = $2
SET password_updated_at = now()
WHERE id = $1
RETURNING *;

-- name: DeleteUser :one
DELETE FROM users 
WHERE id = $1
RETURNING *;
