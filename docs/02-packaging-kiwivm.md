# Packaging KiwiVM

## Achado

JADX no base APK vê **apenas 5 classes**:

1. `com.kiwivm.security.StubApplication`
2. `com.kiwivm.security.Xkd`
3. `com.midea.ai.overseas.R`
4. `kdp.AR`
5. `kotlin.coroutines.jvm.internal.DebugProbesKt`

Evidence search classes: `ev_5aa11d3a4e8f70f00e64716222211081089cdae1c997f95f3796b0ef417e274e`  
Evidence StubApplication: `ev_dd55135c4ee8b68c066caf19dbee64276f8bbd11952e20315581f6af08b22e24`

`classes.dex` tem magic `dex\n035` e ~132 MB — DEX válido, mas o bytecode útil está cifrado/protegido pelo packer.

## StubApplication (observado)

Campos ofuscados: `LibName`, `M31N`, `PvCzj`, etc.  
Métodos: `attachBaseContext`, `onCreate`, `DOX`, `Gke`, …

Interpretação: Application stub carrega `libKwProtectSDK` / `libkadp`, descriptografa DEX em runtime e entrega classes reais (`com.midea.iot.msmart.*`, UI, cloud).

## Impacto na engenharia reversa

| Camada | Acessível estaticamente? |
|--------|--------------------------|
| Manifest / recursos | Parcial |
| Java/Kotlin de negócio | Não (sem unpack runtime) |
| `.so` nativos no split APK | Sim |
| Strings/export JNI nos `.so` | Sim |
| Plugins Lua de lavadora | Não (download cloud) |

Por isso o protocolo de lavadora foi reconstruído a partir das **libs nativas + formato LAN M-Smart**, não do Java descompilado.
