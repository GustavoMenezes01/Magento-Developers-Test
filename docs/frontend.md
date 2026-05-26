# Frontend & Admin

> **Domínio 1 — Arquitetura (52%)** &nbsp;·&nbsp; Layout XML, UI Components, Traduções, Rotas

---

## Layout XML — Nomenclatura

O nome do ficheiro segue a rota: `controller_action_method.xml`

| Página | Ficheiro layout |
|---|---|
| Checkout (main) | `checkout_index_index.xml` |
| Carrinho | `checkout_cart_index.xml` |
| PDP (produto) | `catalog_product_view.xml` |
| Listagem de categoria | `catalog_category_view.xml` |
| Homepage | `cms_index_index.xml` |
| Customer account | `customer_account_index.xml` |

> **Área** é determinada pelo **diretório** (`view/frontend/layout/` vs `view/adminhtml/layout/`), **não** pelo nome do ficheiro.

```
view/
├── frontend/
│   └── layout/
│       ├── checkout_index_index.xml     ← frontend area
│       └── catalog_product_view.xml
└── adminhtml/
    └── layout/
        └── sales_order_index.xml        ← admin area
```

---

## UI Components — Estrutura de Diretórios

```
view/
├── adminhtml/
│   └── ui_component/
│       └── company_entity_listing.xml   ← admin UI component
└── frontend/
    └── ui_component/
        └── my_widget.xml                ← frontend UI component
```

> O **nome do ficheiro** deve ser **exatamente igual** ao nome do componente referenciado no layout XML.

```xml
<!-- layout: company_entity_index.xml -->
<uiComponent name="company_entity_listing"/>

<!-- → ficheiro deve ser: view/adminhtml/ui_component/company_entity_listing.xml -->
```

---

## Admin Configuration (system.xml)

### Estrutura obrigatória em system.xml

Três elementos hierárquicos obrigatórios para os campos renderizarem:

```
section → group → field
```

```xml
<!-- etc/adminhtml/system.xml — define a ESTRUTURA dos campos -->
<config>
    <system>
        <section id="my_section" showInDefault="1" showInWebsite="1" showInStore="1">
            <label>My Section</label>
            <group id="general" showInDefault="1" showInWebsite="1" showInStore="1">
                <label>General</label>
                <field id="enabled" type="select" showInDefault="1" showInWebsite="0" showInStore="0">
                    <label>Enabled</label>
                    <source_model>Magento\Config\Model\Config\Source\Yesno</source_model>
                </field>
            </group>
        </section>
    </system>
</config>
```

```xml
<!-- etc/config.xml — define os VALORES PADRÃO (default values) -->
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

| Ficheiro | Propósito |
|---|---|
| `etc/adminhtml/system.xml` | Define estrutura, labels, tipos dos campos |
| `etc/config.xml` | Define **valores padrão** dos campos |
| `etc/adminhtml/config.xml` | **NÃO existe** — armadilha frequente no exame |
| `etc/system.xml` | **NÃO existe** — location errada |

### Regra de Scoping

> **Child elements não podem ser mais restritivos que o parent.**

Se a `<section>` tem `showInDefault="0"`, nenhum `<field>` dentro dela pode usar `showInDefault="1"`.

| Objetivo | Configuração |
|---|---|
| Apenas global | `showInDefault="1" showInWebsite="0" showInStore="0"` |
| Apenas website | `showInDefault="0" showInWebsite="1" showInStore="0"` — seção, grupo E campo todos com mesmo scope |
| Todos os scopes | `showInDefault="1" showInWebsite="1" showInStore="1"` |

---

## Ficheiros de Configuração Importantes

| Ficheiro | O que contém | No git? |
|---|---|---|
| `app/etc/env.php` | DB credentials, chaves criptográficas, Redis config | **Não** (sensível) |
| `app/etc/config.php` | Módulos habilitados, estado de configuração compilada | Sim |
| `app/etc/di.xml` | DI global (não existe como ficheiro padrão isolado) | — |
| `app/etc/config.xml` | **NÃO existe** no Magento 2 | — |

```php
// app/etc/env.php — gerado durante a instalação
return [
    'db' => [
        'host'     => 'localhost',
        'dbname'   => 'magento',
        'username' => 'magento_user',
        'password' => 'secret',
    ],
    'crypt' => ['key' => '...'],
    'cache' => ['frontend' => ['default' => ['backend' => 'Cm_Cache_Backend_Redis']]],
];
```

---

## Entry Points e Routing

| Entry point | Área |
|---|---|
| `pub/index.php` | **Frontend e Admin** (único entry point) |
| `app/bootstrap.php` | Bootstrapping da aplicação (requerido pelo entry point) |
| ~~`admin/index.php`~~ | **Não existe** — armadilha frequente |

> Admin routes são tratadas via o **mesmo entry point** (`pub/index.php`) com base na URL configurada. Não há ficheiro `admin/index.php`.

---

## Traduções em PHP

```php
// Correto
$message = __('Welcome to our store');
$message = __('Could not save record: %1', $error);

// O que __() faz: passa a string pelo translation system (Magento\Framework\Phrase)
// Retorna a string traduzida conforme o locale atual
```

**Classe responsável:** `\Magento\Framework\Phrase`

### CSV de traduções

```csv
"Welcome to our store","Bem-vindo à nossa loja"
"Could not save record: %1","Não foi possível salvar o registro: %1"
```

---

## Traduções em JavaScript

```javascript
// CORRETO — método oficial e documentado
var text = $.mage.__('Add to Cart');

// NÃO são funções oficiais do Magento core:
// $.t('text')        ← não existe no core
// $translate('text') ← não existe no core
// Magento.__()       ← não existe
// Magento.translate()← não existe
```

> `$.t()` e `$translate()` podem ser aliases criados por convenção em projetos, mas **não são funções oficiais** do sistema de tradução do Magento.

---

## Workflow de Internacionalização (i18n)

Ordem obrigatória:

```bash
# 1. Extrair todas as frases traduzíveis do módulo/tema
bin/magento i18n:collect-phrases app/code/Vendor/Module -o phrases.csv

# 2. Traduzir o CSV (manualmente ou com ferramenta)
# Editar phrases.csv com as traduções

# 3. Criar o pacote de tradução
bin/magento i18n:pack phrases.csv -d pt_BR

# 4. Publicar o conteúdo estático com as traduções
bin/magento setup:static-content:deploy pt_BR -f
```

| Comando | O que faz | Ordem |
|---|---|---|
| `i18n:collect-phrases` | **Extrai** frases traduzíveis do código | 1º |
| `i18n:pack` | **Cria pacote** a partir das traduções | 2º |
| `setup:static-content:deploy` | **Publica** assets incluindo traduções | 3º |
| `cache:clean` | Invalida cache de tradução | após tudo |

---

## Layered Navigation (Navegação Filtrada)

### Para ativar na categoria

> Seção de categoria no Admin → **Anchor: Yes**

Anchor = "Yes" combina produtos da categoria e das sub-categorias. Ativa os filtros de atributos na lateral.

### Para um atributo aparecer como filtro

> No admin do atributo: **Use in Layered Navigation** → `Filterable (with results)`

| Opção | Comportamento |
|---|---|
| `No` | Não aparece como filtro |
| `Filterable (with results)` | Aparece, mostra contagem de resultados |
| `Filterable (no results)` | Aparece mesmo sem resultados |

---

## Product Recommendations (PDP vs Cart)

| Tipo | Onde aparece | Objetivo |
|---|---|---|
| **Related products** | PDP (product detail page) | Mostrar produtos similares |
| **Up-sell products** | PDP | Sugerir alternativa premium |
| **Cross-sell products** | Página do **carrinho** | Aumentar ticket médio |

> **Página do produto por padrão:** Related + Up-sell. **Carrinho:** Cross-sell.
