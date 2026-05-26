# DB & Cache

> **Domínio 1 — Arquitetura (52%)** &nbsp;·&nbsp; Seções 1.5 – 1.10

---

## Indexers

### Conceito

Indexers transformam dados do formato normalizado (EAV) para formato flat/otimizado para leitura rápida. Sem indexação, cada página de produto exigiria queries complexas em tempo real.

### Modos de Indexação

| Modo | Quando atualiza | Uso ideal |
|---|---|---|
| **Update on Save** | Imediatamente ao salvar a entidade | Catálogos pequenos |
| **Update by Schedule** | Via CRON periodicamente | Catálogos grandes, edição frequente |

```bash
# Mudar modo de um indexer específico
bin/magento indexer:set-mode schedule catalog_product_price
bin/magento indexer:set-mode realtime catalog_category_product
```

### Indexers Principais

| Indexer | O que indexa | Modo suportado |
|---|---|---|
| `catalog_category_product` | Relação categoria → produto | Ambos |
| `catalog_product_category` | Relação produto → categoria | Ambos |
| `catalog_product_price` | Preços calculados | Ambos |
| `catalog_product_attribute` | Atributos EAV flat | Ambos |
| `catalogsearch_fulltext` | Índice de busca | Ambos |
| `catalogrule_rule` | Regras de preço de catálogo | Ambos |
| `catalogrule_product` | Produtos afetados por regras | Ambos |
| `sales_order_grid` | Grid de pedidos no Admin | Ambos |
| **`customer_grid`** | **Grid de customers no Admin** | **Update on Save apenas** |
| `inventory` | Estoque multi-source | Ambos |

> **`customer_grid`** é o único indexer que suporta **apenas "Update on Save"** — não suporta "Update by Schedule". Pergunta frequente no exame.

---

## Magento_Indexer vs Magento\\Framework\\Mview

| Componente | O que faz |
|---|---|
| **`Magento_Indexer`** | Módulo que gerencia o processo de indexação: declarar indexers, executar reindex, verificar status, comandos CLI `bin/magento indexer:*` |
| **`Magento\Framework\Mview`** | Gerencia **materialized views** e **database triggers** que rastreiam mudanças em entidades para suportar updates agendados (Update by Schedule) |

> `Magento_Indexer` = o gestor global. `Mview` = o mecanismo de rastreamento de mudanças para indexação agendada.

### Declarar Indexer Customizado

Para "Update by Schedule" funcionar, são necessários **dois arquivos**: `indexer.xml` e `mview.xml`.

```xml
<!-- etc/indexer.xml -->
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Indexer/etc/indexer.xsd">
    <indexer id="vendor_module_index"
             view_id="vendor_module_view"   <!-- deve coincidir com id em mview.xml -->
             class="Vendor\Module\Model\Indexer\MyIndexer"
             primary="id">
        <title translate="true">My Custom Index</title>
        <description translate="true">Indexer description</description>
    </indexer>
</config>
```

```xml
<!-- etc/mview.xml — obrigatório para "Update by Schedule" -->
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Mview/etc/mview.xsd">
    <view id="vendor_module_view"
          class="Vendor\Module\Model\Indexer\MyIndexer"
          group="indexer">
        <subscriptions>
            <!-- cria trigger nesta tabela para rastrear mudanças -->
            <table name="vendor_module_entity" entity_column="entity_id"/>
        </subscriptions>
    </view>
</config>
```

> Sem `mview.xml`, o indexer só funciona em "Update on Save" ou via `indexer:reindex` manual. O `mview` cria triggers no banco para detectar mudanças automaticamente.

---

## Tipos de Cache

| Cache type | Tag | O que armazena |
|---|---|---|
| `config` | `CONFIG` | Configurações do sistema |
| `layout` | `LAYOUT_GENERAL_CACHE_TAG` | XML de layouts compilados |
| `block_html` | `BLOCK_HTML` | HTML de blocos individuais |
| `collections` | `COLLECTION_DATA` | Resultados de coleções |
| `reflection` | `REFLECTION` | Reflexão de classes PHP |
| `db_ddl` | `DB_DDL` | Schema do banco de dados |
| `compiled_config` | — | Configurações compiladas |
| `full_page` | `FPC` | Páginas inteiras (FPC) |
| `translate` | `TRANSLATE` | Strings de tradução |
| `eav` | `EAV` | Metadados de atributos EAV |

### cache:clean vs cache:flush

| Comando | O que faz | Quando usar |
|---|---|---|
| `cache:clean` | Invalida entradas por tag — storage permanece | Produção (seguro com Redis compartilhado) |
| `cache:flush` | **Apaga todo o storage** de cache | Dev, deploys isolados |

---

## Backends de Cache

| Backend | Quando usar |
|---|---|
| **File** | Dev local (padrão) |
| **Redis** | Produção — compartilhado entre nós, persistente |
| **Memcached** | Alternativa ao Redis |
| **Varnish** | Full-page cache em produção (proxy reverso) |

### Cache em Bloco Customizado

```php
protected function _construct(): void
{
    $this->addData([
        'cache_lifetime' => 86400,
        'cache_tags'     => [\Magento\Catalog\Model\Product::CACHE_TAG],
        'cache_key'      => 'my_block_' . $this->getProductId(),
    ]);
}
```

---

## EAV e Database

### O que é EAV

Entity-Attribute-Value é o modelo de dados usado por **produto, categoria e cliente**. Em vez de uma coluna por atributo, há tabelas separadas por tipo de dado.

**Tabelas EAV de produto:**

| Tabela | Tipo de valor |
|---|---|
| `catalog_product_entity_varchar` | Texto (até 255 chars) |
| `catalog_product_entity_int` | Inteiros, booleans, selects |
| `catalog_product_entity_decimal` | Decimais (preços) |
| `catalog_product_entity_datetime` | Datas |
| `catalog_product_entity_text` | Textos longos |

**Entidades EAV principais:**
- `catalog_product_entity`
- `catalog_category_entity`
- `customer_entity`

---

## Declarative Schema

Forma moderna de definir e alterar estrutura de banco de dados. O Magento compara o estado declarado com o estado atual e aplica apenas as diferenças.

```xml
<!-- etc/db_schema.xml -->
<schema xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Setup/Declaration/Schema/etc/schema.xsd">
    <table name="vendor_module_entity" resource="default"
           engine="innodb" comment="My Entity">
        <column xsi:type="int"       name="entity_id"  unsigned="true" nullable="false" identity="true" comment="Entity ID"/>
        <column xsi:type="varchar"   name="name"       nullable="false" length="255"    comment="Name"/>
        <column xsi:type="smallint"  name="status"     nullable="false" default="1"     comment="Status"/>
        <column xsi:type="timestamp" name="created_at" nullable="false" default="CURRENT_TIMESTAMP" comment="Created At"/>
        <constraint xsi:type="primary" referenceId="PRIMARY">
            <column name="entity_id"/>
        </constraint>
        <index referenceId="VENDOR_MODULE_ENTITY_NAME" indexType="btree">
            <column name="name"/>
        </index>
    </table>
</schema>
```

```bash
# Obrigatório após criar/alterar db_schema.xml
bin/magento setup:db-declaration:generate-whitelist --module-name=Vendor_Module
bin/magento setup:upgrade
```

---

## Data Patches

Patches de dados são executados **uma única vez** e registrados na tabela `patch_list`. Substituem os antigos `InstallData` e `UpgradeData`.

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Setup\Patch\Data;

use Magento\Framework\Setup\ModuleDataSetupInterface;
use Magento\Framework\Setup\Patch\DataPatchInterface;

class AddInitialData implements DataPatchInterface
{
    public function __construct(
        private readonly ModuleDataSetupInterface $moduleDataSetup
    ) {}

    public function apply(): self
    {
        $this->moduleDataSetup->startSetup();

        $this->moduleDataSetup->getConnection()->insertMultiple(
            $this->moduleDataSetup->getTable('vendor_module_entity'),
            [
                ['name' => 'Item A', 'status' => 1],
                ['name' => 'Item B', 'status' => 1],
            ]
        );

        $this->moduleDataSetup->endSetup();
        return $this;
    }

    public static function getDependencies(): array
    {
        return []; // outros patches que precisam rodar antes
    }

    public function getAliases(): array
    {
        return [];
    }
}
```

---

## Service Contracts

Interfaces PHP que definem o comportamento público de um módulo, isolando a implementação interna.

```
Api/
├── Data/
│   ├── ProductInterface.php               ← Data Object Interface
│   └── ProductSearchResultsInterface.php
└── ProductRepositoryInterface.php         ← Repository Interface
```

### Repository Interface Típica

```php
interface ProductRepositoryInterface
{
    public function get(string $sku): ProductInterface;
    public function getById(int $productId): ProductInterface;
    public function save(ProductInterface $product): ProductInterface;
    public function delete(ProductInterface $product): bool;
    public function deleteById(string $sku): bool;
    public function getList(SearchCriteriaInterface $searchCriteria): ProductSearchResultsInterface;
}
```

---

## SearchCriteria

```php
$searchCriteria = $this->searchCriteriaBuilder
    ->addFilter('status', 1)
    ->addFilter('visibility', [2, 4], 'in')
    ->setPageSize(20)
    ->setCurrentPage(1)
    ->addSortOrder(
        $this->sortOrderBuilder
            ->setField('name')
            ->setAscendingDirection()
            ->create()
    )
    ->create();

$results = $this->productRepository->getList($searchCriteria);
$products = $results->getItems();
$total    = $results->getTotalCount();
```

---

## Hierarquia de Store

```
Website (website_id)
└── Store / Store Group (group_id)
    └── Store View (store_id)
```

| Nível | Define |
|---|---|
| **Website** | Domínio, moeda base, compartilha clientes |
| **Store/Group** | Catálogo raiz, grupo de checkout |
| **Store View** | Idioma, localização — o que o cliente vê |

---

## Escopos de Configuração

| Escopo | Prioridade | Sobrescreve |
|---|---|---|
| Global | Baixa (fallback) | — |
| Website | Média | Global |
| Store View | Alta | Global + Website |

---

## Traduções

**Hierarquia de prioridade (maior sobrescreve menor):**

1. Banco de dados (via Translation widget no Admin) — maior prioridade
2. `app/design/frontend/Vendor/theme/i18n/pt_BR.csv` — tema
3. `app/code/Vendor/Module/i18n/pt_BR.csv` — módulo
4. `vendor/package/i18n/pt_BR.csv` — pacote Composer

```csv
"Add to Cart","Adicionar ao Carrinho"
"My Account","Minha Conta"
"Could not save the record: %1","Não foi possível salvar o registro: %1"
```

```bash
bin/magento setup:static-content:deploy pt_BR -f
```

---

## URL Rewrites

A tabela `url_rewrite` mapeia URLs amigáveis para rotas internas.

| Coluna | Descrição |
|---|---|
| `request_path` | URL amigável: `produto/meu-produto.html` |
| `target_path` | Rota interna: `catalog/product/view/id/42` |
| `redirect_type` | `0` = sem redirect, `301`, `302` |
| `entity_type` | `product`, `category`, `cms-page` |
| `store_id` | Scope da URL |
