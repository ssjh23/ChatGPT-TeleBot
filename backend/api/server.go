package api

import (
	"github.com/gin-gonic/gin"
	db "github.com/ssjh23/Chatgpt-Telebot/db/sqlc"
)

/* Server serves HTTP requests for the bot. */
type Server struct {
	queries *db.Queries
	router *gin.Engine
}

/* NewServer creates a new HTTP server and setup routing. */
func NewServer(queries *db.Queries) *Server {
	server := &Server{queries: queries}
	router := gin.Default()

	/* Server routes for user endpoints */
	router.POST("/users", server.createUser)
	router.GET("/users/:id", server.getUser)
	router.GET("/users", server.listUsers)
	router.PATCH("/users/:id/password", server.updateUserPassword)
	router.DELETE("/users/:id", server.deleteUser)
	// router.POST("/prompts", server.createPrompt)
	// router.GET("/prompts/:id", server.getPrompt)
	// router.DELETE("/prompts/:id", server.deletePrompt)

	server.router = router
	return server
}

/* Start runs the HTTP server on a specific address. */
func (server *Server) Start(address string) error {
	return server.router.Run(address)
}

func errorResponse(err error) gin.H {
	return gin.H{"error": err.Error()}
}