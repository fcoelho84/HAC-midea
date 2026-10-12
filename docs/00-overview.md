# Visão geral

Integração Home Assistant Custom (HAC) para máquinas de lavar Midea/MSmartHome via LAN.

## Objetivo

Controlar lavadora Midea na mesma rede do Home Assistant sem depender do app aberto.

## Fontes de evidência

| Tipo | Fonte | Papel |
|------|-------|-------|
| Observado | XAPK `SmartHome+(MSmartHome)_3.20.0_APKPure.xapk` | Inventário, libs nativas, packer |
| Observado | REA + JADX | Manifest/classes stub KiwiVM |
| Observado | REA + Ghidra 12.1.4 | `libmidea_oem_core.so` AES/UART |
| Inferido | Formato LAN 5A5A / 8370 + mensagens 0xDB | Cruzamento com stacks M-Smart abertos |
| Desconhecido | Plugins Lua por subtype da lavadora | Baixados em runtime; não estão no XAPK |

## Arquitetura em uma frase

App Android empacota o DEX com KiwiVM; o protocolo de aparelho passa por JNI nativo (`libmsmartsdk.so` Lua + `libmidea_oem_core.so` JSON/UART/AES); a lavadora na LAN escuta TCP `6444` e responde a frames `0xAA` dentro de pacotes `5A5A` (V2) ou envelope `8370` (V3).

## O que o HAC faz

- Descoberta UDP na LAN
- Auth V3 (token/key) quando necessário
- Todos os sensores de ciclo (status, programa, água, temp, spin, tempos, detergente, …)
- Controles remotos: power, start/pause, program, mode, water level, temperature, spin, tempos, detergent/softener
- Tipos `0xDA`, `0xDB`, `0xDC`

## Limitações

- Subtipos com Lua custom podem ter bytes de status diferentes
- Só uma conexão LAN por vez (feche o app MSmartHome)
- Token/key V3 vêm da nuvem Midea; este repo não automatiza login cloud ainda
- DEX real do app não foi desempacotado (KiwiVM)

## Índice

1. [Inventário do artefato](01-artifact-inventory.md)
2. [Packaging KiwiVM](02-packaging-kiwivm.md)
3. [Stack nativo](03-native-stack.md)
4. [Protocolo LAN](04-lan-protocol.md)
5. [Lavadora 0xDB/0xDA](05-washer-db.md)
6. [Ledger de evidências](06-evidence-ledger.md)
7. [Setup no Home Assistant](07-ha-setup.md)
