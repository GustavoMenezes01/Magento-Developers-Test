# Pegadinhas & Detalhes de Prova

> Tópicos que parecem simples mas têm uma resposta "quase certa" errada. Leia antes do exame.

---

## di.xml — Lida com Dados Sensíveis?

> **Não.** `di.xml` é configuração de **Dependency Injection** — apenas define classes, plugins, preferences e argumentos de construtor.

| Ficheiro | O que guarda | Sensível? |
|---|---|---|
| `app/etc/env.php` | DB credentials, chaves criptográficas, Redis host/pass | **Sim** — fora do git |
| `app/etc/config.php` | Módulos habilitados, estado de configuração | Não — pode estar no git |
| `app/etc/di.xml` | **Não existe como ficheiro isolado** em `app/etc/` — DI fica em `app/code/Vendor/Module/etc/di.xml` | Não |
| `etc/di.xml` (módulo) | Plugins, preferences, virtual types, arguments | Não — nenhum dado sensível |

---

## addAttribute() — Parâmetros Exatos

Ao criar atributo de cliente via `CustomerSetup::addAttribute()`, os nomes das chaves importam:

```php
$customerSetup->addAttribute('customer', 'custom_field', [
    'type'           => 'varchar',        // tipo de coluna EAV
    'label'          => 'Custom Field',
    'input'          => 'text',           // frontend input type
    'required'       => false,
    'visible'        => true,             // visível nos formulários do ADMIN
    'visible_on_front' => true,           // visível no frontend (customer account)
    'user_defined'   => true,
    'position'       => 999,
    'system'         => false,
]);
```

| Chave | Efeito | Armadilha |
|---|---|---|
| `visible` | Aparece nos formulários do **Admin** | Não afeta o frontend |
| **`visible_on_front`** | Aparece nas páginas de conta do **cliente** | O nome correto — não é `use_on_front` nem `view_in_front` |
| `user_defined` | Permite que seja editado/removido pelo admin | Sistema não pode deletar se `false` |
| `system` | Se `true`, o Magento trata como atributo de sistema | Atributos de sistema não aparecem no admin como editáveis |

> `visible_on_front` — guarda este nome. Variações `use_on_front`, `show_on_front`, `view_in_front` **não existem**.

---

## Plugin — Atributos Válidos em di.xml

```xml
<type name="Some\Class">
    <plugin name="my_plugin"
            type="Vendor\Module\Plugin\MyPlugin"
            sortOrder="10"
            disabled="false"/>
</type>
```

| Atributo | Válido? | Notas |
|---|---|---|
| `name` | ✅ | Identificador único — obrigatório |
| `type` | ✅ | FQCN da classe do plugin — obrigatório |
| `sortOrder` | ✅ | Ordem entre múltiplos plugins |
| `disabled` | ✅ | `"true"` desativa completamente (DI skips) |
| ~~`active`~~ | ❌ | Não existe |
| ~~`status`~~ | ❌ | Não existe |
| ~~`enabled`~~ | ❌ | Não existe |

---

## module.xml — Sintaxe Exata

```xml
<!-- CORRETO -->
<module name="Vendor_Module">
    <sequence>
        <module name="Magento_Catalog"/>  <!-- carrega Catalog ANTES deste -->
    </sequence>
</module>

<!-- ERRADO — <before> não existe dentro de <sequence> -->
<sequence>
    <before name="Magento_Catalog"/>  ← inválido, ignorado silenciosamente
</sequence>

<!-- ERRADO — before/after como atributo do <module> não existe -->
<module name="Vendor_Module" before="Magento_Catalog"/>  ← inválido
```

> `<sequence>` lista módulos que devem ser carregados **ANTES** do atual. Contém `<module name="...">`, não `<before>` nem `<after>`.

> Se a sintaxe `<before name="..."/>` for usada por engano, o Magento **ignora silenciosamente** — não gera erro fatal.

---

## events.xml vs observer.xml vs event.xml

| Ficheiro | Existe? |
|---|---|
| `etc/events.xml` | ✅ Correto — plural |
| `etc/frontend/events.xml` | ✅ Correto — scoped |
| `etc/adminhtml/events.xml` | ✅ Correto — scoped |
| ~~`etc/event.xml`~~ | ❌ Singular — não funciona |
| ~~`etc/observer.xml`~~ | ❌ Não existe |

---

## system.xml vs config.xml — Diferença Crítica

| Ficheiro | O que define | Armadilha |
|---|---|---|
| `etc/adminhtml/system.xml` | **Estrutura** (sections, groups, fields, labels, tipos) | Não define valores padrão |
| `etc/config.xml` | **Valores padrão** dos campos | Não define estrutura |
| ~~`etc/adminhtml/config.xml`~~ | **Não existe** | Pegadinha de exame |
| ~~`etc/system.xml`~~ | **Não existe** (fora de adminhtml) | Pegadinha de exame |

```xml
<!-- etc/config.xml — valores padrão -->
<config>
    <default>
        <my_section>
            <general>
                <enabled>1</enabled>
            </general>
        </my_section>
    </default>
</config>
```

---

## JS Translation — Funções Exatas

| Função | Oficial no Magento? |
|---|---|
| `$.mage.__('text')` | ✅ **Única função oficial** documentada |
| `$.t('text')` | ❌ Não existe no core |
| `$translate('text')` | ❌ Não existe no core |
| `Magento.__('text')` | ❌ Não existe |
| `Magento.translate('text')` | ❌ Não existe |
| `window.translate('text')` | ❌ Não existe |
| `global.translate('text')` | ❌ Não existe |

> `$t` e `$translate` podem aparecer em projetos como aliases customizados de `mage/translate`, mas **não são funções oficiais** e não integram com o processo de extração de frases.

---

## cron:install vs cron:run

| Comando | O que faz |
|---|---|
| `bin/magento cron:install` | Adiciona jobs ao **crontab do servidor** dentro de marcadores `#~ MAGENTO START` / `#~ MAGENTO END` |
| `bin/magento cron:run` | **Executa** os jobs pendentes imediatamente |
| `bin/magento cron:remove` | Remove as entradas MAGENTO do crontab |

> `cron:install` **preserva** todos os cron jobs existentes fora dos marcadores MAGENTO.
> `cron:install --mode=update` atualiza as entradas dentro dos marcadores sem tocar no resto.

---

## Cloud CLI — Comandos Exatos

| Operação | Comando correto | Armadilha |
|---|---|---|
| Criar backup | `magento-cloud snapshot:create` | `environment:backup` **não existe** |
| Comando incompleto | ~~`magento-cloud environment:snapshot`~~ | Falta o verbo `create` |
| Listar snapshots | `magento-cloud snapshot:list` | — |

---

## Diretórios Cloud — Read-only vs Writable

| Dir | Estado | Prova: "writable em runtime?" | Prova: "read-only após deploy?" |
|---|---|---|---|
| `app/code` | Read-only | ❌ | ✅ |
| `app/design` | Read-only | ❌ | ✅ |
| `pub/static` | Writable | ✅ | ❌ |
| `pub/media` | Writable | ✅ | ❌ |
| `var` | Writable | ✅ | ❌ |
| `generated` | Writable | ✅ | ❌ |
| `/tmp` | Writable | ✅ | ❌ |

> **Resposta "writable during runtime":** `var, pub/static, pub/media, /tmp`
> **Resposta "read-only after deployment":** `app/code, app/design`

---

## Starter vs Pro — Número de Environments

| Plano | Integration Environments |
|---|---|
| Starter | **Máximo 2** ativos para desenvolvimento |
| Pro | **Ilimitados** para desenvolvimento paralelo |

---

## Cloud Tech Stack — Componentes Certos

| Função | Componente correto | Armadilhas |
|---|---|---|
| CDN | **Fastly** | ≠ Akamai |
| Web server | **NGINX** | ≠ Apache |
| File storage distribuído | **GlusterFS** | ≠ NFS |
| Cache / Sessions | **Redis** | ≠ Memcached |
| DB cluster HA | **Galera (MySQL Galera Cluster)** | ≠ Redis Cluster |

---

## DI Scope — Area-Specific Override

| Ficheiro | Aplica em |
|---|---|
| `etc/di.xml` | **Todas** as áreas (global) |
| `etc/frontend/di.xml` | Só **frontend** — sobrescreve global |
| `etc/adminhtml/di.xml` | Só **admin** — sobrescreve global |

> Area-specific **sempre** sobrescreve global para o mesmo elemento.

---

## Indexers — Modos Suportados

| Indexer | Update on Save | Update by Schedule |
|---|---|---|
| `catalog_product_price` | ✅ | ✅ |
| `catalogsearch_fulltext` | ✅ | ✅ |
| `sales_order_grid` | ✅ | ✅ |
| **`customer_grid`** | ✅ | ❌ **Apenas Update on Save** |

---

## Magento_Indexer vs Mview

| Componente | Responsabilidade |
|---|---|
| `Magento_Indexer` | Gestão global: declarar indexers, CLI `indexer:*`, verificar status |
| `Magento\Framework\Mview` | **Materialized views** e **database triggers** para rastrear mudanças (suporte ao Update by Schedule) |

---

## Layout XML — Naming vs Diretório

```
view/frontend/layout/checkout_index_index.xml   → área = frontend (pelo dir)
view/adminhtml/layout/sales_order_index.xml     → área = adminhtml (pelo dir)
```

> A **área** é determinada pelo **diretório** (`frontend/` vs `adminhtml/`), não pelo nome do ficheiro.
> O nome do ficheiro = `frontName_controller_action.xml`

---

## UI Component — Nome do Ficheiro = Nome do Componente

```xml
<!-- layout XML referencia: -->
<uiComponent name="product_export_grid"/>

<!-- ficheiro DEVE se chamar exatamente: -->
view/adminhtml/ui_component/product_export_grid.xml
```

> Se o ficheiro estiver no diretório errado, Magento simplesmente não encontra — não gera erro imediato.

---

## EAV vs Extension Attributes

| | EAV | Extension Attributes |
|---|---|---|
| Tipos | Primitivos (string, int, decimal, datetime) | **Arrays e objetos** |
| Onde usar | Admin UI, produto/cliente/categoria | **Service contracts e APIs** |
| Limitação EAV | **Só primitivos** | — |

---

## Scoping Rules — system.xml

> **Child não pode ser mais restritivo que parent.**

```xml
<!-- ERRADO: section mostra em Default, mas field não mostra -->
<section showInDefault="1">
    <group showInDefault="1">
        <field showInDefault="0" showInWebsite="1"/>  ← child mais restritivo = problema
    </group>
</section>

<!-- CORRETO para "apenas website" — TODOS os níveis devem ter o mesmo scope -->
<section showInDefault="0" showInWebsite="1" showInStore="0">
    <group showInDefault="0" showInWebsite="1" showInStore="0">
        <field showInDefault="0" showInWebsite="1" showInStore="0"/>
    </group>
</section>
```

---

## Vendor vs app/code

| Situação | Diretório |
|---|---|
| Módulo instalado via **Composer** | `vendor/<vendor>/<module>` |
| Módulo criado/instalado **manualmente** | `app/code/<Vendor>/<Module>` |

---

## Ficheiros que NÃO Existem no Magento 2

| Ficheiro | Confusão |
|---|---|
| `app/etc/config.xml` | Existe no M1, **não no M2** |
| `etc/adminhtml/config.xml` | Parece certo mas não existe |
| `etc/system.xml` (fora de adminhtml) | Deve estar em `etc/adminhtml/system.xml` |
| `etc/event.xml` | Singular — deve ser `events.xml` |
| `etc/observer.xml` | Não existe |
| `magento-cloud environment:backup` | Comando que não existe — usar `snapshot:create` |
| `admin/index.php` | Não existe — entry point é `pub/index.php` |

---

## Cache: clean vs flush

| Comando | O que faz | Quando usar |
|---|---|---|
| `cache:clean` | Invalida entradas por **tag** — storage permanece | Produção (seguro com Redis compartilhado) |
| `cache:flush` | **Apaga todo o storage** | Dev, deploys isolados |

> Em produção com Redis compartilhado, `cache:flush` pode afetar outros processos — prefira `cache:clean`.

---

## Plugin `around` — Argumentos do Método Original (Armadilha Silenciosa)

O `around` plugin recebe o `$subject`, o `$proceed` **e depois os argumentos originais do método**.  
Se o método interceptado tiver argumentos, você **deve** declará-los e repassá-los para `$proceed()`.

```php
// Método original: public function execute(int $orderId, string $comment): bool

// ERRADO — omite os args → $proceed() não recebe nada → bug silencioso
public function aroundExecute(MyClass $subject, callable $proceed): mixed
{
    return $proceed(); // orderId e comment perdidos!
}

// CORRETO
public function aroundExecute(
    MyClass $subject,
    callable $proceed,
    int $orderId,     // <- argumento original
    string $comment   // <- argumento original
): mixed {
    // lógica antes
    $result = $proceed($orderId, $comment); // <- repassa ao método original
    // lógica depois
    return $result;
}
```

> **Regra:** O `$proceed()` deve receber os mesmos argumentos que o método original receberia. Esquecer isso não gera erro — o método original simplesmente recebe valores errados ou nulos.

---

## Plugin `around` — Não Chamar `$proceed()`

Se `$proceed()` **não for chamado**, o método original **nunca executa**. Isso é intencional para short-circuit, mas catastrófico se esquecido:

```php
// Se você omitir $proceed(), o método original é silenciosamente pulado
public function aroundSave(Product $subject, callable $proceed): mixed
{
    if ($this->shouldSkip()) {
        return null; // método original nunca roda — use com intenção
    }
    return $proceed(); // normal: chama o original
}
```

---

## Plugin `before` — Retornar `null` vs `array`

| Retorno | Efeito |
|---|---|
| `null` | Argumentos **não são modificados** — original recebe o que foi passado |
| `array` | Os valores do array **substituem** os argumentos do método |

```php
// Retornar null = não alterar
public function beforeSetName(Product $subject, string $name): ?array
{
    if (!$this->shouldTransform()) {
        return null; // deixa o $name original passar
    }
    return [strtoupper($name)]; // substitui o argumento
}
```

> **Atenção:** Mesmo que o método tenha apenas 1 argumento, o retorno deve ser um `array`, não um scalar. `return $name` é errado — Magento espera `return [$name]`.

---

## Plugin em Interface — Permitido

Você **pode** criar um plugin diretamente em uma **interface**:

```xml
<type name="Magento\Catalog\Api\ProductRepositoryInterface">
    <plugin name="my_plugin" type="Vendor\Module\Plugin\ProductRepositoryPlugin"/>
</type>
```

O plugin intercepta **todas as implementações** daquela interface que estejam registradas via Preference. Isso é mais robusto do que plugar na implementação diretamente.

---

## SearchCriteria — AND vs OR

Múltiplos `addFilter()` encadeados = condição **AND**.  
Para condição **OR**, os filtros devem estar no mesmo **FilterGroup**.

```php
// AND — produto com status=1 E visibility=4
$criteria = $this->searchCriteriaBuilder
    ->addFilter('status', 1)
    ->addFilter('visibility', 4)
    ->create();

// OR — produto com status=1 OU visibility=4
$filterA = $this->filterBuilder->setField('status')->setValue(1)->setConditionType('eq')->create();
$filterB = $this->filterBuilder->setField('visibility')->setValue(4)->setConditionType('eq')->create();
$group   = $this->filterGroupBuilder->setFilters([$filterA, $filterB])->create();
$criteria = $this->searchCriteriaBuilder->setFilterGroups([$group])->create();
```

> **Regra:** filtros em `FilterGroup` diferentes = AND entre grupos. Filtros no mesmo `FilterGroup` = OR entre eles.

---

## Factory e Proxy — Auto-gerados, sem di.xml

**Factory** e **Proxy** são gerados automaticamente pelo `setup:di:compile`.  
Você **não precisa declarar nada em `di.xml`** — basta type-hintar a classe com o sufixo correto.

| Sufixo | O que faz | Quando usar |
|---|---|---|
| `ClassNameFactory` | Cria novas instâncias de `ClassName` | Quando precisa de várias instâncias ou instâncias dentro de loops |
| `ClassNameProxy` | Instanciação lazy — atrasa até o primeiro uso | Quando a dependência é pesada e pode não ser usada |

```php
public function __construct(
    private readonly ProductInterfaceFactory $productFactory, // cria Product
    private readonly ProductRepositoryProxy $repositoryProxy  // lazy load
) {}
```

> **Armadilha:** `ClassNameFactory` vs `new ClassName()` — nunca use `new` para classes injetáveis. Use Factory.

---

## Custom Order Status vs Custom Order State

| | Status | State |
|---|---|---|
| O que é | Rótulo visível configurável | Estado interno do sistema |
| Pode adicionar customizado? | ✅ Sim — Admin → Stores → Order Status | ❌ Não (sem override profundo) |
| Quantidade no core | Ilimitado | ~8 valores fixos |
| Relação | Muitos status → um state | Um state → muitos status |

```
State "processing" (fixo)
├── status "processing"      ← padrão
├── status "awaiting_erp"    ← customizado (pode adicionar)
└── status "payment_review"  ← customizado (pode adicionar)
```

> **Armadilha do exame:** "O dev quer adicionar um status personalizado" → **Status** (sim, possível via admin). "O dev quer adicionar um state personalizado" → não é suportado out-of-the-box.

---

## `mview.xml` — Obrigatório para "Update by Schedule" em Indexer Customizado

Para que um indexer customizado suporte o modo **"Update by Schedule"**, você precisa de DOIS arquivos:

- `etc/indexer.xml` — declara o indexer
- `etc/mview.xml` — declara os triggers de banco para rastrear mudanças

Sem `mview.xml`, o indexer roda apenas em "Update on Save" ou via `indexer:reindex` manual.

```xml
<!-- etc/mview.xml -->
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Mview/etc/mview.xsd">
    <view id="vendor_module_view"
          class="Vendor\Module\Model\Indexer\MyIndexer"
          group="indexer">
        <subscriptions>
            <!-- rastreia mudanças nesta tabela -->
            <table name="vendor_module_entity" entity_column="entity_id"/>
        </subscriptions>
    </view>
</config>
```

> O `view_id` em `indexer.xml` deve ser igual ao `id` em `mview.xml`.

---

## `extension_attributes.xml` — Localização Correta

`extension_attributes.xml` fica em `etc/` — **não** é scoped para `etc/frontend/` ou `etc/adminhtml/`.

```
etc/
└── extension_attributes.xml   ← CORRETO (global)

etc/frontend/
└── extension_attributes.xml   ← NÃO EXISTE / não funciona

etc/adminhtml/
└── extension_attributes.xml   ← NÃO EXISTE / não funciona
```

```xml
<!-- etc/extension_attributes.xml -->
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Api/etc/extension_attributes.xsd">
    <extension_attributes for="Magento\Sales\Api\Data\OrderInterface">
        <attribute code="custom_field" type="string"/>
    </extension_attributes>
</config>
```

---

## Cenários "O dev quer..." — Mecanismo Correto

| O dev quer... | Mecanismo |
|---|---|
| Modificar argumento de um método público | Plugin `before` |
| Modificar retorno de um método público | Plugin `after` |
| Substituir ou condicionar chamada de método | Plugin `around` |
| Modificar método `final`, `private` ou `static` | Preference (último recurso) |
| Criar múltiplas instâncias de uma classe injetável | Factory (`ClassNameFactory`) |
| Evitar instanciação de dependência pesada e raramente usada | Proxy (`ClassNameProxy`) |
| Reagir a um evento sem alterar o fluxo | Observer |
| Adicionar config no Admin com valor padrão | `system.xml` + `config.xml` |
| Adicionar total/fee ao carrinho | `sales.xml` + classe que estende `AbstractTotal` |
| Criar rota no frontend | `etc/frontend/routes.xml` + Controller |
| Criar rota no Admin | `etc/adminhtml/routes.xml` + Controller (`extends Backend\App\Action`) |
| Rodar código SQL uma vez no deploy | Data Patch (`DataPatchInterface`) |
| Criar tabela customizada | `db_schema.xml` + `generate-whitelist` |
| Indexer com "Update by Schedule" | `indexer.xml` + `mview.xml` |
| Expor campo customizado na API REST | `extension_attributes.xml` |
| Criar um CLI command | `di.xml` (CommandList) + classe que estende `Command` |

---

## Crontab — `<schedule>` hardcoded vs `<config_path>`

O schedule de um cron job pode vir de dois lugares:

```xml
<!-- Hardcoded — schedule fixo no XML -->
<job name="vendor_job" instance="..." method="execute">
    <schedule>0 2 * * *</schedule>
</job>

<!-- Via config path — admin pode alterar o schedule -->
<job name="vendor_job" instance="..." method="execute">
    <config_path>vendor_module/cron/schedule</config_path>
</job>
```

> Se usar `<config_path>`, o valor do schedule vem de `core_config_data` (configurável no admin via `system.xml`).  
> Se usar `<schedule>`, o schedule é fixo e não pode ser alterado sem editar o XML.

---

## Configurable Product — Requisitos do Super Attribute

Para um atributo ser usado como opção de variação (super attribute) em produto Configurable:

| Requisito | Valor correto | Armadilha |
|---|---|---|
| `scope` | **Global** (`is_global = 1`) | Scope Website ou Store View → não aparece como opção |
| `input_type` | **`select`** | `multiselect`, `text`, `boolean` não funcionam como super attribute |
| `frontend_input` | `select` | `visual_swatch` e `text_swatch` também funcionam |

```php
// Constante para scope global
\Magento\Eav\Model\Entity\Attribute\ScopedAttributeInterface::SCOPE_GLOBAL // = 1
```

> **Armadilha:** criar atributo com scope "Store View" e tentar usá-lo como variação de Configurable → o campo não aparece na tela de configuração do produto.
