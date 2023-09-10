package main

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.Any("/v1/*path", func(c *gin.Context) {
		path := c.Param("path")
		targetURL := "https://api.openai.com" + path

		client := &http.Client{}
		req, err := http.NewRequest(c.Request.Method, targetURL, c.Request.Body)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer "+os.Getenv("OPENAI_API_KEY"))

		resp, err := client.Do(req)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer resp.Body.Close()

		for key, values := range resp.Header {
			for _, value := range values {
				c.Writer.Header().Set(key, value)
			}
		}

		c.Status(resp.StatusCode)

		_, err = io.Copy(c.Writer, resp.Body)
		if err != nil {
			fmt.Println(err)
		}
	})

	r.Run(":4242")
}
