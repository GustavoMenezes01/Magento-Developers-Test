# Produtos — Cenários & Detalhes

> **Domínio 2 — Customizações (36%)** &nbsp;·&nbsp; Referência completa de tipos, atributos, preços e situações reais

---

## Cenários Rápidos — "O cliente quer..."

| O cliente quer... | Solução |
|---|---|
| Produto com opções de cor e tamanho (cada combinação tem SKU próprio) | **Configurable product** |
| Montar um kit onde o cliente escolhe os componentes | **Bundle product** |
| Mostrar vários produtos simples juntos numa página, vendidos individualmente | **Grouped product** |
| Vender um serviço ou assinatura sem envio físico | **Virtual product** |
| Vender um arquivo para download (PDF, software) | **Downloadable product** |
| Desconto por quantidade (compra 5, paga menos por unidade) | **Tier price** |
| Preço diferente para clientes Wholesale vs Retail | **Group price** |
| Promoção temporária com preço especial por datas | **Special price** |
| Filtros de atributo na listagem de categoria | **Layered navigation** (Anchor + Filterable) |
| Campo personalizado visível na API REST | **EAV attribute** com `is_visible=true` |
| Campo com estrutura complexa (array/objeto) na API | **Extension attribute** |
| Vídeo na galeria do produto | YouTube API key + product edit |
| Produtos relacionados na PDP | **Related products** |
| Sugerir upgrade mais caro na PDP | **Up-sell products** |
| Mostrar complementos na página do carrinho | **Cross-sell products** |
| Criar atributo que aparece nos filtros de regra de promoção | `Use for Promo Rule Conditions = Yes` |
| Atributo visível apenas no admin | `visible = true`, `visible_on_front = false` |
| Atributo visível no frontend (conta do cliente) | `visible_on_front = true` |

---

## Tipos de Produto — Comparação Detalhada

### Simple

- SKU único, estoque direto
- Base para todos os outros tipos
- Pode ser filho de Configurable ou componente de Bundle/Grouped

### Configurable

- Tem **variações** baseadas em atributos (cor, tamanho, material)
- Os filhos são produtos **Simple** com SKU próprio e estoque próprio
- O pai (Configurable) **não tem estoque direto** — o estoque está nos filhos
- O cliente seleciona a variação e compra o Simple correspondente

**Requisitos do Super Attribute (atributo de variação):**

| Requisito | Valor | Motivo |
|---|---|---|
| `scope` | **Global** | Scope Website/Store View → não aparece como opção de variação |
| `input_type` | **`select`** | `text`, `multiselect`, `boolean` não funcionam |
| `visual_swatch` / `text_swatch` | ✅ Também funcionam | São select com visualização especial |

> **Armadilha:** atributo criado com scope "Store View" não aparece na tela de configuração do produto Configurable — e não gera erro, simplesmente some da lista.

```
Camiseta Azul (Configurable - sem estoque)
├── Camiseta Azul P  (Simple - SKU: CAM-AZL-P, qty: 10)
├── Camiseta Azul M  (Simple - SKU: CAM-AZL-M, qty: 5)
└── Camiseta Azul G  (Simple - SKU: CAM-AZL-G, qty: 0)
```

### Bundle

- Cliente **monta o kit** escolhendo entre opções pré-definidas
- Cada opção pode ter um ou mais produtos Simple ou Virtual para escolha
- Preço pode ser **fixo** (definido no Bundle) ou **dinâmico** (soma dos componentes)
- Seleção **não é baseada em atributos** como cor/tamanho — são produtos distintos

```
Kit PC Gamer (Bundle)
├── Opção "Monitor": [Monitor 24" ou Monitor 27" ou Monitor 32"]
├── Opção "Teclado":  [Teclado Mecânico ou Teclado Membrana]
└── Opção "Mouse":    [Mouse 1600dpi ou Mouse 3200dpi]
```

### Grouped

- Exibe vários produtos Simple na **mesma página**
- O cliente escolhe a **quantidade** de cada item individualmente
- **Não** há customização de opções — apenas qtd
- Cada produto mantém seu próprio preço e estoque

```
Kit Escritório (Grouped)
├── Mesa (Simple) — qty: [1]
├── Cadeira (Simple) — qty: [1]
└── Luminária (Simple) — qty: [2]
```

> **Bundle vs Grouped:** Bundle = cliente escolhe *quais* componentes. Grouped = cliente escolhe *quantos* de cada.

### Virtual

- Sem envio, sem peso, sem estoque físico
- Exemplos: consultoria, garantia estendida, assinatura, taxa de serviço
- Aparece no carrinho normalmente mas sem campo de endereço de entrega

### Downloadable

- Possui links de download (PDF, ZIP, MP3, software)
- Pode ter amostras (preview)
- Sem envio físico — o cliente recebe o link por email após o pagamento
- Pode limitar número de downloads e ter prazo de expiração

---

## Atributos — Tipos de Input

| Input Type | Backend Type | Uso | Multi-valor? |
|---|---|---|---|
| `text` | `varchar` | Texto curto (até 255 chars) | Não |
| `textarea` | `text` | Texto longo | Não |
| `select` | `int` | Dropdown — **uma opção** | Não |
| `multiselect` | `varchar` | Multi-seleção — **várias opções** | Sim |
| `boolean` | `int` | Sim/Não (0/1) | Não |
| `price` | `decimal` | Valores monetários | Não |
| `date` | `datetime` | Datas | Não |
| `media_image` | `varchar` | Imagem | Não |
| `visual_swatch` | `int` | Swatch visual (cor) — **uma opção** | Não |
| `text_swatch` | `int` | Swatch de texto — **uma opção** | Não |

> **Regra:** Dropdown, Visual Swatch, Text Swatch → **seleção única**. Multiselect → **múltipla seleção**.

---

## Atributos — Propriedades Importantes

| Propriedade | Efeito |
|---|---|
| `visible` | Aparece nos formulários do **admin** |
| `visible_on_front` | Aparece nas páginas de conta do **cliente** (frontend) |
| `searchable` | Incluído na busca fulltext |
| `filterable` | Disponível como filtro na **layered navigation** |
| `comparable` | Aparece na comparação de produtos |
| `used_for_promo_rules` / `Use for Promo Rule Conditions` | Disponível como condição em cart/catalog price rules |
| `is_visible_on_front` | Aparece na tab "More Information" da PDP |
| `used_in_product_listing` | Disponível em listagens sem carregar o produto completo |

---

## Attribute Sets

- Agrupam atributos em **grupos** (tabs no admin)
- Todo produto pertence a um Attribute Set
- O padrão é **"Default"** (ID 4)
- Produto Configurable cria atributos específicos para as variações

```
Attribute Set "Roupas"
├── Grupo "General": name, sku, price, status
├── Grupo "Dimensions": size, color, material
└── Grupo "SEO": url_key, meta_title, meta_description
```

---

## Preços — Todos os Tipos

### Tier Price (Preço por Quantidade)

> Preço **por unidade** diminui conforme a quantidade aumenta. O **total ainda cresce** — só o valor unitário cai.

**Armadilha de exame:**
```
Cart com 1 item  (R$20/un): total = R$20
Cart com 5 itens (R$15/un): total = R$75  ← total MAIOR, mas preço/un MENOR
```

| Pergunta do exame | Resposta correta |
|---|---|
| "O que acontece ao adicionar mais itens com tier pricing?" | **O preço por unidade diminui** |
| "O total diminui com mais itens?" | **Não** — o total ainda sobe |

```php
$product->setTierPrices([
    ['website_id' => 0, 'cust_group' => 0, 'price_qty' => 5,  'price' => 18.00],
    ['website_id' => 0, 'cust_group' => 0, 'price_qty' => 10, 'price' => 15.00],
    ['website_id' => 0, 'cust_group' => 0, 'price_qty' => 20, 'price' => 12.00],
]);
```

| Qty | Preço unit. |
|---|---|
| 1–4 | R$ 20,00 |
| 5–9 | R$ 18,00 |
| 10–19 | R$ 15,00 |
| 20+ | R$ 12,00 |

### Group Price

> Preço específico por **customer group**.

Configurado no produto → Advanced Pricing → Customer Group Price.

| Customer Group | Preço |
|---|---|
| General (público) | R$ 100,00 |
| Wholesale | R$ 80,00 |
| Retailer | R$ 90,00 |

### Special Price

> Promoção temporária com data de início/fim. Sobrescreve o preço base enquanto vigente.

```php
$product->setSpecialPrice(49.99);
$product->setSpecialFromDate('2026-06-01');
$product->setSpecialToDate('2026-06-30');
```

### Catalog Price Rule

> Aplica desconto automaticamente a grupos de produtos com base em condições (categoria, atributo, SKU).

- Configurado em **Marketing > Catalog Price Rules**
- Aplicado antes de o produto chegar ao carrinho
- Afeta o preço exibido na listagem e na PDP

### Cart Price Rule

> Desconto aplicado **no carrinho** com base em condições.

Condições disponíveis por padrão:
- **SKU** ✅
- **Price in cart** ✅
- **Quantity in cart** ✅
- ~~Description~~ ❌
- ~~Stock Status~~ ❌
- ~~Creation Date~~ ❌

> Para um atributo aparecer como condição: **"Use for Promo Rule Conditions" = Yes** no admin do atributo.

---

## Visibilidade do Produto

| Visibility value | Onde aparece |
|---|---|
| `Not Visible Individually` | Não aparece em listagens nem busca (usado para filhos de Configurable) |
| `Catalog` | Aparece em listagens de categoria, não na busca |
| `Search` | Aparece na busca, não em listagens |
| `Catalog, Search` | Aparece em todos os lugares |

```php
use Magento\Catalog\Model\Product\Visibility;

Visibility::VISIBILITY_NOT_VISIBLE  // 1
Visibility::VISIBILITY_IN_CATALOG   // 2
Visibility::VISIBILITY_IN_SEARCH    // 3
Visibility::VISIBILITY_BOTH         // 4
```

---

## Status do Produto

```php
use Magento\Catalog\Model\Product\Attribute\Source\Status;

Status::STATUS_ENABLED   // 1
Status::STATUS_DISABLED  // 2
```

---

## Criar Produto — Atributos Mínimos Obrigatórios

Para criar um produto Simple programaticamente sem erro de validação:

```php
$product->setSku('unique-sku');     // obrigatório — identifier único
$product->setName('Product Name');  // obrigatório
$product->setPrice(29.99);          // obrigatório para Simple
$product->setTypeId('simple');
$product->setAttributeSetId(4);     // Default = 4
```

> **SKU, Name e Price** são os 3 atributos mínimos obrigatórios para Simple. Sem SKU → validation error.

---

## Layered Navigation — Setup Completo

Para que os filtros de atributo apareçam na listagem de uma categoria:

**Passo 1 — Categoria como Anchor:**
> Admin → Catalog → Categories → [categoria] → **Is Anchor: Yes**

Anchor = combina produtos da categoria com produtos das sub-categorias.

**Passo 2 — Atributo como Filterable:**
> Admin → Stores → Attributes → Product → [atributo] → **Use in Layered Navigation: Filterable (with results)**

| Opção | Comportamento |
|---|---|
| `No` | Não aparece como filtro |
| `Filterable (with results)` | Aparece, oculta opções sem resultados |
| `Filterable (no results)` | Aparece mesmo que uma opção tenha 0 resultados |

---

## Vídeos na Galeria do Produto

**Setup:**
1. Stores → Configuration → Catalog → **Product Video** → inserir **YouTube API Key**
2. Catalog → Products → [editar produto] → Images and Videos → Add Video → colar URL do YouTube

> Sem a API key configurada, os thumbnails não são gerados.
> O Magento suporta YouTube nativamente. Vimeo não tem suporte nativo.

---

## Product Associations — Onde Aparece Cada Uma

| Tipo | Aba no admin | Onde aparece no storefront | Objetivo |
|---|---|---|---|
| **Related** | Product → Related Products | **PDP** (abaixo da descrição) | Mostrar produtos similares |
| **Up-sell** | Product → Up-sell Products | **PDP** (abaixo do bloco principal) | Sugerir produto melhor/mais caro |
| **Cross-sell** | Product → Cross-sell Products | **Página do carrinho** | Aumentar ticket médio |

> **PDP por padrão mostra:** Related + Up-sell.
> **Carrinho por padrão mostra:** Cross-sell.

---

## URL de Produto — Configurações SEO

| Config | Caminho | Efeito |
|---|---|---|
| **Use Categories Path for Product URLs** | Catalog → Search Engine Optimization | `No` → URL única sem path de categoria (evita duplicate content) |
| **Product URL Suffix** | Catalog → Search Engine Optimization | Muda a extensão (`.html`, vazio) — não afeta o path de categoria |
| **Save Rewrites History** | **Não existe** no Magento core | Armadilha de exame |

> **Problema:** produto acessível via `men/shirts/blue-shirt.html` E `blue-shirt.html` = duplicate content.
> **Solução:** "Use Categories Path for Product URLs" → **No**.

---

## Customer Segmentation com Produtos

Segmentos podem usar condições de **produto** e **carrinho**:

| Condição | Disponível? |
|---|---|
| Produtos no carrinho | ✅ |
| Histórico de compras | ✅ |
| Valor total de compras (aggregate) | ✅ |
| Date of Birth | ✅ |
| Email | ✅ |
| First Name | ✅ |
| **Password** | ❌ Nunca exposto |
| Stock Status | ❌ Não disponível em condições |
