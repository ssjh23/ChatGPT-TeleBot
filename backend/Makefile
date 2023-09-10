postgres:
	docker run --name telebot_backend -p 5439:5432 -e POSTGRES_USER=root -e POSTGRES_PASSWORD=secret -d postgres:12-alpine

createdb: 
	docker exec -it telebot_backend createdb --username=root --owner=root telebot_db

dropdb:
	docker exec -it telebot_backend dropdb telebot_db

migratecreate:
	migrate create -ext sql -dir db/migration -seq init_schema

migrateforce:
	migrate -path db/migration -database "postgresql://root:secret@localhost:5439/telebot_db?sslmode=disable" force ${version}

migrateup: 
	migrate -path db/migration -database "postgresql://root:secret@localhost:5439/telebot_db?sslmode=disable" -verbose up ${version}

migratedown:
	migrate -path db/migration -database "postgresql://root:secret@localhost:5439/telebot_db?sslmode=disable" -verbose down ${version}

sqlc:
	sqlc generate

test:
	go test -v -cover ./...

server: 
	go run main.go
	
.PHONY: postgres createddb dropdb migratecreate migrateup migratedown migrateforce sqlc test