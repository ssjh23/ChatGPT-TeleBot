package api

import (
	"log"

	"github.com/gin-gonic/gin"
	db "github.com/ssjh23/Chatgpt-Telebot/db/sqlc"
	"github.com/ssjh23/Chatgpt-Telebot/token"
	"github.com/ssjh23/Chatgpt-Telebot/util"
)

/* Server serves HTTP requests for the bot. */
type Server struct {
	config util.Config
	queries *db.Queries
	tokenMaker token.Maker
	router *gin.Engine
}

/* NewServer creates a new HTTP server and setup routing. */
func NewServer(config util.Config, queries *db.Queries) *Server {
	tokenMaker, err := token.NewPasetoMaker(config.TokenSymmetricKey)
	if err != nil {
		log.Fatal("cannot create token maker", err)
	}
	server := &Server{
		queries: queries,
		config: config,
		tokenMaker: tokenMaker,
	}
	server.setupRouter()
	return server
}

/* Helper function to setup router */
func (server *Server) setupRouter() {
	router := gin.Default()
	/* Server routes for user endpoints */
	router.POST("/users", server.createUser)
	router.POST("/users/login", server.loginUser)
	router.GET("/users/:id", server.getUser)
	router.GET("/users", server.listUsers)
	router.PATCH("/users/:id/password", server.updateUserPassword)
	router.DELETE("/users/:id", server.deleteUser)
	// router.POST("/prompts", server.createPrompt)
	// router.GET("/prompts/:id", server.getPrompt)
	// router.DELETE("/prompts/:id", server.deletePrompt)

	server.router = router
}

/* Start runs the HTTP server on a specific address. */
func (server *Server) Start(address string) error {
	return server.router.Run(address)
}

func errorResponse(err error) gin.H {
	return gin.H{"error": err.Error()}
}

