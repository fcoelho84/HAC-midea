# Setup Home Assistant

## Instalação

### Via HACS (recomendado)

1. HACS → ⋮ → **Custom repositories**
2. URL: `https://github.com/fcoelho84/HAC-midea`
3. Category: **Integration**
4. Baixe **Midea Washer (LAN)** (use a release `0.1.0`, não o commit)
5. Reinicie o Home Assistant
6. **Settings → Devices & services → Add integration → Midea Washer (LAN)**

### Manual

1. Copie `custom_components/midea_washer` para a pasta `custom_components` do HA:

```bash
cp -r custom_components/midea_washer /config/custom_components/
```

2. Reinicie o Home Assistant.
3. **Settings → Devices & services → Add integration → Midea Washer (LAN)**.

## Credenciais V3

Se o aparelho for protocol 3, precisa de `token` e `key` (hex).

Formas comuns de obter:

1. Integração oficial **Midea** do HA (cloud só na configuração)
2. Ferramentas/community que logam no MSmartHome e listam devices
3. Captura do app (mitm) — fora do escopo deste repo

Cole token e key sem espaços.

## Checklist

- [ ] Lavadora e HA na mesma LAN (ou rota sem isolamento client)
- [ ] App MSmartHome **fechado** (só 1 TCP)
- [ ] IP fixo/DHCP reservation na lavadora
- [ ] Firewall libera UDP 6445 (descoberta) e TCP 6444
- [ ] Tipo correto: `0xDB` (front), `0xDA` (top), `0xDC` (dryer)

## Entidades esperadas

- Progress
- Time Remaining
- Power
- Start

## Troubleshooting

| Sintoma | Ação |
|---------|------|
| Discover vazio | Manual IP + device id; confira VLAN/AP isolation |
| Auth failed | Token/key errados ou expirados; regenere no cloud |
| Connect timeout | App aberto? IP errado? Porta 6444 |
| Status Unknown | Subtype Lua diferente; capture dump e compare com `docs/05-washer-db.md` |

## Alternativa

HA core já tem integração **Midea** com suporte a washer. Este HAC é focado, documentado a partir do APK 3.20.0, e útil se você quiser só lavadora / código próprio.
