# SCUM DB Edit — Especificação Técnica Completa (v1.10)

## 0) Objetivo do produto
Aplicativo **Java 8+ (Swing)** multiplataforma (Linux/Windows) para **abrir, visualizar e editar** o banco de dados **SQLite** do servidor **SCUM** (`scum.db`).  
Requisitos-chaves:

- UI por **abas**: Jogador, Inventário, Veículos, Clã, Presets, Avançado (Blobs), Relatório do Modelo, Sobre/Help.
- **Cálculo** e **edição reversa** de atributos dinâmicos (**STR/DEX/CON/INT**).
- Parser de **blobs** (UE4) + parser alternativo (XML/textual) para inventário.
- **Validações** de tipo e de intervalo (incluindo **regras cruzadas**: exemplo `Quantity ≤ StacksCount*StackSize`).
- **Backup automático** e transação segura a cada gravação.
- **Logs** com rotação por **tamanho + data**, rollover **diário**, logs contendo **SteamID** e **PlayerId** quando pertinente.
- **Presets** (JSON) com export/import, aplicáveis ao jogador atual.
- **Perfis Maven** (`dev`, `prod`) e **.jar** executável “double-click”.
- **CI (GitHub Actions)**: build, testes, e **release** anexando `.jar` em tags.

> **IMPORTANTE**: O banco do SCUM **varia por build**. A especificação prevê **adapters** para cobrir esquemas frequentes:
> - Modelo A: `entity` + `entity_component` (+ `expirable_entity_component`) — **UE4/ConZ** blobs
> - Modelo B: tabelas “diretas” (ex.: `Characters`, `Vehicles`, `Clans`…) — **campos explícitos**  
> O aplicativo **detecta** qual esquema está presente e seleciona o **adapter** adequado.

---

## 1) Arquitetura & pastas

**Padrão MVC + Services + DAO + Adapters**.

```
scum-db-edit/
├─ scum.db                        # banco real (fornecido no repo)
├─ src/
│  ├─ main/java/
│  │  └─ com/scumdb/editor/
│  │     ├─ ui/                  # Swing (frames, panels)
│  │     │  ├─ App.java          # main()
│  │     │  ├─ MainFrame.java
│  │     │  └─ tabs/
│  │     │     ├─ PlayerPanel.java
│  │     │     ├─ InventoryPanel.java
│  │     │     ├─ VehiclePanel.java
│  │     │     ├─ ClanPanel.java
│  │     │     ├─ PresetPanel.java
│  │     │     ├─ BlobsPanel.java            # “Avançado (Blobs)”
│  │     │     └─ ModelReportPanel.java      # relatório + “reaprender”
│  │     ├─ model/               # POJOs
│  │     │  ├─ Player.java
│  │     │  ├─ Item.java
│  │     │  ├─ Vehicle.java
│  │     │  ├─ Clan.java
│  │     │  └─ InventoryNode.java
│  │     ├─ dao/                 # DAO base + Adapters (A/B)
│  │     │  ├─ Database.java
│  │     │  ├─ PlayerDao.java
│  │     │  ├─ InventoryDao.java
│  │     │  ├─ VehicleDao.java
│  │     │  ├─ ClanDao.java
│  │     │  ├─ adapter/
│  │     │  │  ├─ SchemaDetector.java
│  │     │  │  ├─ AdapterA_EntityBased.java  # entity/entity_component
│  │     │  │  └─ AdapterB_ClassicTables.java# Characters/Inventory etc.
│  │     ├─ service/
│  │     │  ├─ PlayerService.java
│  │     │  ├─ InventoryService.java
│  │     │  ├─ VehicleService.java
│  │     │  ├─ ClanService.java
│  │     │  ├─ BlobService.java              # parsing/edição de blobs
│  │     │  └─ AttributeModelService.java    # cálculo STR/DEX/CON/INT
│  │     ├─ util/
│  │     │  ├─ LoggerConfig.java
│  │     │  ├─ SQLiteUtils.java
│  │     │  ├─ IoUtils.java
│  │     │  ├─ Validation.java
│  │     │  ├─ HexDump.java
│  │     │  └─ Zlib.java
│  │     └─ presets/
│  │        ├─ Preset.java
│  │        └─ PresetIO.java
│  └─ main/resources/
│     ├─ log4j2.xml
│     ├─ presets/               # presets exemplo
│     │  ├─ guerreiro.json
│     │  └─ explorador.json
│     └─ model/weights.json     # pesos do modelo após “reaprender”
├─ scripts/
│  ├─ run-windows.bat
│  └─ run-linux.sh
├─ pom.xml
└─ README.md
```

---

## 2) Banco de dados: detecção de esquema & consultas

### 2.1 SchemaDetector

- Consulta `sqlite_master` para listar tabelas.
- **Se** encontrar `entity` + `entity_component` ⇒ **Adapter A** (UE4).
- **Se** encontrar `Characters` ⇒ **Adapter B** (tabelas clássicas).
- Se ambos presentes, priorize A (mais moderno).

```sql
-- detecção
SELECT name FROM sqlite_master WHERE type='table';
```

### 2.2 Adapter A (entity/entity_component)

**Tabelas-chave** (nomes típicos, podem variar levemente):

- `entity`  
  Campos esperados (observados em bancos reais; podem variar):
  - `id` (INTEGER PK)
  - `class` (TEXT) — ex.: `FPrisonerEntity` para jogadores
  - `owning_entity_id` (INTEGER, opcional)
  - `parent_entity_id` (INTEGER, opcional)
  - `location` / `rotation` (opcional)
  - `data` (BLOB, frequentemente **NULL para FPrisonerEntity**)

- `entity_component`
  - `id` (PK)
  - `entity_id` (FK para `entity.id`)
  - `class` (TEXT) — **pode estar vazio** em alguns bancos
  - `data` (BLOB) — **dados UE4** (assinatura típica `++UE4+Release-4.27.7`, paths `/Script/ConZ.*`)
  - Tamanho comum: ~600–900 bytes; às vezes maior.

- `expirable_entity_component`
  - `entity_component_id` (FK)
  - `created_at` (timestamp)
  - Sem `class`; tipo do componente vem de `entity_component`.

**Identificação de jogadores**:
```sql
SELECT id FROM entity WHERE class = 'FPrisonerEntity';
```

**Componentes por jogador**:
```sql
SELECT id, class, LENGTH(data) AS len
FROM entity_component
WHERE entity_id = ? AND data IS NOT NULL AND LENGTH(data) > 0;
```

> **Observação**: muitos bancos reais **não** guardam dados do jogador em `entity.data` (fica vazio); os dados ficam nos **componentes**.

### 2.3 Adapter B (tabelas clássicas)

Tabelas esperadas (nomes exemplares; a implementação deve ser tolerante):

- `Characters(Id, characterName, SteamId, FamePoints, Wallet, Wallet2, Inventory BLOB, ...)`
- `Vehicles(Id, Type, Location, OwnerId, ...)`
- `Clans(Id, Name, ...)`
- `ClanMembers(ClanId, MemberId(=SteamId), Rank, ...)`

Consultas típicas:

```sql
-- listar jogadores
SELECT Id, characterName, SteamId FROM Characters ORDER BY characterName;

-- carregar dados básicos
SELECT FamePoints, Wallet AS Money, Wallet2 AS Gold FROM Characters WHERE Id=?;

-- inventário (blob)
SELECT Inventory FROM Characters WHERE Id=?;

-- veículos
SELECT Id, Type, Location, OwnerId FROM Vehicles WHERE OwnerId=?;

-- clã do jogador
SELECT c.Id, c.Name, m.Rank
FROM ClanMembers m JOIN Clans c ON m.ClanId = c.Id
WHERE m.MemberId = ?;
```

---

## 3) Modelo de atributos dinâmicos (STR/DEX/CON/INT)

### 3.1 Fontes dos atributos
- **Adapter A (UE4)**: ler **componentes** do jogador com `/Script/ConZ.*`. Ex.:  
  `RangedResourceConsumerEntityComponentSave`, `Metabolism*`, `*Physical*`, etc.  
  Dados **serializados** no formato UE4.  
  **Heurística**:
  - Detectar se `data` possui `zlib` (bytes 0x78 0x9C). Se sim, **descomprimir**.
  - Caso contrário, tratar como **binário cru** (UE4 FProperty/UStruct).
  - Como fallback, percorrer `float` a cada 4 bytes (`little-endian`) e classificar por **faixa plausível**:
    - 0–100 (% ou “health-like”)
    - 0–10 (atributo nível SCUM)
    - 0–1000 (xp-like ou acumulações)
  - Opcional: mapear por **`class`** do componente usando arquivo `resources/model/weights.json` que guarda **offsets** conhecidos por versões (ex.: `"MetabolismComponent": {"MuscleMass": 8, "Fat": 4, ...}` em unidades de 4 bytes).

- **Adapter B**: **não** há atributos diretos. Usar:
  - Inventário (peso total/massa = proxy para **STR**).
  - Saúde, ferimentos, stamina = **CON**.
  - Uso de armas leves, corrida (se houver estatísticas de eventos) = **DEX**.
  - INT = default (ex.: 2.5) caso não haja insumo confiável.

### 3.2 Fórmulas (baseline)
> **Podem ser “reaprendidas”** via regressão linear e persistidas em `resources/model/weights.json`.

```text
STR = w1*MuscleMass + w2*UpperBodyStrength + w3*LegStrength  (normalizar 0–5)
DEX = w4*MotorSkills + w5*RunningSkill + w6*FineMotorControl (0–5)
CON = w7*Fat + w8*Stamina + w9*ConstitutionRaw              (0–5)
INT = (se disponível) w10*Knowledge + w11*MapMem + w12*DexterityCoupling
    (senão usar default INT_default em config, p.ex. 2.5)
```

**Normalização**: Após cálculo, **clamp** para `0.0–5.0`.  
**Weights default** (se não houver `weights.json`):
- `STR: MuscleMass 0.4, Upper 0.3, Leg 0.3`
- `DEX: MotorSkills 1.0`
- `CON: Fat 0.5, Stamina 0.3, ConstitutionRaw 0.2`
- `INT: constante 2.5`

### 3.3 Reaprendizado (“Reaprender”)
- Coleta amostras do próprio DB (componentes dos jogadores).
- Gera matriz X (features) e y (targets estimados via regras do jogo ou valores médios registrados).
- Resolve **OLS** (equações normais) implementadas manualmente (sem libs externas):
  - `θ = (XᵀX)⁻¹ Xᵀ y`
- Persiste pesos em `resources/model/weights.json`.
- Exibe **MAE/RMSE** e **n** de amostras no painel **Relatório do Modelo**.

---

## 4) Inventário (containers recursivos + blobs)

### 4.1 Dois formatos prováveis
1) **XML/Texto comprimido** (já visto em alguns DBs):
   - Detectar zlib → **Inflater** → texto XML com tags como `<ClassName>`, `<StackCount>`, `<Health>`, `<Color>`.
   - Parse via regex/DOM; montar árvore `InventoryNode`.

2) **UE4 BLOB**:
   - Sem texto legível; processar por **floats** (4 bytes) + heurísticas.
   - Config `resources/presets/inventory-mapping.json` com **offsets** por classe (quando conhecidos).
   - Sempre oferecer modo **“Avançado”** para edição manual por offset.

### 4.2 Campos por Item
- `className` (String)
- `quantity` (int)
- `stackSize` (int, opcional)
- `stacksCount` (int, opcional)
- `condition` (float 0–100)
- `color` (RGB em `#RRGGBB` ou 3 ints)
- `children: List<InventoryNode>`

### 4.3 Validações
- **Tipos**:
  - quantity/stackSize/stacksCount ⇒ **int**
  - condition ⇒ **float**
  - color ⇒ **string** com `^#?[0-9A-Fa-f]{6}$` ou 3 ints 0–255
- **Regras cruzadas**:
  - `Quantity ≤ (StacksCount * StackSize)` quando ambos existem.
- **Faixas**:
  - `0 ≤ condition ≤ 100`

### 4.4 Persistência reversa
- XML: atualizar nodos → recomprimir (zlib) → `UPDATE`.
- UE4: atualizar offsets mapeados → recompor BLOB bruto → `UPDATE`.

---

## 5) Veículos & Clãs

### 5.1 Veículos
- Adapter A:
  - Entidades `Vehicle_*` em `entity` (classes variam: ex.: `Vehicle_Wheel_ES`, etc.).  
  - Proprietário via `entity.owning_entity_id` ou componente que guarda Owner/SteamId.  
  - Prover **transferência** de dono e **remoção**.

- Adapter B:
  - `Vehicles( Id, Type, Location, OwnerId )`.
  - Operações via SQL direto.

### 5.2 Clãs
- Adapter A:
  - associação via componentes `Clan*`. Ler blob do **membership**.
- Adapter B:
  - `ClanMembers(MemberId=SteamId, ClanId, Rank)` e `Clans(Id, Name)`.  
  - Operações: **remover do clã**, **alterar rank**, **mover de clã**.

---

## 6) UI: telas e interações (Swing)

### 6.1 App & Frame
- `App.main`: aplica `LoggerConfig.configure()`, cria `MainFrame`.
- `MainFrame`: `JTabbedPane` com tabs: **Jogador**, **Inventário**, **Veículos**, **Clã**, **Presets**, **Avançado (Blobs)**, **Relatório do Modelo**, **Sobre**.  
- Menu: **Arquivo** (Carregar DB, Salvar, Backup), **Editar** (Desfazer Futuro), **Ajuda** (Sobre).

### 6.2 Jogador
- Top: [**Carregar DB**], Combo **Jogadores** (nome + SteamID)
- Campos: **Fame**, **Money**, **Gold**
- Atributos (calc. dinâmico): **STR**, **DEX**, **CON**, **INT**  
- Botões:
  - **Salvar alterações** (Fame/Money/Gold)  
  - **Salvar atributos** (aplica **persistência reversa**, ver §3)  
- Validações: **números**; clamp; logs com MDC (SteamID, PlayerId).

### 6.3 Inventário
- **JTree** com containers recursivos
- Duplo-clique em item ⇒ dialog de edição (`quantity`, `condition`, `color`)
- Botões: **Adicionar**, **Remover**, **Salvar inventário**
- Ao salvar:
  - **Backup automático** do `scum.db` (`.bak-YYYYMMDD-HHMMSS`)
  - Transação `BEGIN IMMEDIATE; ... COMMIT;` (rollback em erro)

### 6.4 Veículos
- Input **SteamID**, botão **Carregar**
- Tabela (ID, Tipo, Localização, Dono)
- Botões: **Transferir** (novo SteamID), **Remover**

### 6.5 Clã
- Input **SteamID**, **Carregar**
- Exibir: **ClanName**, **ClanId**, **Rank**
- Botões: **Remover do clã**, **Alterar rank** (combobox)

### 6.6 Presets
- **Importar** (JSON) → valida tipo/intervalo
- **Exportar** atual (gera JSON)
- **Aplicar ao jogador** (solicita SteamID; usa `AttributeReverser` + updates (Fame/Money/Gold))

### 6.7 Avançado (Blobs)
- Selecionar jogador ⇒ listar componentes (`entity_component`)  
- Ao selecionar componente:
  - Mostrar **hex dump** dos primeiros N bytes
  - Listar **floats heurísticos** (`offset`, `valor`) com editores
  - **Salvar**: escreve nos offsets, atualiza BLOB no DB
  - **Restaurar**: recarrega do DB

### 6.8 Relatório do Modelo
- Mostra **pesos atuais**, **MAE/RMSE**, **n** amostras, data do treino
- **Reaprender**: reavalia pesos usando dados do banco atual

---

## 7) Logs (Log4j2) — rotação diária + tamanho (rollover ativo)

- Arquivo: `logs/app.log` (ao lado do .jar).
- Rollover **diário** e também por **tamanho** (ex.: 5MB), `max=7`.
- Incluir **SteamID** e **PlayerId** via **MDC** quando disponível.
- Exemplo `log4j2.xml`:

```xml
<Configuration status="WARN">
  <Appenders>
    <RollingFile name="LogFile" fileName="logs/app.log"
                 filePattern="logs/app-%d{yyyy-MM-dd}-%i.log.gz">
      <PatternLayout pattern="%d [%t] %-5level %X{steamId} %X{playerId} %logger - %msg%n"/>
      <Policies>
        <TimeBasedTriggeringPolicy/>
        <SizeBasedTriggeringPolicy size="5MB"/>
      </Policies>
      <DefaultRolloverStrategy max="7"/>
    </RollingFile>
    <Console name="Console" target="SYSTEM_OUT">
      <PatternLayout pattern="%d %-5level %logger - %msg%n"/>
    </Console>
  </Appenders>
  <Loggers>
    <Root level="${sys:log.level:-info}">
      <AppenderRef ref="LogFile"/>
      <AppenderRef ref="Console"/>
    </Root>
  </Loggers>
</Configuration>
```

- `LoggerConfig.configure()` deve procurar `log4j2.xml` no **mesmo diretório do .jar** e inicializar o Log4j2.

---

## 8) Persistência segura (backup + transações)

- **Antes de qualquer COMMIT**, criar **backup automático**: `scum.db.bak-YYYYMMDD-HHMMSS`.
- Operações de escrita:
  - `BEGIN IMMEDIATE;`
  - `UPDATE ...` usando **`PreparedStatement`** (sempre!)
  - `COMMIT;`
  - `catch` ⇒ `ROLLBACK;` e log `ERROR`.

- **Atomicidade**: para blobs grandes, considerar `PRAGMA journal_mode=WAL;` (opcional) e/ou gravar em temp, depois substituir.

---

## 9) Validações & regras

### 9.1 Tipos
- `int`: Fame, Money (se inteiro), Gold, Quantity, StackSize, StacksCount, cores RGB.
- `float`: STR, DEX, CON, INT, Condition, Stamina etc.
- `boolean`: flags diversas (se houver), via `0/1`.

### 9.2 Faixas
- `0 ≤ STR/DEX/CON/INT ≤ 5`
- `0 ≤ Condition ≤ 100`
- `0 ≤ Quantity ≤ 1_000_000` (ajuste necessário)
- `0 ≤ Money/Gold` (sem limite superior rígido; validar overflow)

### 9.3 Regras cruzadas
- `Quantity ≤ StacksCount * StackSize` (se ambos existirem).
- `0 ≤ Health ≤ MaxHealth`.

### 9.4 Erros de domínio
- Se `Adapter A` ativo e classe do componente é desconhecida:
  - Permitir somente **edição avançada** por offsets.
  - Bloquear alteração automática de campos não mapeados.

---

## 10) Presets (JSON)

### 10.1 Esquema

```json
{
  "name": "Preset Guerreiro",
  "description": "STR/CON altas, DEX/INT baixas",
  "attributes": { "strength": 4.5, "constitution": 4.2, "dexterity": 2.1, "intelligence": 1.2 },
  "money": 500,
  "fame_points": 200,
  "gold": 50
}
```

- Validar tipos, faixas (atributos entre 0–5).
- **Importar**: carrega JSON e mostra preview.
- **Aplicar**: requer **SteamID** do jogador atual; usa `AttributeReverser` + updates (Fame/Money/Gold).
- **Exportar**: gera JSON do estado atual.

---

## 11) “Reaprender” pesos do modelo

- Serviço `AttributeModelService`:
  1) Coleta features dos componentes (Adapter A) ou proxies (Adapter B).
  2) Monta **X** e **y** (meta: aproximar valores “alvo”; pode-se usar heurística/target default).
  3) Resolve OLS (sem dependências externas).
  4) Persiste `weights.json`.
  5) **Relatório**: MAE, RMSE, variância explicada (R² opcional), nº de amostras.

- UI: **ModelReportPanel**
  - Tabela de pesos, KPIs, botão “Reaprender”.
  - Mostrar data/hora do último treino.

---

## 12) Blobs (UE4) — parsing e edição

### 12.1 Detecção e descompressão
- Se `data` inicia com bytes `0x78 0x9C` ⇒ zlib → **Inflater**.
- Senão, tratar como **raw UE4**.

### 12.2 Estratégias de leitura
1) **Mapeamento conhecido** por `class` do componente:
   - `resources/model/weights.json` (ou `blob-mappings.json`) pode conter offsets:
   ```json
   {
     "MetabolismComponent": { "MuscleMass": 8, "Fat": 4, "UpperBodyStrength": 12, "LegStrength": 16, "Stamina": 20 }
   }
   ```
   - Offsets em **bytes** ou unidades de 4 bytes (documentar convenção).

2) **Heurística de varredura**:
   - Percorrer a cada 4 bytes (`Little Endian`) e converter para `float`.
   - Filtrar por faixas (0–5, 0–10, 0–100, etc.) e apresentar no **BlobsPanel** com **offset**.

### 12.3 Escrita (persistência reversa)
- Ao editar um valor:
  - Converter `float → 4 bytes LE`.
  - Escrever no offset correspondente do array `byte[]`.
  - Se o BLOB original era **comprimido**, recomprimir ao salvar.
- `UPDATE entity_component SET data=? WHERE id=?`.

---

## 13) Build, perfis e execução

### 13.1 Maven
- `maven-shade-plugin` para gerar `*-all.jar`.
- Perfis:
  - `dev` (logs `debug`, ativo por padrão)
  - `prod` (logs `error`, minimizado)

**Exemplo `pom.xml` (trechos principais)**:
```xml
<properties>
  <maven.compiler.source>1.8</maven.compiler.source>
  <maven.compiler.target>1.8</maven.compiler.target>
</properties>

<dependencies>
  <dependency>
    <groupId>org.xerial</groupId>
    <artifactId>sqlite-jdbc</artifactId>
    <version>3.45.1.0</version>
  </dependency>
  <dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.17.2</version>
  </dependency>
  <dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.17.2</version>
  </dependency>
</dependencies>

<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-shade-plugin</artifactId>
      <version>3.2.4</version>
      <executions>
        <execution>
          <phase>package</phase>
          <goals><goal>shade</goal></goals>
          <configuration>
            <transformers>
              <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                <mainClass>com.scumdb.editor.ui.App</mainClass>
              </transformer>
            </transformers>
          </configuration>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>

<profiles>
  <profile>
    <id>prod</id>
    <properties><log.level>error</log.level></properties>
  </profile>
  <profile>
    <id>dev</id>
    <activation><activeByDefault>true</activeByDefault></activation>
    <properties><log.level>debug</log.level></properties>
  </profile>
</profiles>
```

### 13.2 Execução
- `./mvnw -Pprod -DskipTests clean package`
- Resultado: `target/scum-db-edit-1.10.0-all.jar`
- Scripts:
  - `scripts/run-linux.sh`: `java -jar target/scum-db-edit-1.10.0-all.jar`
  - `scripts/run-windows.bat`: idem

---

## 14) GitHub Actions (CI)

`.github/workflows/release.yml` (resumo):
- Gatilhos: push em `main` e `tags: v*`.
- Passos:
  - `actions/setup-java@v4`
  - `./mvnw -Pprod -DskipTests package`
  - `actions/upload-artifact` → anexar `*-all.jar`
  - Em **tags**, criar **release** e anexar `.jar` (usar `softprops/action-gh-release`).

---

## 15) Padrões de código & qualidade

- Java 8, nomes claros, `try-with-resources` para JDBC.
- **PreparedStatement** sempre, nada de concatenação de SQL.
- **Camadas**: UI → Service → DAO/Adapter.
- **Logs**: nível apropriado; contexto MDC (`steamId`, `playerId`).
- **Validações** centralizadas (`Validation`).
- **Erros**: mensagens amigáveis na UI + logs técnicos.

---

## 16) Testes (JUnit 5)

- `AttributeModelServiceTest`: normalização, clamp, OLS em dataset pequeno.
- `BlobServiceTest`: leitura/escrita de floats em offsets (round-trip).
- `InventoryServiceTest`: validações de `Quantity` vs `StacksCount*StackSize`; XML parse.
- `AdapterDetectorTest`: seleção de adapter por `sqlite_master`.

---

## 17) Pseudo-código & trechos críticos

### 17.1 Adapter detector
```java
boolean hasEntity = tableExists("entity");
boolean hasComponent = tableExists("entity_component");
boolean hasCharacters = tableExists("Characters");
if (hasEntity && hasComponent) use AdapterA_EntityBased;
else if (hasCharacters) use AdapterB_ClassicTables;
else throw new IllegalStateException("Esquema não suportado");
```

### 17.2 Leitura de floats no BLOB
```java
float readFloatLE(byte[] buf, int offset) {
  int i = (buf[offset] & 0xFF)
        | ((buf[offset+1] & 0xFF) << 8)
        | ((buf[offset+2] & 0xFF) << 16)
        | ((buf[offset+3] & 0xFF) << 24);
  return Float.intBitsToFloat(i);
}
```

### 17.3 Escrita de floats no BLOB
```java
void writeFloatLE(byte[] buf, int offset, float value) {
  int i = Float.floatToIntBits(value);
  buf[offset]   = (byte)( i        & 0xFF);
  buf[offset+1] = (byte)((i >> 8)  & 0xFF);
  buf[offset+2] = (byte)((i >> 16) & 0xFF);
  buf[offset+3] = (byte)((i >> 24) & 0xFF);
}
```

### 17.4 Compressão/Descompressão (zlib)
```java
byte[] inflate(byte[] data);
byte[] deflate(byte[] plain);
```

### 17.5 Transação & backup
```java
backup(scum.db, "scum.db.bak-YYYYMMDD-HHMMSS");
conn.setAutoCommit(false);
// do updates...
conn.commit();
```

---

## 18) Sobre/Help
- Descrever campos exibidos em cada aba, valores possíveis e validações.
- Explicar **risco** de editar blobs avançados.
- FAQ: erros comuns, como restaurar backup, etc.

---

## 19) Autor & créditos
- Autor do app: **Iago Daflon**  
- Incluir no `README.md` e em **Sobre** na UI.

---

## 20) Aceite / critérios de “pronto”
- App abre `scum.db` local do repo.
- Lista jogadores (Adapter A/B conforme o banco).
- Calcula e mostra STR/DEX/CON/INT; permite editar e **persistir** reverso.
- Inventário com containers recursivos; editar `quantity/condition/color`, salvar no DB.
- Veículos: listar, transferir, remover.
- Clã: visualizar, remover vínculo, alterar rank.
- Presets: importar/exportar/aplicar.
- Avançado (Blobs): listar componentes, editar floats por offset, salvar.
- Logs com rotação diária + tamanho; backup antes de commit.
- `mvn -Pprod package` gera `.jar` executável.
- CI gera release com `.jar` em tag.
