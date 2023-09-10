package api

import (
	"database/sql"
	"net/http"

	"github.com/gin-gonic/gin"
	db "github.com/ssjh23/Chatgpt-Telebot/db/sqlc"
)

type createUserRequest struct {
	ChatID string `json:"chatId" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type getUserRequest struct {
	ID int64 `uri:"id" binding:"required,min=1"`
}

type listUsersRequest struct {
	PageID int32 `form:"page_id" binding:"required,min=1"`
	PageSize int32 `form:"page_size" binding:"required,min=5,max=10"`
}

type updateUserPasswordRequestID struct {
	ID int64 `uri:"id" binding:"required,min=1"`
}

type updateUserPasswordRequestPassword struct {
	Password string `json:"password" binding:"required"`
}

type deleteUserRequest struct {
	ID int64 `uri:"id" binding:"required,min=1"`
}

/* Server method that creates user */
func (server *Server) createUser(ctx *gin.Context) {
	var req createUserRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	arg := db.CreateUserParams{
		ChatID: req.ChatID,
		Password: req.Password,
	}
	user, err := server.queries.CreateUser(ctx, arg)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	ctx.JSON(http.StatusOK, user)
}

/* Server method that gets user */
func (server *Server) getUser(ctx *gin.Context) {
	var req getUserRequest
	if err := ctx.ShouldBindUri(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	user, err := server.queries.GetUser(ctx, req.ID)
	if err != nil {
		if err == sql.ErrNoRows {
			ctx.JSON(http.StatusNotFound, errorResponse(err))
			return
		}
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	ctx.JSON(http.StatusOK, user)
}

/* Server method that lists users*/
func (server *Server) listUsers(ctx *gin.Context) {
	var req listUsersRequest
	if err := ctx.ShouldBindQuery(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	arg := db.ListUsersParams{
		Limit: req.PageSize,
		Offset: (req.PageID - 1) * req.PageSize,
	}
	users, err := server.queries.ListUsers(ctx, arg)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	ctx.JSON(http.StatusOK, users)
}

/* Server method that updates user password*/
func (server *Server) updateUserPassword(ctx *gin.Context) {
	var reqID updateUserPasswordRequestID
	var reqPassword updateUserPasswordRequestPassword
	if err := ctx.ShouldBindJSON(&reqPassword); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	if err := ctx.ShouldBindUri(&reqID); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	arg := db.UpdateUserPasswordParams{
		ID: reqID.ID,
		Password: reqPassword.Password,
	}
	user, err := server.queries.UpdateUserPassword(ctx, arg)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	ctx.JSON(http.StatusOK, user)
}

/* Server method that deletes user */
func (server *Server) deleteUser(ctx *gin.Context) {
	var req deleteUserRequest
	if err := ctx.ShouldBindUri(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	deletedUser, err := server.queries.DeleteUser(ctx, req.ID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	ctx.JSON(http.StatusOK, deletedUser)
}
	
