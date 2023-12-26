# ChatGPT Telegram Bot 
## Backend
### Local Setup 
#### Pre-requisites
1. Docker and Docker Desktop
2. Go version 19.3
3. (Optional) Dbeaver

#### Step 0: Adding dependencies
1. Be in the same level directory as `go mod`
2. Run the following to get all the dependencies defined in go mod
```
go get .
```
#### Step 1: Set up Postgres Database
1. Pull a postgres version 12 image from Docker Hub
```
docker pull postgres:12-alpine
```
2. Be in the same level directory where `Makefile` is
3. Create a docker network named `telebot_network`
```
make network
```
If successful, a long hash of the docker network id will be printed
e.g. 
```
(base) seansoo@Seans-MacBook-Pro backend % make network
docker network create telebot_network
2beb972dc3fa79cade57c0a0e4c37d8f38431e30dfba42a4af93db848f267416
```
4. Create the docker container to run the postgres image and put it on the created docker network
```
make postgres
```
If successful, a long hash of the container id will be printed
```
(base) seansoo@Seans-MacBook-Pro backend % make postgres
docker run --name telebot_db --network telebot_network -p 5432:5432 -e POSTGRES_USER=root -e POSTGRES_PASSWORD=secret -d postgres:12-alpine
f486220f65ed9b844e82db2fbdd232c4432eb18ab85e159cfd886cb2b0db96b8
```
5. Create a database named `telebot_db` within the docker container
```
make createdb
```
6. Run migrations on the created database
```
make migrateuplocal
```
If successful, it should look similar to
```
(base) seansoo@Seans-MacBook-Pro backend % make migrateuplocal
migrate -path db/migration -database "postgresql://root:secret@localhost:5432/telebot_db?sslmode=disable" -verbose up 
2023/12/18 18:18:46 Start buffering 1/u init_schema
2023/12/18 18:18:46 Start buffering 2/u init_schema
2023/12/18 18:18:46 Read and execute 1/u init_schema
2023/12/18 18:18:46 Finished 1/u init_schema (read 10.55ms, ran 27.792084ms)
2023/12/18 18:18:46 Read and execute 2/u init_schema
2023/12/18 18:18:46 Finished 2/u init_schema (read 45.472375ms, ran 8.589833ms)
2023/12/18 18:18:46 Finished after 73.090791ms
2023/12/18 18:18:46 Closing source and database
```
#### Step 2 (Optional): Setting up of Dbeaver
This is dependent on what database management GUI you are using, if you plan to use any in the first place. This is setup will be using
DBeaver, but should be similar to other tools.

