# Stack nativo

## Mapa JNI (observado via exports ELF)

### `libmsmartsdk.so`

Pacote Java esperado: `com.midea.iot.msmart.protocol.lua.LuaState`

| JNI | Função |
|-----|--------|
| `nativeLuaOpen` | `luaL_newstate` |
| `nativeOpenlibs` | `luaL_openlibs` + `luaopen_lua_extensions` |
| `nativeDofile` / `nativeDoString` | carrega script Lua |
| `nativeCall` / `nativePcall` | chama funções Lua |
| get/push/tostring/tonumber… | bridge tipado |

**Inferência:** cada subtype de aparelho usa um `.lua` que traduz JSON de UI ↔ bytes UART do dispositivo.

### `libmidea_oem_core.so`

SHA-256: `af57f2bda7166e122ebfa6004736334314b1d0361d1540e38749469f2fdd9441`  
Ghidra overview: 871 procedures — Evidence `ev_56dcfa30badad6edf3e723befa78798fe2d5de020b065ac594a9edfd320c187c`

Pacote Java: `com.midea.oem.iot.core.jni.OEMCoreNative`

| JNI | Papel |
|-----|-------|
| `getCommonAESKey` | devolve chave AES comum |
| `setCommonAESKey` | sobrescreve chave comum |
| `getKey` | chave por app-id / tipo |
| `jsonModelInit` | carrega modelo JSON |
| `bit16ToJsonData` / `jsonDataTo16Bit` | conversão payload |
| `init` / `setAppId` / `path` / `diff` | lifecycle OEM |

Símbolos C relevantes:

- `ms_make_query_uart_frame` @ `0x121b38`
- `ms_uart_pro_check_sum` @ `0x12166c`
- `combinate_json_by_uart_data_kh`
- `ms_aws_frame_init_kh`
- `support_*_frame_ac*` (AC explícito; lavadora via caminho Lua/OEM genérico)

### `libsha256crypt.so`

`com.midea.ai.overseas.base.crypt.Sha256CryptUtils`:
- `getEncryptString`
- `getEncryptValueFromByts`
- `setLogEnable`

## `getCommonAESKey` (Ghidra)

Evidence analyze: arquivo agent `d5e5cd2d-…`

Pseudocódigo (resumo): se cache vazio, cria `jstring` com literal:

```text
f526b03e0b591a6eeddf4fe77b9517fa
```

e devolve essa string.

**Observado:** chave hex de 32 chars embutida no `.so`.  
**Inferência:** usada no caminho OEM/cloud/common — **não** é a mesma chave LAN V2 `md5(SIGN_KEY)` dos stacks abertos (ver protocolo).

## `getKey` (Ghidra)

Evidence analyze: arquivo agent `90efa061-…`

- Sem permissão (`DAT_00154c89` bit0 == 0): `"You don't have permission."`
- Switch em `DAT_00154c1c` (app IDs `0x44d`, `0x44e`, `0x450`, …)
- Subtipos de chave 1..9
- Strings visíveis: `"meicloud"`, `"f526b03e0b591a6eeddf4fe77b9517fa"`, mais blobs base64 em `.rodata`

## UART checksum (Ghidra @ `0x12166c`)

```c
// ms_uart_pro_check_sum
sum = 0;
for each byte: sum = (sum + byte) & 0xff conceptually;
return -sum;  // i.e. (-sum) & 0xff
```

Equivalente Python: `(-sum(data)) & 0xff`  
Também escrito como `(~sum(data) + 1) & 0xff`.

## UART query frame (Ghidra @ `0x121b38`)

- Zera buffer destino
- Lê template de `s_model_map`
- Exige primeiro byte `0xAA` (`*src != -0x56`)
- Exige length ≥ 0x0C
- Copia template e recalcula checksum (vetorizado)

**Observado:** frames de aparelho começam com `0xAA` e usam checksum 8-bit two's complement.
