# APIs

> **Domínio 2 — Customizações (36%)** &nbsp;·&nbsp; Seções 2.3, 2.4

---

## REST API

### webapi.xml

```xml
<!-- etc/webapi.xml -->
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:module:Magento_Webapi:etc/webapi.xsd">

    <!-- Lista pública -->
    <route url="/V1/vendor-module/items" method="GET">
        <service class="Vendor\Module\Api\ItemRepositoryInterface" method="getList"/>
        <resources>
            <resource ref="anonymous"/>
        </resources>
    </route>

    <!-- Requer autenticação admin -->
    <route url="/V1/vendor-module/items/:id" method="GET">
        <service class="Vendor\Module\Api\ItemRepositoryInterface" method="getById"/>
        <resources>
            <resource ref="Magento_Catalog::catalog"/>
        </resources>
    </route>

    <!-- Apenas para o próprio cliente autenticado -->
    <route url="/V1/vendor-module/me/items" method="GET">
        <service class="Vendor\Module\Api\ItemRepositoryInterface" method="getMyItems"/>
        <resources>
            <resource ref="self"/>
        </resources>
    </route>
</routes>
```

---

## Tipos de Autenticação

| Tipo | Header | Quem usa |
|---|---|---|
| Admin token | `Authorization: Bearer <admin_token>` | Integrações administrativas |
| Customer token | `Authorization: Bearer <customer_token>` | Apps do cliente logado |
| Guest | Sem header | Recursos públicos (`anonymous`) |
| Integration | OAuth 1.0 | Sistemas externos via Admin > Integrations |

### Recursos Especiais

| Recurso | Significado |
|---|---|
| `anonymous` | Sem autenticação — acesso público |
| `self` | Apenas o próprio cliente autenticado |

---

## Obter Tokens

```bash
# Token de admin
curl -X POST https://loja.com/rest/V1/integration/admin/token \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Admin@123"}'

# Token de customer
curl -X POST https://loja.com/rest/V1/integration/customer/token \
  -H 'Content-Type: application/json' \
  -d '{"username":"cliente@email.com","password":"Senha@123"}'
```

### Usar o Token

```bash
curl -X GET https://loja.com/rest/V1/products/my-sku \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...'
```

---

## GraphQL

### Definir Schema — schema.graphqls

```graphql
type Query {
    myProducts(
        search: String
        filter: ProductAttributeFilterInput
        pageSize: Int = 20
        currentPage: Int = 1
    ): MyProductsOutput
        @resolver(class: "Vendor\\Module\\Model\\Resolver\\Products")
        @cache(cacheIdentity: "Vendor\\Module\\Model\\Resolver\\ProductsIdentity")
        @doc(description: "Retorna lista de produtos customizados")
}

type MyProductsOutput {
    items: [ProductInterface] @doc(description: "Lista de produtos")
    total_count: Int          @doc(description: "Total de resultados")
    page_info: SearchResultPageInfo
}
```

### Implementar o Resolver

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Model\Resolver;

use Magento\Framework\GraphQl\Config\Element\Field;
use Magento\Framework\GraphQl\Query\ResolverInterface;
use Magento\Framework\GraphQl\Schema\Type\ResolveInfo;

class Products implements ResolverInterface
{
    public function resolve(
        Field $field,
        mixed $context,
        ResolveInfo $info,
        ?array $value = null,
        ?array $args = null
    ): array {
        // lógica de resolução
        return [
            'items'       => [],
            'total_count' => 0,
            'page_info'   => ['current_page' => 1, 'page_size' => 20, 'total_pages' => 0],
        ];
    }
}
```

---

## GraphQL — Convenções Importantes

### Naming do módulo

```
{Vendor}_{Module}GraphQl   ← sufixo obrigatório
```

```
Vendor/
└── MyModuleGraphQl/       ← nome do diretório
    ├── registration.php
    ├── etc/
    │   ├── module.xml
    │   └── schema.graphqls   ← DEVE estar aqui
    └── Model/
        └── Resolver/
            └── MyResolver.php
```

> Armadilha: `schema.graphqls` em `etc/frontend/` ou `etc/adminhtml/` — **não funciona**. Deve estar em `etc/` (global).

### Tipos de operação GraphQL

| Tipo | Descrição | Autenticação |
|---|---|---|
| `query` | Leitura de dados | Opcional (depende do tipo) |
| `mutation` | Escrita/modificação | Geralmente requer token |

### Cache no GraphQL

```graphql
type Query {
    myQuery: MyType
        @resolver(class: "Vendor\\Module\\Model\\Resolver\\MyResolver")
        @cache(cacheIdentity: "Vendor\\Module\\Model\\Resolver\\MyIdentity")
}
```

A classe de identidade implementa `Magento\Framework\GraphQl\Query\Resolver\IdentityInterface` e define as cache tags para invalidação.

---

## REST — Método HTTP e Operação

| HTTP Method | Operação CRUD | Comportamento |
|---|---|---|
| `GET` | Read | Busca dados, sem body |
| `POST` | Create | Cria novo recurso |
| `PUT` | Update (completo) | Substitui o recurso inteiro |
| `DELETE` | Delete | Remove o recurso |

> **Armadilha:** `PUT` substitui o recurso inteiro. Para updates parciais em alguns endpoints, usar `POST`.

---

## Adobe SaaS Services

| Serviço | Função |
|---|---|
| **Live Search** | Busca powered by Adobe AI (substitui Elasticsearch no storefront) |
| **Product Recommendations** | Recomendações com ML (também comprado, mais vistos, etc.) |
| **Catalog Service** | API de catálogo otimizada para storefronts headless |
| **Payment Services** | Processamento de pagamentos integrado |

---

## Fluxo de Dados SaaS

```
Adobe Commerce (backend)
    ↓  Data Export Module
    ↓  Feed Indexers (products, prices, categories, inventory)
    ↓  SaaS Data Export API
    ↓  Adobe SaaS Platform
    ↓  Live Search / Product Recs / Catalog Service
```

### Sincronização Manual de Feeds

```bash
bin/magento saas:resync --feed=products
bin/magento saas:resync --feed=productAttributes
bin/magento saas:resync --feed=categories
bin/magento saas:resync --feed=prices
bin/magento saas:resync --feed=inventoryStockStatus

# Verificar status
bin/magento indexer:status | grep saas
```

---

## API Mesh

API Mesh é uma camada de orquestração baseada em **Adobe App Builder** que permite:

- Combinar múltiplas APIs (Commerce, terceiros) em um **único endpoint GraphQL**
- Transformar e mapear dados entre APIs
- Centralizar autenticação e cache
- Reduzir chamadas do frontend (resolve N+1 queries)

```
Frontend / PWA Studio
    ↓
API Mesh (GraphQL unificado)
    ├── Adobe Commerce GraphQL
    ├── ERP API (REST)
    └── CRM API (REST/GraphQL)
```

> API Mesh roda na infraestrutura da Adobe (App Builder/IO Runtime) — **não é um módulo Magento**.
