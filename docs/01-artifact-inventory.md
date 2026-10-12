# Inventário do artefato

## Arquivo

| Campo | Valor |
|-------|-------|
| Path | `/home/coelho/Downloads/SmartHome+(MSmartHome)_3.20.0_APKPure.xapk` |
| SHA-256 | `d2d78657923cf120a6f37e56f4fe371ca484845b178e7ae86b41f20887231730` |
| Formato | ZIP / XAPK v2 |
| Evidence | `ev_45296a201ebf2ec9b8661cc83ddbd96b3e31b12a83ef2f1b1e15e07ddc0e6d3c` |

## Conteúdo XAPK

| Arquivo | SHA-256 | Tamanho | Papel |
|---------|---------|---------|-------|
| `com.midea.ai.overseas.apk` | `0adf001fe9e06887f5ebe97744707a37bd7bb8ee89b43eb120d8b127aed51e70` | 148523242 | Base APK |
| `config.arm64_v8a.apk` | `d8ec953a3a46e139eb07b5de74fe584421604d19e599ccdc0b41fa70a0a9609d` | 27671956 | Native arm64 |
| `dynamicvideoeditor.apk` | `11bd4db4e3b1436e4588ba9bede3d8faa3a27635a83e487d78456bce9e162100` | 492719 | Feature dinâmica |
| `dynamicvideoeditor.config.arm64_v8a.apk` | `c27e5ecce3f33096bd2210e58abda4a65b92efb0e6f0ac53e3ea0755ef2b5c1a` | 37094401 | Native do feature |
| `manifest.json` | `a6d8a345d12ae06cf304837071bba3a166f20247fa1991f181347e4432e0527f` | 3918 | Metadados XAPK |
| `icon.png` | `60a6020042d706a19608bd11d64d62d5e4b90336b358fd0d6a96d78a16211e86` | 5497 | Ícone |

Extração REA: `/tmp/rea-extracted-9f778a95-d94e-4981-8377-81aa359ce2bd`  
Evidence extract: `ev_9c86b49b1df115d780efa08d44bd1ae2e3e969a0ec90b1f9c6e67744c49e9394`

## Identidade do app (`manifest.json`)

- `package_name`: `com.midea.ai.overseas`
- `name`: SmartHome
- `version_name`: `3.20.0`
- `version_code`: `320009`
- `min_sdk_version`: 28
- `target_sdk_version`: 36

Permissões relevantes: `INTERNET`, `ACCESS_WIFI_STATE`, `CHANGE_WIFI_MULTICAST_STATE`, `BLUETOOTH_*`, `ACCESS_FINE_LOCATION`, `NEARBY_WIFI_DEVICES`.

## Libs nativas relevantes (`config.arm64_v8a.apk`)

Copiadas para `artifacts/native/lib/arm64-v8a/`:

| Lib | Tamanho | Papel observado |
|-----|---------|-----------------|
| `libmsmartsdk.so` | 231968 | Lua 5.1 + JNI `com.midea.iot.msmart.protocol.lua.LuaState` |
| `libmidea_oem_core.so` | 332888 | JSON↔bit16, UART frames, AES keys (Ghidra) |
| `libmidea_common_bs.so` | 78560 | Helper comum |
| `liblua_parse.so` | 3614280 | Parser Lua adicional |
| `libsha256crypt.so` | 341208 | `Sha256CryptUtils` JNI |
| `libKwProtectSDK.so` | ~13MB | Packer KiwiVM |
| `libkadp.so` | ~1.1MB | Runtime Kiwi/KADP |

## Assets úteis

- `assets/com.midea.ai.appliances.cert.pem` — cert app `com.midea.ai.appliances` (MideaGroupIoT)
- `assets/kiwiguard.lic` — licença KiwiGuard
- `META-INF/services/com.midea.iot.msmart.IInitListener` → `com.midea.iot.msmart.MSPrivateKeyInitListenerImpl`

## O que não veio no XAPK

Scripts Lua por aparelho (`T_0000_DB_*.lua` etc.) e plugins H5/Weex de lavadora. O app baixa isso da nuvem Meicloud em runtime.
