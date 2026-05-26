# Adobe Commerce Developer Professional — AD0-E724
## Guia de Estudos Completo

> **Exame:** AD0-E724 | **Questões:** 50 | **Tempo:** 100 min | **Aprovação:** 39/50 (78%) | **Custo:** $125

---

## Estrutura do Exame

| Domínio | Peso | ~Questões |
|---|---|---|
| 1 — Arquitetura | 52% | ~26 |
| 2 — Customizações | 36% | ~18 |
| 3 — Cloud | 12% | ~6 |

---

# DOMÍNIO 1 — ARQUITETURA (52%)

## 1.1 Estrutura de Módulos e CLI

### Estrutura de pastas de um módulo

```
app/code/Vendor/ModuleName/
├── registration.php            ← OBRIGATÓRIO: registra o módulo
├── composer.json               ← dependências via Composer
├── etc/
│   ├── module.xml              ← declara nome, versão e sequência
│   ├── di.xml                  ← injeção de dependência global
│   ├── config.xml              ← valores padrão de configuração
│   ├── acl.xml                 ← permissões de ACL
│   ├── frontend/
│   │   ├── routes.xml          ← rotas do storefront
│   │   └── di.xml              ← DI escopo frontend
│   └── adminhtml/
│       ├── routes.xml          ← rotas do Admin
│       ├── menu.xml            ← itens de menu Admin
│       └── system.xml          ← campos de configuração Admin
├── Controller/
│   ├── Adminhtml/              ← controllers do Admin
│   └── Index/Index.php         ← controller frontend
├── Model/
│   ├── ResourceModel/          ← acesso ao banco de dados
│   └── ResourceModel/Collection/ ← coleções
├── Block/                      ← blocos de template
├── view/
│   ├── frontend/
│   │   ├── layout/             ← XMLs de layout
│   │   └── templates/          ← arquivos .phtml
│   └── adminhtml/
├── Setup/
│   └── Patch/
│       ├── Data/               ← patches de dados
│       └── Schema/             ← patches de schema (legado)
└── etc/db_schema.xml           ← Declarative Schema (moderno)
```

### registration.php — por que é obrigatório?

```php
<?php
use Magento\Framework\Component\ComponentRegistrar;

ComponentRegistrar::register(
    ComponentRegistrar::MODULE,
    'Vendor_ModuleName',
    __DIR__
);
```
Sem este arquivo, o Magento ignora completamente o módulo.

### module.xml — sequência de dependências

```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Module/etc/module.xsd">
    <module name="Vendor_ModuleName">
        <sequence>
            <module name="Magento_Catalog"/>
            <module name="Magento_Sales"/>
        </sequence>
    </module>
</config>
```
`<sequence>` garante que os módulos listados sejam carregados ANTES do seu.

### Comandos CLI essenciais

| Comando | O que faz |
|---|---|
| `bin/magento setup:upgrade` | Aplica novos módulos, patches e schema |
| `bin/magento setup:di:compile` | Compila o container de DI (geração de proxies, factories, interceptors) |
| `bin/magento setup:static-content:deploy` | Publica arquivos estáticos (JS, CSS, imagens) |
| `bin/magento cache:flush` | Limpa o cache (apaga o storage) |
| `bin/magento cache:clean` | Invalida entradas de cache sem apagar o storage |
| `bin/magento module:enable Vendor_Name` | Habilita um módulo |
| `bin/magento module:disable Vendor_Name` | Desabilita um módulo |
| `bin/magento indexer:reindex` | Reindexa todos os indexers |
| `bin/magento indexer:status` | Mostra status dos indexers |
| `bin/magento cron:run` | Executa jobs de cron |
| `bin/magento deploy:mode:set developer` | Muda para modo developer |
| `bin/magento deploy:mode:set production` | Muda para modo production |

**Ordem correta de deploy em produção:**
1. `setup:upgrade`
2. `setup:di:compile`
3. `setup:static-content:deploy`
4. `cache:flush`

---

## 1.2 DI — Dependency Injection

### Como funciona o DI no Magento

O Magento usa um container de DI que injeta automaticamente dependências via construtor. Você nunca usa `new ClassName()` diretamente — tudo vem pelo construtor.

```php
class MyClass
{
    public function __construct(
        private readonly \Magento\Catalog\Api\ProductRepositoryInterface $productRepository,
        private readonly \Psr\Log\LoggerInterface $logger
    ) {}
}
```

### Tipos de configuração em di.xml

**1. Preference (substituição completa)**
```xml
<preference for="Magento\Catalog\Api\ProductRepositoryInterface"
            type="Vendor\Module\Model\ProductRepository"/>
```
- Substitui completamente uma classe/interface por outra
- Risco: pode quebrar compatibilidade com outros módulos
- Use apenas quando plugin não for suficiente

**2. Plugin (interceptor)**
```xml
<type name="Magento\Catalog\Model\Product">
    <plugin name="vendor_module_product_plugin"
            type="Vendor\Module\Plugin\ProductPlugin"
            sortOrder="10"
            disabled="false"/>
</type>
```
Tipos de método plugin:
- `beforeMethod`: executa antes, pode modificar argumentos
- `afterMethod`: executa depois, pode modificar retorno
- `aroundMethod`: envolve a chamada, decide se o original roda

**3. Virtual Type**
```xml
<virtualType name="Vendor\Module\Model\CustomLogger"
             type="Magento\Framework\Logger\Monolog">
    <arguments>
        <argument name="name" xsi:type="string">custom</argument>
    </arguments>
</virtualType>
```
Cria uma "instância configurada" sem criar nova classe PHP.

**4. Arguments (injeção de parâmetros)**
```xml
<type name="Vendor\Module\Model\MyClass">
    <arguments>
        <argument name="myParam" xsi:type="string">valor</argument>
        <argument name="isEnabled" xsi:type="boolean">true</argument>
    </arguments>
</type>
```

### Quando usar cada mecanismo

| Situação | Mecanismo |
|---|---|
| Modificar comportamento de método público | Plugin |
| Substituir implementação de interface | Preference |
| Reagir a um evento sem retorno | Observer |
| Instância com config diferente da padrão | Virtual Type |
| Método é `private`, `final`, ou `static` | **Plugin NÃO funciona** → use Preference ou rewrite |

### Plugin: exemplo completo

```php
<?php
namespace Vendor\Module\Plugin;

class ProductPlugin
{
    // Before: modifica os argumentos antes do método original
    public function beforeSetName(
        \Magento\Catalog\Model\Product $subject,
        string $name
    ): array {
        return [strtoupper($name)]; // retorna array com os novos argumentos
    }

    // After: modifica o retorno do método original
    public function afterGetName(
        \Magento\Catalog\Model\Product $subject,
        string $result
    ): string {
        return $result . ' (modificado)';
    }

    // Around: controla toda a execução
    // Product::save() não tem argumentos — correto sem parâmetros extras
    // Se o método original tivesse args (ex: execute(int $id)), você DEVE declarar e repassar:
    // public function aroundExecute($subject, callable $proceed, int $id) { return $proceed($id); }
    public function aroundSave(
        \Magento\Catalog\Model\Product $subject,
        callable $proceed
    ) {
        // lógica antes
        $result = $proceed(); // chama o método original
        // lógica depois
        return $result;
    }
}
```

---

## 1.3 Observers e Events

### Como funciona

O Magento emite eventos via `EventManager::dispatch()`. Observers são "ouvintes" que reagem a esses eventos de forma desacoplada.

### Registrar um observer em events.xml

```xml
<!-- etc/frontend/events.xml ou etc/events.xml -->
<config xmlns:xsi="..." xsi:noNamespaceSchemaLocation="...">
    <event name="catalog_product_save_after">
        <observer name="vendor_module_product_save"
                  instance="Vendor\Module\Observer\ProductSaveObserver"/>
    </event>
</config>
```

### Implementar o Observer

```php
<?php
namespace Vendor\Module\Observer;

use Magento\Framework\Event\ObserverInterface;
use Magento\Framework\Event\Observer;

class ProductSaveObserver implements ObserverInterface
{
    public function execute(Observer $observer): void
    {
        $product = $observer->getData('product'); // pega dados do evento
        // sua lógica aqui
    }
}
```

### Eventos mais comuns (cobrados na prova)

| Evento | Quando dispara |
|---|---|
| `catalog_product_save_before` | Antes de salvar produto |
| `catalog_product_save_after` | Depois de salvar produto |
| `checkout_cart_add_product_complete` | Produto adicionado ao carrinho |
| `sales_order_place_after` | Pedido finalizado |
| `customer_login` | Cliente faz login |
| `controller_action_predispatch` | Antes de qualquer action de controller |

---

## 1.4 CRON

### Declarar um job em crontab.xml

```xml
<!-- etc/crontab.xml -->
<config xmlns:xsi="..." xsi:noNamespaceSchemaLocation="...">
    <group id="default">
        <job name="vendor_module_job" instance="Vendor\Module\Cron\MyJob"
             method="execute">
            <schedule>*/5 * * * *</schedule> <!-- a cada 5 minutos -->
        </job>
    </group>
</config>
```

### Implementar a classe Cron

```php
<?php
namespace Vendor\Module\Cron;

class MyJob
{
    public function execute(): void
    {
        // lógica do job
    }
}
```

### Grupos de cron

| Grupo | Finalidade |
|---|---|
| `default` | Jobs gerais |
| `index` | Indexação de dados |
| `catalog_event` | Eventos de catálogo |
| `consumers` | Message queue consumers |

---

## 1.5 Indexers

### Conceito

Indexers transformam dados do formato normalizado (EAV) para formato flat/otimizado para leitura rápida.

### Modos de indexação

| Modo | Quando atualiza | Uso ideal |
|---|---|---|
| **Update on Save** | Imediatamente ao salvar a entidade | Catálogos pequenos |
| **Update by Schedule** | Via CRON, periodicamente | Catálogos grandes, alta frequência de edição |

### Indexers principais

| Indexer | O que indexa |
|---|---|
| `catalog_category_product` | Relação categoria-produto |
| `catalog_product_category` | Relação produto-categoria |
| `catalog_product_price` | Preços de produtos |
| `catalog_product_attribute` | Atributos EAV em formato flat |
| `catalogsearch_fulltext` | Índice de busca (Elasticsearch) |
| `catalogrule_rule` | Regras de preço de catálogo |
| `catalogrule_product` | Produtos afetados por regras |
| `sales_order_grid` | Grid de pedidos no Admin |

### Declarar um indexer customizado

```xml
<!-- etc/indexer.xml -->
<config xmlns:xsi="..." xsi:noNamespaceSchemaLocation="...">
    <indexer id="vendor_module_index"
             view_id="vendor_module_view"
             class="Vendor\Module\Model\Indexer\MyIndexer"
             primary="id">
        <title translate="true">My Custom Index</title>
        <description translate="true">Description here</description>
    </indexer>
</config>
```

---

## 1.6 Cache

### Tipos de cache e o que armazenam

| Cache type | Tag | O que armazena |
|---|---|---|
| `config` | CONFIG | Configurações do sistema |
| `layout` | LAYOUT_GENERAL_CACHE_TAG | XML de layouts compilados |
| `block_html` | BLOCK_HTML | HTML de blocos individuais |
| `collections` | COLLECTION_DATA | Resultados de coleções de dados |
| `reflection` | REFLECTION | Reflexão de classes PHP |
| `db_ddl` | DB_DDL | Schema do banco de dados |
| `compiled_config` | - | Configurações compiladas |
| `full_page` | FPC | Páginas inteiras (FPC) |
| `vertex` | VERTEX | Cache do Vertex Tax |

### Backends de cache

| Backend | Quando usar |
|---|---|
| **File** | Dev local (padrão) |
| **Redis** | Produção (recomendado) — compartilhado entre nós |
| **Memcached** | Alternativa ao Redis |
| **Varnish** | Full-page cache em produção |

### Adicionar cache a um bloco customizado

```php
protected function _construct()
{
    $this->addData([
        'cache_lifetime' => 86400, // segundos (1 dia)
        'cache_tags'     => [\Magento\Catalog\Model\Product::CACHE_TAG],
        'cache_key'      => 'my_custom_block_' . $this->getProductId(),
    ]);
}
```

---

## 1.7 EAV e Database

### O que é EAV

Entity-Attribute-Value é o modelo de dados usado por produto, categoria e cliente. Em vez de uma coluna por atributo, há tabelas separadas por tipo.

**Entidades EAV principais:**
- `catalog_product_entity` + `catalog_product_entity_{type}`
- `catalog_category_entity` + `catalog_category_entity_{type}`
- `customer_entity` + `customer_entity_{type}`

**Tipos de valor:** `varchar`, `int`, `decimal`, `datetime`, `text`

### Declarative Schema — db_schema.xml

```xml
<!-- etc/db_schema.xml -->
<schema xmlns:xsi="..." xsi:noNamespaceSchemaLocation="...">
    <table name="vendor_module_entity" resource="default"
           engine="innodb" comment="My Entity">
        <column xsi:type="int" name="entity_id" unsigned="true"
                nullable="false" identity="true" comment="Entity ID"/>
        <column xsi:type="varchar" name="name" nullable="false"
                length="255" comment="Name"/>
        <column xsi:type="timestamp" name="created_at" nullable="false"
                default="CURRENT_TIMESTAMP" comment="Created At"/>
        <constraint xsi:type="primary" referenceId="PRIMARY">
            <column name="entity_id"/>
        </constraint>
        <index referenceId="VENDOR_MODULE_ENTITY_NAME" indexType="btree">
            <column name="name"/>
        </index>
    </table>
</schema>
```

**Gerar o whitelist após criar o schema:**
```bash
bin/magento setup:db-declaration:generate-whitelist --module-name=Vendor_Module
```

### Data Patches

```php
<?php
namespace Vendor\Module\Setup\Patch\Data;

use Magento\Framework\Setup\Patch\DataPatchInterface;

class AddInitialData implements DataPatchInterface
{
    public function __construct(
        private readonly \Magento\Framework\Setup\ModuleDataSetupInterface $moduleDataSetup
    ) {}

    public function apply(): self
    {
        $this->moduleDataSetup->startSetup();
        // sua lógica de dados aqui
        $this->moduleDataSetup->endSetup();
        return $this;
    }

    public static function getDependencies(): array { return []; }
    public function getAliases(): array { return []; }
}
```

---

## 1.8 Service Contracts

### Conceito

Service Contracts são interfaces PHP que definem o comportamento público de um módulo, isolando a implementação interna. São o contrato público entre módulos.

**Estrutura:**
```
Api/
├── Data/
│   ├── ProductInterface.php        ← Data Object Interface
│   └── ProductSearchResultsInterface.php
└── ProductRepositoryInterface.php  ← Repository Interface
```

### Repository Interface típica

```php
interface ProductRepositoryInterface
{
    public function get(string $sku, bool $editMode = false): ProductInterface;
    public function getById(int $productId): ProductInterface;
    public function save(ProductInterface $product): ProductInterface;
    public function delete(ProductInterface $product): bool;
    public function deleteById(string $sku): bool;
    public function getList(SearchCriteriaInterface $searchCriteria): ProductSearchResultsInterface;
}
```

### SearchCriteria — como usar

```php
$searchCriteria = $this->searchCriteriaBuilder
    ->addFilter('status', 1)
    ->addFilter('visibility', [2, 4], 'in')
    ->setPageSize(20)
    ->setCurrentPage(1)
    ->addSortOrder($this->sortOrderBuilder->setField('name')->setAscendingDirection()->create())
    ->create();

$results = $this->productRepository->getList($searchCriteria);
```

---

## 1.9 Hierarquia de Store e Localização

### Hierarquia

```
Website (website_id)
└── Store / Store Group (group_id)
    └── Store View (store_id)
```

- **Website**: nível mais alto, define domínio/moeda base
- **Store/Group**: define catálogo raiz e checkout
- **Store View**: define idioma/localização, o que o cliente vê

### Escopos de configuração

| Escopo | Prioridade | Onde configurar |
|---|---|---|
| Global | Baixa (fallback) | Stores > Configuration > (sem seletor de scope) |
| Website | Média | Selecionar Website no dropdown |
| Store View | Alta (sobrescreve) | Selecionar Store View no dropdown |

### Traduções

**Hierarquia de tradução (ordem de prioridade):**
1. Banco de dados (via Translation widget no Admin)
2. `app/design/frontend/Vendor/theme/i18n/en_US.csv` (tema)
3. `app/code/Vendor/Module/i18n/en_US.csv` (módulo)
4. `vendor/package/i18n/en_US.csv` (pacote Composer)

```csv
"Add to Cart","Adicionar ao Carrinho"
"My Account","Minha Conta"
```

---

## 1.10 URL Rewrites e Admin Panel

### URL Rewrites

A tabela `url_rewrite` mapeia URLs amigáveis para rotas internas.

| Coluna | Descrição |
|---|---|
| `request_path` | URL amigável: `produto/nome-do-produto.html` |
| `target_path` | Rota interna: `catalog/product/view/id/42` |
| `redirect_type` | 0 = sem redirect, 301, 302 |
| `entity_type` | `product`, `category`, `cms-page` |

### Attribute Sets no Admin

- Attribute Sets agrupam atributos de produtos
- Atributos pertencem a grupos dentro de um Attribute Set
- O Attribute Set padrão é "Default"
- Produtos do tipo Configurable criam atributos específicos para variações

---

# DOMÍNIO 2 — CUSTOMIZAÇÕES (36%)

## 2.1 Catálogo

### Tipos de produto

| Tipo | Uso | Tem estoque físico? |
|---|---|---|
| **Simple** | Produto básico, SKU único | Sim |
| **Configurable** | Produto com variações (cor, tamanho) | Sim (via simples) |
| **Grouped** | Grupo de produtos simples juntos | Sim |
| **Bundle** | Kit customizável de produtos | Sim |
| **Virtual** | Serviço, assinatura — sem envio | Não |
| **Downloadable** | Arquivo digital para download | Não |

### Criando produto programaticamente

```php
$product = $this->productFactory->create();
$product->setSku('my-sku-001');
$product->setName('My Product');
$product->setPrice(29.99);
$product->setStatus(\Magento\Catalog\Model\Product\Attribute\Source\Status::STATUS_ENABLED);
$product->setVisibility(\Magento\Catalog\Model\Product\Visibility::VISIBILITY_BOTH);
$product->setTypeId(\Magento\Catalog\Model\Product\Type::TYPE_SIMPLE);
$product->setAttributeSetId(4); // Default attribute set
$product->setStockData(['qty' => 100, 'is_in_stock' => 1]);

$this->productRepository->save($product);
```

### Attribute Types e Input Types

| Input Type | Backend Type | Uso |
|---|---|---|
| text | varchar | Texto curto |
| textarea | text | Texto longo |
| select | int | Dropdown |
| multiselect | varchar | Multi-seleção |
| boolean | int | Sim/Não |
| price | decimal | Preço |
| date | datetime | Data |

---

## 2.2 Checkout e Sales

### Fluxo de pedido (entities)

```
Quote (carrinho)
  └── Order (pedido confirmado)
        ├── Invoice (fatura gerada)
        ├── Shipment (envio gerado)
        └── Credit Memo (devolução)
```

### Quote vs Order

| Aspecto | Quote | Order |
|---|---|---|
| Tabela | `quote` | `sales_order` |
| Status | Ativo/Inativo | pending, processing, complete, etc. |
| Itens | `quote_item` | `sales_order_item` |
| Quando existe | Durante o checkout | Após finalização |

### Order States e Statuses

| State | Statuses possíveis |
|---|---|
| `new` | pending, pending_payment |
| `pending_payment` | pending_payment |
| `processing` | processing |
| `complete` | complete |
| `closed` | closed |
| `canceled` | canceled |
| `holded` | holded |

### Customizar o checkout (steps)

```xml
<!-- view/frontend/layout/checkout_index_index.xml -->
<referenceComponent name="checkout.steps">
    <arguments>
        <argument name="jsLayout" xsi:type="array">
            <item name="components" xsi:type="array">
                <item name="checkout" xsi:type="array">
                    <item name="children" xsi:type="array">
                        <item name="steps" xsi:type="array">
                            <item name="children" xsi:type="array">
                                <item name="my-custom-step" xsi:type="array">
                                    <item name="component" xsi:type="string">Vendor_Module/js/view/my-step</item>
                                    <item name="sortOrder" xsi:type="string">1</item>
                                </item>
                            </item>
                        </item>
                    </item>
                </item>
            </item>
        </argument>
    </arguments>
</referenceComponent>
```

### Total Collectors (customizar totais do carrinho)

```xml
<!-- etc/sales.xml -->
<config>
    <section name="quote">
        <group name="totals">
            <item name="my_custom_fee" instance="Vendor\Module\Model\Quote\Total\CustomFee" sort_order="450"/>
        </group>
    </section>
</config>
```

---

## 2.3 APIs REST e GraphQL

### REST API — webapi.xml

```xml
<!-- etc/webapi.xml -->
<routes xmlns:xsi="..." xsi:noNamespaceSchemaLocation="...">
    <route url="/V1/vendor-module/items" method="GET">
        <service class="Vendor\Module\Api\ItemRepositoryInterface" method="getList"/>
        <resources>
            <resource ref="Magento_Catalog::catalog"/>
        </resources>
    </route>
    <route url="/V1/vendor-module/items/:id" method="GET">
        <service class="Vendor\Module\Api\ItemRepositoryInterface" method="getById"/>
        <resources>
            <resource ref="anonymous"/> <!-- público, sem auth -->
        </resources>
    </route>
</routes>
```

### Tipos de autenticação REST

| Tipo | Header | Quem usa |
|---|---|---|
| Admin token | `Authorization: Bearer <admin_token>` | Integrações admin |
| Customer token | `Authorization: Bearer <customer_token>` | Apps do cliente |
| Guest | Sem header | Recursos públicos (anonymous) |
| Integration | OAuth 1.0 | Sistemas externos |

### Obter tokens via REST

```bash
# Token de admin
POST /rest/V1/integration/admin/token
{"username":"admin","password":"password123"}

# Token de customer
POST /rest/V1/integration/customer/token
{"username":"customer@email.com","password":"pass123"}
```

### GraphQL — schema.graphqls

```graphql
type Query {
    myProducts(
        search: String
        filter: ProductAttributeFilterInput
        pageSize: Int = 20
        currentPage: Int = 1
    ): MyProducts @resolver(class: "Vendor\\Module\\Model\\Resolver\\Products") @cache(cacheIdentity: "Vendor\\Module\\Model\\Resolver\\ProductsIdentity")
}

type MyProducts {
    items: [ProductInterface]
    total_count: Int
    page_info: SearchResultPageInfo
}
```

---

## 2.4 Adobe SaaS Services e Data Export

### Serviços SaaS da Adobe

| Serviço | Função |
|---|---|
| **Live Search** | Busca powered by Adobe AI |
| **Product Recommendations** | Recomendações de produtos com ML |
| **Catalog Service** | API de catálogo otimizada para vitrine |
| **Payment Services** | Processamento de pagamentos |

### Fluxo de dados SaaS

```
Adobe Commerce (backend)
    ↓ Data Export Module
    ↓ Feed Indexers (products, prices, categories, inventory)
    ↓ SaaS Data Export API
    ↓ Adobe SaaS Platform
    ↓ Live Search / Product Recs / Catalog Service
```

### Comandos úteis para SaaS

```bash
# Sincronizar feeds manualmente
bin/magento saas:resync --feed=products
bin/magento saas:resync --feed=productAttributes
bin/magento saas:resync --feed=categories
bin/magento saas:resync --feed=prices

# Verificar status
bin/magento indexer:status | grep saas
```

### API Mesh

API Mesh é uma camada de orquestração (baseada em Adobe App Builder) que permite:
- Combinar múltiplas APIs (Commerce, terceiros) em um único endpoint GraphQL
- Transformar dados entre APIs
- Adicionar autenticação e cache centralizados

---

## 2.5 Manipulação Programática de Entidades

### Customer — criar programaticamente

```php
$customer = $this->customerFactory->create();
$customer->setEmail('test@email.com');
$customer->setFirstname('John');
$customer->setLastname('Doe');
$customer->setWebsiteId(1);
$customer->setStoreId(1);

$hashedPassword = $this->encryptor->getHash('password123', true);
$this->customerRepository->save($customer, $hashedPassword);
```

### Manipular Order programaticamente

```php
// Criar invoice
$invoice = $this->invoiceService->prepareInvoice($order);
$invoice->setRequestedCaptureCase(\Magento\Sales\Model\Order\Invoice::CAPTURE_ONLINE);
$invoice->register();

$transaction = $this->transactionFactory->create()
    ->addObject($invoice)
    ->addObject($order);
$transaction->save();
```

---

# DOMÍNIO 3 — CLOUD (12%)

## 3.1 Arquitetura do Adobe Commerce Cloud

### Ambientes

```
Production (live)
    ↑ merge
Staging (pré-prod, clone da prod)
    ↑ merge
Integration branches (desenvolvimento)
    ├── feature/branch-a
    └── feature/branch-b
```

### Arquitetura de infraestrutura

**Starter plan:**
- 4 ambientes: Production, Staging, 2 Integration

**Pro plan:**
- Production (cluster dedicado): 3 nós web + MySQL master/slave + Redis + Elasticsearch
- Staging (clone da prod)
- Integration (N branches)

---

## 3.2 Arquivos de Configuração Cloud

### .magento.app.yaml

```yaml
name: myapp
type: php:8.2
build:
    flavor: none
dependencies:
    php:
        composer/composer: '^2.2'
hooks:
    build: |
        set -e
        composer install --no-dev --prefer-dist --optimize-autoloader
        php ./vendor/bin/ece-tools run scenario/build/generate.xml
        php ./vendor/bin/ece-tools run scenario/build/transfer.xml
    deploy: |
        php ./vendor/bin/ece-tools run scenario/deploy.xml
    post_deploy: |
        php ./vendor/bin/ece-tools run scenario/post-deploy.xml
web:
    locations:
        '/':
            root: pub
            passthru: /index.php
relationships:
    database: 'mysql:mysql'
    redis: 'redis:redis'
    elasticsearch: 'elasticsearch:elasticsearch'
```

### services.yaml

```yaml
mysql:
    type: mysql:10.6
    disk: 2048
redis:
    type: redis:7.0
elasticsearch:
    type: elasticsearch:8.5
    disk: 1024
```

### routes.yaml

```yaml
"https://www.{default}/":
    type: upstream
    upstream: "myapp:http"
"https://{default}/":
    type: redirect
    to: "https://www.{default}/"
```

### .magento.env.yaml

```yaml
stage:
    global:
        SKIP_HTML_MINIFICATION: true
    build:
        SCD_STRATEGY: compact
        SCD_COMPRESSION_LEVEL: 4
    deploy:
        SEARCH_CONFIGURATION:
            engine: elasticsearch7
            elasticsearch_server_hostname: elasticsearch.internal
            elasticsearch_server_port: '9200'
        CACHE_CONFIGURATION:
            _merge: true
            frontend:
                default:
                    backend: Cm_Cache_Backend_Redis
                    backend_options:
                        server: redis.internal
                        port: '6379'
```

---

## 3.3 CLI do Cloud

| Comando | O que faz |
|---|---|
| `magento-cloud login` | Autenticar |
| `magento-cloud environment:list` | Listar ambientes |
| `magento-cloud environment:checkout <branch>` | Fazer checkout de ambiente |
| `magento-cloud ssh` | SSH no ambiente ativo |
| `magento-cloud environment:push` | Push do branch atual |
| `magento-cloud environment:merge` | Merge para o ambiente pai |
| `magento-cloud environment:delete` | Deletar ambiente |
| `magento-cloud log:tail --type=deploy` | Ver logs de deploy |
| `magento-cloud db:sql` | Acesso SQL ao banco |
| `magento-cloud tunnel:open` | Abrir tunnel para serviços |
| `magento-cloud variable:set VAR valor` | Definir variável de ambiente |
| `magento-cloud variable:get VAR` | Ler variável |

---

## 3.4 Variáveis de Ambiente e Segurança

### Níveis de variáveis

| Nível | Scope | Comando |
|---|---|---|
| Project | Todos os ambientes | `magento-cloud variable:set --level=project` |
| Environment | Ambiente específico | `magento-cloud variable:set --level=environment` |

### Variáveis sensíveis (nunca no git!)

```bash
# Chave de API — apenas no ambiente, sem expor no git
magento-cloud variable:set --level=environment \
    --sensitive=true \
    --name=PAYMENT_API_KEY \
    --value="sk_live_xxxxx"
```

### ECE-Tools e Deploy Scenarios

O `ece-tools` orquestra o deploy via cenários XML:
- `scenario/build/generate.xml` — gera código (DI compile, etc.)
- `scenario/build/transfer.xml` — transfere assets
- `scenario/deploy.xml` — deploy principal (maintenance on, setup:upgrade, etc.)
- `scenario/post-deploy.xml` — warm-up de cache, health checks

### Hooks de deploy — ordem e o que cada um pode fazer

| Hook | Acesso a serviços? | Tráfego servido? | Uso típico |
|---|---|---|---|
| `build` | Não | Não | Compilar código, instalar deps, gerar assets estáticos |
| `deploy` | Sim | Não (maintenance on) | `setup:upgrade`, configurações de cache |
| `post_deploy` | Sim | Sim | Warm-up de cache, notificações, health checks |

---

## Perguntas de Exemplo — Estilo Prova Real

### Arquitetura

**Q1:** Um desenvolvedor criou um plugin `around` em um método da classe `Magento\Catalog\Model\Product`, mas o plugin nunca é executado. Qual é a causa mais provável?

**A:** O método interceptado pode ser `final`, `private`, ou `static`. Plugins só funcionam em métodos públicos não-finais. A solução é usar uma Preference em vez de Plugin.

---

**Q2:** Qual é a diferença entre `cache:clean` e `cache:flush`?

**A:** `cache:clean` invalida as entradas de cache por tag (os dados são marcados como inválidos mas o storage permanece). `cache:flush` apaga completamente o storage de cache. Em produção com Redis compartilhado, `cache:flush` pode afetar outros processos — prefira `cache:clean`.

---

**Q3:** Um novo módulo foi instalado mas `bin/magento module:status` mostra que ele está desabilitado. Qual sequência de comandos é necessária para ativá-lo corretamente?

**A:** 
1. `bin/magento module:enable Vendor_ModuleName`
2. `bin/magento setup:upgrade`
3. `bin/magento setup:di:compile`
4. `bin/magento cache:flush`

---

### Customizações

**Q4:** Qual é a diferença entre `Observer` e `Plugin` ao modificar comportamento de uma operação de salvar produto?

**A:** Plugin intercepta o método diretamente e pode modificar argumentos e retorno. Observer reage ao evento `catalog_product_save_after` de forma desacoplada mas não pode modificar o comportamento do save em si nem retornar valores. Use Plugin quando precisar de controle sobre o fluxo; use Observer para reações side-effect.

---

**Q5:** Um cliente quer que todos os produtos tenham um campo customizado "Certificate Number" que apareça no frontend e na API REST. Quais passos são necessários?

**A:**
1. Criar atributo de produto via Data Patch (tipo `varchar`)
2. Adicionar ao Attribute Set desejado
3. Para a API: o atributo EAV já é exposto via `ProductInterface` automaticamente se `is_visible` = true
4. Para o frontend: usar layout XML para renderizar o atributo no template de produto

---

### Cloud

**Q6:** Qual arquivo você edita para mudar a versão do PHP usada no ambiente Cloud de 8.1 para 8.2?

**A:** `.magento.app.yaml` — alterar a linha `type: php:8.1` para `type: php:8.2`, depois commitar e fazer push para o branch de integration.

---

## Links de Estudo Oficiais

- [Documentação oficial do developer](https://developer.adobe.com/commerce/docs/)
- [PHP Developer Guide](https://developer.adobe.com/commerce/php/development/)
- [Commerce on Cloud Guide](https://experienceleague.adobe.com/en/docs/commerce-on-cloud)
- [REST API Reference](https://developer.adobe.com/commerce/webapi/rest/)
- [GraphQL Reference](https://developer.adobe.com/commerce/webapi/graphql/)
- [Adobe Commerce DevDocs — Plugins](https://developer.adobe.com/commerce/php/development/components/plugins/)
- [Adobe Commerce DevDocs — Events/Observers](https://developer.adobe.com/commerce/php/development/components/events-and-observers/)
- [Declarative Schema](https://developer.adobe.com/commerce/php/development/components/declarative-schema/)

---

*Guia gerado para preparação AD0-E724 — Adobe Commerce Developer Professional*
*Versão de referência: Adobe Commerce 2.4.7*
