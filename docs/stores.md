# Stores & Store Views

> **Domínio 1 — Arquitetura (52%)** &nbsp;·&nbsp; Hierarquia, escopos, e situações reais de multi-store

---

## Cenários Rápidos — "O cliente quer..."

| O cliente quer... | Solução | Por quê |
|---|---|---|
| Um SKU acessível em duas lojas distintas | Atribuir o produto a **ambos os Websites** no admin | SKU é global — o produto já existe, basta associar |
| Conta do cliente válida nas duas Store Views de um mesmo site | Nada — funciona automaticamente | Customer account é **website-scoped** (compartilhado entre Store Views do mesmo Website) |
| Conta do cliente válida em dois Websites diferentes | Marcar **"Share Customer Accounts" = Global** em `Stores > Config > Customers > Account Sharing Options` | Por padrão contas **não** são compartilhadas entre Websites |
| Preço diferente por mercado (BR vs EUA) | Criar **Websites** separados + preço por website | Price scope é **website** |
| Idioma diferente por Store View | Configurar **Locale** separado em cada Store View | Locale é **store view-scoped** |
| Descrição do produto diferente por idioma | Editar o produto, trocar o **Store View selector** no admin, salvar os campos de texto | Atributos de conteúdo são **store view-scoped** |
| Esconder produto em uma loja mas não em outra | Alterar **Visibility** ou **Status** em scope de Store View | Status/Visibility são store view-scoped |
| Categoria diferente por loja | Criar categorias com **Is Active = No** em determinadas Store Views | Category display é store view-scoped |
| Configuração de frete diferente por Website | Ir em `Stores > Config`, **mudar o scope** para o Website desejado | Configurações aceitam override por Website/Store View |
| Layout/tema diferente por Store View | Atribuir **Design Theme** diferente em `Content > Design > Configuration` | Theme é store view-scoped |

---

## Hierarquia: Website → Store → Store View

```
Global (escopo Default)
└── Website A  (ex: "Loja Brasil")
│    ├── Store A1  (ex: "Catálogo Principal")
│    │    ├── Store View: pt_BR  ← idioma/moeda
│    │    └── Store View: en_US  ← idioma/moeda alternativo
│    └── Store A2  (ex: "Catálogo Outlet")
│         └── Store View: pt_BR
└── Website B  (ex: "Loja EUA")
     └── Store B1
          └── Store View: en_US
```

| Nível | Representa | Exemplo |
|---|---|---|
| **Global** | Configurações padrão que valem para tudo | Valor default sem override |
| **Website** | Unidade de negócio independente (moeda, clientes, preços) | "Loja Brasil" vs "Loja EUA" |
| **Store** | Agrupador de catálogo (root category) | "Catálogo Masculino" vs "Catálogo Feminino" |
| **Store View** | Apresentação visual/idioma de um Store | "pt_BR", "en_US", "es_MX" |

> **Regra de negócio:** Um Website pode ter vários Stores, mas cada Store tem **uma root category**. Um Store pode ter várias Store Views.

---

## Escopos de Configuração

### O que é configurável em qual nível

| Config | Escopo mínimo | Exemplo |
|---|---|---|
| Moeda base | **Website** | BRL no Brasil, USD nos EUA |
| Moeda de display | **Store View** | Pode exibir USD mas aceitar EUR |
| Preço de produto | **Website** | Preço BR ≠ Preço EUA |
| Idioma / Locale | **Store View** | pt_BR, en_US, es_MX |
| Fuso horário | **Website** | America/Sao_Paulo |
| Tax rules | **Website** | Regras de ICMS vs Sales Tax |
| Customer account | **Website** | Conta criada no Website A não existe no B (padrão) |
| Métodos de pagamento | **Website** | Boleto só no Website BR |
| Métodos de frete | **Website** | Correios só no Website BR |
| Design/Tema | **Store View** | Tema de natal só em pt_BR |
| E-mail templates | **Store View** | E-mail em português para pt_BR |
| Root Category | **Store** | Catálogo inteiro separado por Store |

---

## Escopos de Produto

### O que é global vs localizado

| Atributo do produto | Escopo | Comportamento |
|---|---|---|
| **SKU** | Global | Mesmo SKU em todos os lugares |
| **Price** | Website (configurável) | Pode ter preço diferente por Website |
| **Stock qty** | Global (com MSI: website/source) | Mesmo estoque por padrão |
| **Status** (enabled/disabled) | Store View | Pode desabilitar em uma Store View |
| **Visibility** | Store View | Pode esconder em uma Store View |
| **Name** | Store View | Traduzível por idioma |
| **Description** | Store View | Traduzível por idioma |
| **URL Key** | Store View | URL diferente por idioma |
| **Meta Title/Description** | Store View | SEO por idioma |
| **Custom attribute (texto)** | Store View | Traduzível |
| **Custom attribute (select/dropdown)** | Global | Opção selecionada é global |
| **Images** | Store View (pode ter override) | Imagem localizada possível |

> **Regra prática:** Campos de texto → Store View. Campos numéricos/lógicos → tendem a ser globais.

---

## Customer Accounts — Compartilhamento

### Como funciona o escopo padrão

Por padrão, o Magento cria contas de cliente no escopo do **Website**:

```
Website A                  Website B
├── customer@email.com     └── (mesmo e-mail → conta diferente ou erro)
└── Store View pt_BR
└── Store View en_US ← mesma conta funciona nas duas Store Views!
```

### Config: Account Sharing

`Stores → Configuration → Customers → Customer Configuration → Account Sharing Options`

| Opção | Comportamento |
|---|---|
| **Per Website** (padrão) | Conta válida apenas no Website onde foi criada |
| **Global** | Uma conta funciona em todos os Websites |

> **Pegadinha do exame:** Dentro do mesmo Website, o cliente **automaticamente** tem acesso a todas as Store Views — não é necessária nenhuma configuração. O problema só existe entre **Websites diferentes**.

### Criar cliente em Website específico programaticamente

```php
$customer->setWebsiteId(1);  // Website ID
$customer->setStoreId(1);    // Store View ID onde foi criado
```

---

## Price Scope — Configuração

`Stores → Configuration → Catalog → Catalog → Price`

| Opção | Comportamento |
|---|---|
| **Global** | Um preço para todos os Websites |
| **Website** | Preço independente por Website |

> Mudar o Price Scope de Global para Website **não move** preços existentes — eles precisam ser reconfigurados em cada Website.

---

## Como Editar Conteúdo por Store View (Admin)

1. Ir em `Catalog → Products → [produto]`
2. No canto superior esquerdo: dropdown **"Store View"** → selecionar a Store View desejada
3. Os campos com override vão mostrar um **checkbox "Use Default"** ao lado
4. Desmarcar "Use Default" → editar o valor localizado
5. Salvar

```
[ ] Use Default Value  |  Nome do Produto em Português
```

> Se "Use Default" está marcado, o produto herda o valor do escopo pai (Global). Se desmarcado, o valor salvo é específico para aquela Store View.

---

## Root Category — Catálogos Separados por Store

Cada **Store** tem uma **Root Category**. Isso permite catálogos completamente distintos:

```
Store "Masculino" → Root Category ID: 3  (contém produtos masculinos)
Store "Feminino"  → Root Category ID: 5  (contém produtos femininos)
```

- Um produto atribuído à categoria 3 **não aparece** na Store "Feminino" automaticamente
- Para o produto aparecer nas duas Stores, deve ser atribuído a categorias de **ambas as root categories**

---

## Websites, Stores, Store Views — Tabela de IDs

Cada entidade tem um ID próprio. Constantes/métodos úteis:

```php
use Magento\Store\Model\StoreManagerInterface;

// Obter Store View atual
$store = $this->storeManager->getStore();
$storeId = $store->getId();           // ex: 1
$websiteId = $store->getWebsiteId();  // ex: 1

// Listar todos os Websites
$websites = $this->storeManager->getWebsites();

// Listar todas as Stores
$stores = $this->storeManager->getStores();

// Website pelo código
$website = $this->storeManager->getWebsite('base');
```

---

## Configuração por Escopo — Config Table

Todas as configurações de `Stores → Config` ficam em `core_config_data`:

| Coluna | Valor exemplo | Significado |
|---|---|---|
| `scope` | `default` | Valor global |
| `scope` | `websites` | Valor para um Website |
| `scope` | `stores` | Valor para uma Store View |
| `scope_id` | `0` | Global (scope=default) |
| `scope_id` | `1` | Website ID ou Store View ID |
| `path` | `catalog/price/scope` | Caminho da configuração |
| `value` | `0` ou `1` | Valor salvo |

```sql
SELECT * FROM core_config_data WHERE path = 'catalog/price/scope';
-- scope=default, scope_id=0, value=0 (Global) ou value=1 (Website)
```

---

## Casos de Uso Avançados

### Produto com URL diferente por idioma

```
Store View pt_BR → url_key: "camiseta-azul"    → /camiseta-azul.html
Store View en_US → url_key: "blue-t-shirt"     → /blue-t-shirt.html
```

Cada Store View tem seu próprio registro em `url_rewrite` com o `store_id` correspondente.

### Desabilitar produto em uma Store View específica

1. Abrir o produto no admin
2. Trocar Store View para a Store View onde quer desabilitar
3. Desmarcar "Use Default" no campo Status
4. Colocar Status = **Disabled**
5. Salvar

O produto continua **enabled** nas outras Store Views.

### Preço diferente por Website (com Price Scope = Website)

```php
// Setar preço para Website específico via REST API
// PUT /V1/products/:sku
{
  "product": {
    "sku": "my-sku",
    "price": 99.90,
    "extension_attributes": {
      "website_ids": [1]
    }
  }
}
```

Ou via admin: Catalog → Products → [produto] → Advanced Pricing → mudar o scope no dropdown antes de salvar.

---

## O que NUNCA muda de escopo

| Item | Escopo | Imutável? |
|---|---|---|
| SKU | Global | ✅ Sempre global |
| Attribute code | Global | ✅ Sempre global |
| Attribute Set | Global | ✅ Sempre global |
| Category ID | Global | ✅ O ID é global |
| Product ID | Global | ✅ O ID é global |
| Tax Class | Global | ✅ Sempre global |

> **Armadilha:** "SKU diferente por store" → **impossível por design**. SKU é identificador único global. Se a necessidade é ter "produtos diferentes" por loja, são produtos diferentes com SKUs diferentes atribuídos a Websites/categorias diferentes.
