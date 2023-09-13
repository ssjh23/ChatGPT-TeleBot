package api

import (
	"database/sql"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ssjh23/Chatgpt-Telebot/util"
)

type loginUserRequest struct {
	ChatID string `json:"chatId" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type loginUserResponse struct {
	AccessToken string `json:"accessToken"`
	User userResponse `json:"user"`
}

/* Login user, checking if user exists in db, password and returns token */
func (server *Server) loginUser (ctx *gin.Context) {
	var req loginUserRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}

	user, err := server.queries.GetUser(ctx, req.ChatID)
	if err != nil {
		if err == sql.ErrNoRows {
			ctx.JSON(http.StatusUnauthorized, errorResponse(err))
			return
		}
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	err = util.CheckPassword(req.Password, user.Password)
	if err != nil {
		ctx.JSON(http.StatusUnauthorized, errorResponse(err))
		return
	}

	accessToken, err := server.tokenMaker.CreateToken(
		user.ChatID, 
		server.config.AccessTokenDuration,
	)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	
	resp := loginUserResponse {
		User: newUserResponse(user),
		AccessToken: accessToken,
	}
	ctx.JSON(http.StatusOK, resp)
}
