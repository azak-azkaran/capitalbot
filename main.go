package main

import (
	"time"

	"net/http"
	"crypto/tls"

	"go.uber.org/zap"
)

var (
	Sugar     *zap.SugaredLogger
)

const (
	CAPITAL_URL = "https://api-capital.backend-capital.com/api/v1"
	DEMO_CAPITAL_URL = "https://demo-api-capital.backend-capital.com/api/v1"
)

func init(){
	logger, _ := zap.NewProduction()
	defer logger.Sync() // flushes buffer, if any
	Sugar = logger.Sugar()
}

func GetClient(timeout int) (*http.Client, error) {
	var tr *http.Transport
		tr = &http.Transport{
			Proxy: nil,
			// Disable HTTP/2.
			TLSNextProto: make(map[string]func(authority string, c *tls.Conn) http.RoundTripper),
		}

	return &http.Client{Transport: tr, Timeout: time.Duration(time.Duration(timeout) * time.Second)}, nil
}



func main(){
	Sugar.Info("Starting")
	client, err := GetClient(2)
	if err != nil {
		Sugar.Error(err)
	}

	resp,err := client.Get(DEMO_CAPITAL_URL + "/time")
	if err != nil {
		Sugar.Error(err)
	}
	Sugar.Info("Response: " + resp.Status)
}
