# Ledger de evidências

Cada conclusão liga a Evidence ID / método. Separar observado / inferido / desconhecido.

## Artefato

| Conclusão | Tipo | Evidence / método |
|-----------|------|-------------------|
| XAPK SHA-256 `d2d78657…` | Observado | `open_binary` + `inspect_artifact` `ev_45296a20…` |
| Package `com.midea.ai.overseas` 3.20.0 | Observado | `manifest.json` + JADX package inspect |
| Split APKs listados | Observado | inventory occurrences |

## Packing

| Conclusão | Tipo | Evidence |
|-----------|------|----------|
| Só 5 classes DEX visíveis | Observado | `search_android_classes` `ev_5aa11d3a…` |
| Entry `StubApplication` KiwiVM | Observado | `inspect_android_class` `ev_dd55135c…` |
| DEX real cifrado em runtime | Inferido | tamanho classes.dex + stub + `libKwProtectSDK.so` |
| Conteúdo Java msmart inacessível sem unpack | Desconhecido | — |

## Native

| Conclusão | Tipo | Evidence |
|-----------|------|----------|
| `libmsmartsdk` = Lua JNI msmart | Observado | `readelf` exports `Java_com_midea_iot_msmart_protocol_lua_*` |
| OEM JSON↔UART + AES | Observado | exports `OEMCoreNative_*` + strings |
| AES comum `f526b03e…` | Observado | Ghidra `getCommonAESKey` + `read_bytes` `0x13ffc2` `ev_d7ff92ef…` |
| `"meicloud"` em getKey | Observado | Ghidra pseudocode getKey |
| Checksum UART = `-sum` | Observado | Ghidra `ms_uart_pro_check_sum` `@0x12166c` |
| Frame UART começa `0xAA` | Observado | Ghidra `ms_make_query_uart_frame` `@0x121b38` |
| Sem string wash no OEM core | Observado | `search_strings wash` vazio `ev_f9b092a6…` |
| Lavadora via Lua remoto | Inferido | ausência local + padrão Meicloud plugins |

## Protocolo LAN / lavadora

| Conclusão | Tipo | Evidence |
|-----------|------|----------|
| TCP 6444 / UDP 6445 | Inferido (community) | stacks M-Smart; alinhado permissões Wi‑Fi multicast do app |
| Pacote 5A5A + AES-ECB md5(SIGN_KEY) | Inferido (community) | distinto da chave OEM observada |
| Envelope V3 8370 | Inferido (community) | necessário em aparelhos novos |
| Tipo 0xDB front load | Inferido (community) | mapeamento M-Smart |
| Layout status DB body | Inferido (community) | message body parser |
| Checksum/0xAA batem com OEM RE | Observado↔corroborado | Ghidra + implementação HAC |

## Desconhecidos abertos

1. Unpack completo do DEX KiwiVM (precisa runtime)
2. Lua exact subtype da lavadora do usuário
3. Endpoint cloud exato e payload de download de plugin nesta versão 3.20.0
4. Se `f526…` entra em algum handshake LAN novo (não visto no caminho LocalSecurity clássico)

## Artefatos locais no repo

```text
artifacts/manifest.json
artifacts/assets/com.midea.ai.appliances.cert.pem
artifacts/assets/kiwiguard.lic
artifacts/native/lib/arm64-v8a/libmsmartsdk.so
artifacts/native/lib/arm64-v8a/libmidea_oem_core.so
artifacts/native/lib/arm64-v8a/libmidea_common_bs.so
artifacts/native/lib/arm64-v8a/liblua_parse.so
artifacts/native/lib/arm64-v8a/libsha256crypt.so
```
