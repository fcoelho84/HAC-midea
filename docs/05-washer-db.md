# Lavadora — sensores e controles

Layout de status alinhado a `midealocal` DB (`0xDB`) / body UART.

## Sensores (leitura)

| Entity key | Nome | Origem |
|------------|------|--------|
| `status` | Status | body[2] → idle/standby/start/pause/end/fault/delay |
| `mode` | Mode | body[3] |
| `program` | Program | body[4] |
| `progress` | Progress | bitmask body[16] |
| `water_level` | Water Level | body[5] |
| `temperature` | Wash Temperature | body[7] |
| `dehydration_speed` | Spin Speed | body[8] |
| `wash_time` | Wash Time Level | body[9] |
| `wash_time_value` | Wash Time Value | body[27] |
| `dehydration_time` | Spin Time Level | body[10] |
| `dehydration_time_value` | Spin Time Value | body[28] |
| `time_remaining` | Time Remaining | body[17..18] LE minutos |
| `detergent` | Detergent | body[11] |
| `softener` | Softener | body[12] |
| `stains` | Stains | body[26] |
| `dirty_degree` | Dirty Degree | body[30] |
| `washing_data_hex` | Washing Data | body[3:16] (diagnóstico) |

## Controles (escrita remota)

| Entity | Tipo | Ação |
|--------|------|------|
| `power` | switch | Liga/desliga |
| `start` | switch | Start / pause |
| `program` | select | Programa (cotton, eco, wool, …) |
| `mode` | select | Modo |
| `water_level` | select | Nível de água |
| `temperature` | select | Temperatura |
| `dehydration_speed` | select | Centrifugação RPM |
| `wash_time` | number | Nível tempo lavagem |
| `dehydration_time` | number | Nível tempo centrifugação |
| `detergent` | number | Nível detergente |
| `softener` | number | Nível amaciante |

Fluxo típico remoto:

1. Power on
2. Ajuste program / water / temp / spin / tempos
3. Start on

Params vão no bloco `washing_data` (13 bytes). Set usa frame `0x02` com `FF FF` + dados (sem forçar start). Start usa `FF 01` + `washing_data`.

## Limite real do protocolo

Stacks abertos só documentam **power** e **start** como set confirmado.  
Selects/numbers acima **escrevem** o mesmo bloco que a máquina ecoa no status — funciona na maioria dos 0xDB; subtype Lua estranho pode ignorar campos.

Se um select não mudar: confira subtype / capture dump e compare `washing_data_hex`.

## Programas (amostra)

`cotton`, `eco`, `fast_wash`, `mixed_wash`, `wool`, `baby_clothes`, `quick_wash`, `shirt`, `cold_wash`, `jean`, `silk`, `wash_and_dry`, `steam_care`, … (mapa completo em `const.py`).
