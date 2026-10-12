# Protocolo LAN M-Smart

## Portas

| Porta | Transporte | Uso |
|-------|------------|-----|
| 6445 | UDP broadcast | Descoberta |
| 6444 | TCP | Controle / status |

Uma conexão TCP por vez. Feche o app MSmartHome antes de usar o HAC.

## Camadas

```text
[ App / HAC ]
     |
     v
UART frame 0xAA ... checksum     <-- ms_make_query_uart_frame / checksum (REA)
     |
     v
AES-ECB + pacote 5A5A            <-- LocalSecurity LAN (community + REAES diverge)
     |
     v
(opcional) envelope 8370 V3      <-- handshake token/key
     |
     v
TCP 6444
```

## Frame UART (camada aparelho)

| Offset | Campo |
|--------|-------|
| 0 | `0xAA` |
| 1 | length (inclui checksum) |
| 2 | device type (`0xDB`, `0xDA`, …) |
| 3–5 | reserved |
| 6 | frame id |
| 7 | frame protocol |
| 8 | device protocol version |
| 9 | message type (`0x02` set, `0x03` query, `0x04` notify) |
| 10… | body (`body_type` + payload) |
| last | checksum de `bytes[1:-1]` |

Checksum: `(-sum(bytes[1:-1])) & 0xff` — **observado** em `ms_uart_pro_check_sum`.

## Pacote LAN `5A5A` (V2)

| Offset | Campo |
|--------|-------|
| 0–1 | `5A 5A` |
| 2–3 | message type (`01 11` comando) |
| 4–5 | length little-endian |
| 6–7 | `20 00` |
| 8–11 | message id |
| 12–19 | timestamp BCD-ish |
| 20–27 | device id little-endian 8 bytes |
| 28–39 | padding |
| 40… | AES-ECB(UART) |
| last 16 | `md5(packet + SIGN_KEY)` |

### Chaves — atenção

| Nome | Valor | Status |
|------|-------|--------|
| LAN SIGN_KEY | `xhdiwjnchekd4d512chdjx5d8e4c394D2D7S` | Usada pelos stacks abertos M-Smart |
| LAN AES key | `md5(SIGN_KEY)` = `6a92ef406bad2f0359baad994171ea6d` | Packet encrypt V2 |
| OEM common AES | `f526b03e0b591a6eeddf4fe77b9517fa` | **Observado** em `getCommonAESKey` |

As duas chaves **não** são iguais. O HAC usa a chave LAN (`md5(SIGN_KEY)`) para pacotes TCP. A chave OEM fica documentada para caminhos Meicloud/OEM.

## Protocolo V3 (`0x8370`)

1. TCP connect
2. Envia handshake: `encode_8370(token, MSGTYPE_HANDSHAKE_REQUEST=0)`
3. Resposta 64 bytes → deriva `tcp_key = xor(aes_cbc_decrypt(payload, key), key)`
4. Comandos: UART → 5A5A → `encode_8370(..., MSGTYPE_ENCRYPTED_REQUEST=6)`

Token e key (hex) vêm do cloud MSmartHome/Meiju após pairing.

## Descoberta UDP

Broadcast para `255.255.255.255:6445`. Resposta `5A5A` traz device id, IP, tipo.

## Cloud (fora do escopo do HAC v0.1)

App usa Meicloud (`"meicloud"` em `getKey`). Plugins Lua e token V3 baixam daí. HAC atual exige token/key manuais se o aparelho for V3.
