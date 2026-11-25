# TLS del despliegue cloud — 2026-11-24T23:56:39-06:00
Host: `juice-lab-masi-staging.onrender.com` · cliente: OpenSSL 3.5.7 (imagen fijada por digest)

| Versión | Resultado | Protocolo/cifrado negociado |
|---|---|---|
| tls1 | rechazada | alert protocol version |
| tls1_1 | rechazada | alert protocol version |
| tls1_2 | ACEPTADA | TLSv1.2, Cipher is ECDHE-ECDSA-AES128-GCM-SHA256 |
| tls1_3 | ACEPTADA | TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384 |

## Certificado
```
subject=CN=onrender.com
issuer=C=US, O=Google Trust Services, CN=WE1
notBefore=Nov 19 21:53:13 2026 GMT
notAfter=Feb 17 22:53:10 2027 GMT
X509v3 Subject Alternative Name: 
    DNS:onrender.com, DNS:*.onrender.com
```

## Redirección HTTP → HTTPS
- `http://juice-lab-masi-staging.onrender.com/` → HTTP/1.1 301 Moved Permanently Location: https://juice-lab-masi-staging.onrender.com/ 
- HSTS en HTTPS: strict-transport-security: max-age=31536000; includeSubDomains
