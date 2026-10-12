# HAC-midea — Midea Washer para Home Assistant

Custom component LAN para lavadoras Midea/MSmartHome (`0xDA` / `0xDB` / `0xDC`), documentado a partir do APK **SmartHome 3.20.0**.

## Docs

Comece em [docs/00-overview.md](docs/00-overview.md).

| Doc | Conteúdo |
|-----|----------|
| [01](docs/01-artifact-inventory.md) | Inventário XAPK |
| [02](docs/02-packaging-kiwivm.md) | KiwiVM / DEX packed |
| [03](docs/03-native-stack.md) | Libs nativas + Ghidra |
| [04](docs/04-lan-protocol.md) | Protocolo LAN |
| [05](docs/05-washer-db.md) | Mensagens lavadora |
| [06](docs/06-evidence-ledger.md) | Ledger observado/inferido |
| [07](docs/07-ha-setup.md) | Instalação HA |

## Instalação rápida

```bash
cp -r custom_components/midea_washer /config/custom_components/
```

Reinicie o HA → adicione **Midea Washer (LAN)**.

## Entidades HA (lavadora)

**Sensores:** status, mode, program, progress, water level, temperature, spin speed, wash/spin times, time remaining, detergent, softener, stains, dirty degree.

**Controles:** power, start/pause, program, mode, water level, temperature, spin speed, wash time, spin time, detergent, softener.

Detalhe: [docs/05-washer-db.md](docs/05-washer-db.md).

## Achados-chave do RE

- Base APK protegido por **KiwiVM** (5 classes stub).
- Protocolo de aparelho em nativo: `libmsmartsdk.so` (Lua) + `libmidea_oem_core.so` (UART/AES/JSON).
- UART: header `0xAA`, checksum `(-sum) & 0xff` (Ghidra).
- AES OEM embutido `f526b03e0b591a6eeddf4fe77b9517fa` ≠ chave LAN `md5(SIGN_KEY)`.

## Estrutura

```text
custom_components/midea_washer/   # integração HA
artifacts/                        # libs/certs extraídos
docs/                             # documentação RE + setup
```
