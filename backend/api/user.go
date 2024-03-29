package api

import (
	"database/sql"
	"errors"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/lib/pq"
	db "github.com/ssjh23/Chatgpt-Telebot/db/sqlc"
	"github.com/ssjh23/Chatgpt-Telebot/token"
	"github.com/ssjh23/Chatgpt-Telebot/util"
)

type createUserRequest struct {
	ChatID string `json:"chatId" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type getUserRequest struct {
	ChatID string `uri:"chatId" binding:"required"`
}

type listUsersRequest struct {
	PageID int32 `form:"pageId" binding:"required,min=1"`
	PageSize int32 `form:"pageSize" binding:"required,min=5,max=10"`
}

type updateUserPasswordRequestID struct {
	ChatID string `uri:"chatId" binding:"required"`
}

type updateUserPasswordRequestPassword struct {
	Password string `json:"password" binding:"required"`
}

type userResponse struct {
	ChatID            string    `json:"chatId"`
	CreatedAt         time.Time `json:"createdAt"`
	PasswordUpdatedAt time.Time `json:"passwordUpdatedAt"`
}

type updateUserPasswordResponse struct {
	ID int64 `json:"id"`
	ChatID string `json:"chatId"`
	Message string `json:"message"`
}

type deleteUserRequest struct {
	ChatID string `uri:"chatId" binding:"required"`
}

func newUserResponse(user db.User) userResponse {
	return userResponse{
		ChatID: user.ChatID,
		CreatedAt: user.CreatedAt,
		PasswordUpdatedAt: user.PasswordUpdatedAt,
	}
}

/* Server method that creates user */
func (server *Server) createUser(ctx *gin.Context) {
	var req createUserRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	hashedPassword, err := util.HashPassword(req.Password)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	arg := db.CreateUserParams{
		ChatID: req.ChatID,
		Password: hashedPassword,
	}
	user, err := server.queries.CreateUser(ctx, arg)
	if err != nil {
		if pqError, ok := err.(*pq.Error); ok {
			switch pqError.Code.Name() {
			case "unique_violation":
				ctx.JSON(http.StatusForbidden, errorResponse(err))
				return
			}	
		}
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	resp := newUserResponse(user)
	ctx.JSON(http.StatusOK, resp)
}

/* Server method that gets user */
func (server *Server) getUser(ctx *gin.Context) {
	var req getUserRequest
	if err := ctx.ShouldBindUri(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	authPayload := ctx.MustGet(authorizationPayloadKey).(*token.Payload)
	if req.ChatID != authPayload.ChatID {
		err := errors.New("account does not belong to authenticated user")
		ctx.JSON(http.StatusUnauthorized, errorResponse(err))
		return
	}

	user, err := server.queries.GetUser(ctx, req.ChatID)
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
	authPayload := ctx.MustGet(authorizationPayloadKey).(*token.Payload)
	if reqID.ChatID != authPayload.ChatID {
		err := errors.New("account does not belong to authenticated user")
		ctx.JSON(http.StatusUnauthorized, errorResponse(err))
		return
	}
	updatedHashedPassword, err := util.HashPassword(reqPassword.Password)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	arg := db.UpdateUserPasswordParams{
		ChatID: reqID.ChatID,
		Password: updatedHashedPassword,
	}
	user, err := server.queries.UpdateUserPassword(ctx, arg)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}

	resp := updateUserPasswordResponse{
		ID: user.ID,
		ChatID: user.ChatID,
		Message: "Password updated successfully",
	}
	ctx.JSON(http.StatusOK, resp)
}

/* Server method that deletes user */
func (server *Server) deleteUser(ctx *gin.Context) {
	var req deleteUserRequest
	if err := ctx.ShouldBindUri(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, errorResponse(err))
		return
	}
	authPayload := ctx.MustGet(authorizationPayloadKey).(*token.Payload)
	if req.ChatID != authPayload.ChatID {
		err := errors.New("account does not belong to authenticated user")
		ctx.JSON(http.StatusUnauthorized, errorResponse(err))
		return
	}
	deletedUser, err := server.queries.DeleteUser(ctx, authPayload.ChatID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, errorResponse(err))
		return
	}
	ctx.JSON(http.StatusOK, deletedUser)
}


	
