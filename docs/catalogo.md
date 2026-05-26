# Catálogo & Sales

> **Domínio 2 — Customizações (36%)** &nbsp;·&nbsp; Seções 2.1, 2.2, 2.5

---

## Tipos de Produto

| Tipo | Uso | Tem estoque físico? |
|---|---|---|
| **Simple** | Produto básico com SKU único | Sim |
| **Configurable** | Produto com variações (cor, tamanho) — filhos são Simples | Sim (via simples) |
| **Grouped** | Exibe grupo de produtos simples na mesma página | Sim |
| **Bundle** | Kit customizável — cliente escolhe os componentes | Sim |
| **Virtual** | Serviço, assinatura, garantia — sem envio físico | Não |
| **Downloadable** | Arquivo digital para download | Não |

> **Atenção:** No produto Configurable, o estoque está nos filhos (Simples), não no pai.

---

## Criar Produto Programaticamente

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Service;

use Magento\Catalog\Api\Data\ProductInterfaceFactory;
use Magento\Catalog\Api\ProductRepositoryInterface;
use Magento\Catalog\Model\Product\Attribute\Source\Status;
use Magento\Catalog\Model\Product\Type;
use Magento\Catalog\Model\Product\Visibility;

class ProductCreator
{
    public function __construct(
        private readonly ProductInterfaceFactory $productFactory,
        private readonly ProductRepositoryInterface $productRepository
    ) {}

    public function create(): void
    {
        $product = $this->productFactory->create();
        $product->setSku('my-sku-001');
        $product->setName('My Product');
        $product->setPrice(29.99);
        $product->setStatus(Status::STATUS_ENABLED);
        $product->setVisibility(Visibility::VISIBILITY_BOTH);
        $product->setTypeId(Type::TYPE_SIMPLE);
        $product->setAttributeSetId(4); // Default attribute set
        $product->setStockData(['qty' => 100, 'is_in_stock' => 1]);

        $this->productRepository->save($product);
    }
}
```

---

## Attribute Types

| Input Type | Backend Type | Uso |
|---|---|---|
| `text` | `varchar` | Texto curto |
| `textarea` | `text` | Texto longo |
| `select` | `int` | Dropdown (single value) |
| `multiselect` | `varchar` | Multi-seleção |
| `boolean` | `int` | Sim/Não |
| `price` | `decimal` | Preço |
| `date` | `datetime` | Data |
| `media_image` | `varchar` | Imagem |

---

## Fluxo de Pedido

```
Quote (carrinho ativo)
  └── Order (pedido confirmado)
        ├── Invoice  (fatura / captura de pagamento)
        ├── Shipment (envio / tracking)
        └── Credit Memo (devolução / reembolso)
```

---

## Quote vs Order

| Aspecto | Quote | Order |
|---|---|---|
| Tabela principal | `quote` | `sales_order` |
| Itens | `quote_item` | `sales_order_item` |
| Endereço | `quote_address` | `sales_order_address` |
| Quando existe | Durante o checkout | Após finalização |
| Estado | Ativo / Inativo | `pending`, `processing`, etc. |

---

## Order States e Statuses

| State | Statuses possíveis |
|---|---|
| `new` | `pending`, `pending_payment` |
| `pending_payment` | `pending_payment` |
| `processing` | `processing` |
| `complete` | `complete` |
| `closed` | `closed` |
| `canceled` | `canceled` |
| `holded` | `holded` |

> **State** é o estado interno do sistema (fixo). **Status** é o rótulo visível configurável por loja.

---

## Customizar Checkout

### Adicionar Step Customizado

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
                                    <item name="isVisible" xsi:type="boolean">true</item>
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

---

## Total Collectors

Usados para adicionar linhas customizadas ao sumário do carrinho (ex.: taxa, desconto especial).

```xml
<!-- etc/sales.xml -->
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:module:Magento_Sales:etc/sales.xsd">
    <section name="quote">
        <group name="totals">
            <item name="my_custom_fee"
                  instance="Vendor\Module\Model\Quote\Total\CustomFee"
                  sort_order="450"/>
        </group>
    </section>
</config>
```

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Model\Quote\Total;

use Magento\Quote\Api\Data\ShippingAssignmentInterface;
use Magento\Quote\Model\Quote;
use Magento\Quote\Model\Quote\Address\Total;
use Magento\Quote\Model\Quote\Address\Total\AbstractTotal;

class CustomFee extends AbstractTotal
{
    public function collect(
        Quote $quote,
        ShippingAssignmentInterface $shippingAssignment,
        Total $total
    ): self {
        parent::collect($quote, $shippingAssignment, $total);

        $fee = 5.00;
        $total->addTotalAmount($this->getCode(), $fee);
        $total->addBaseTotalAmount($this->getCode(), $fee);

        return $this;
    }
}
```

---

## Customer Programaticamente

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Service;

use Magento\Customer\Api\CustomerRepositoryInterface;
use Magento\Customer\Api\Data\CustomerInterfaceFactory;
use Magento\Framework\Encryption\EncryptorInterface;

class CustomerCreator
{
    public function __construct(
        private readonly CustomerInterfaceFactory $customerFactory,
        private readonly CustomerRepositoryInterface $customerRepository,
        private readonly EncryptorInterface $encryptor
    ) {}

    public function create(): void
    {
        $customer = $this->customerFactory->create();
        $customer->setEmail('novo@email.com');
        $customer->setFirstname('João');
        $customer->setLastname('Silva');
        $customer->setWebsiteId(1);
        $customer->setStoreId(1);

        $hashedPassword = $this->encryptor->getHash('Senha@123', true);
        $this->customerRepository->save($customer, $hashedPassword);
    }
}
```

---

## SearchCriteria — AND vs OR

Múltiplos `addFilter()` = condição **AND**. Para **OR**, os filtros precisam estar no mesmo `FilterGroup`.

```php
// AND: produtos com status=1 E type_id='simple'
$criteria = $this->searchCriteriaBuilder
    ->addFilter('status', 1)
    ->addFilter('type_id', 'simple')
    ->create();

// OR: produtos com status=1 OU status=2
$filterEnabled  = $this->filterBuilder->setField('status')->setValue(1)->setConditionType('eq')->create();
$filterDisabled = $this->filterBuilder->setField('status')->setValue(2)->setConditionType('eq')->create();
$group = $this->filterGroupBuilder->setFilters([$filterEnabled, $filterDisabled])->create();
$criteria = $this->searchCriteriaBuilder->setFilterGroups([$group])->create();

// AND entre grupos, OR dentro de cada grupo
// Grupo 1: (status=1 OR status=2) AND Grupo 2: (type_id='simple' OR type_id='virtual')
```

> **Regra:** Filtros em `FilterGroup` **diferentes** = AND entre grupos. Filtros no **mesmo** `FilterGroup` = OR entre eles.

---

## Extension Attributes vs EAV

| | EAV Attributes | Extension Attributes |
|---|---|---|
| Tipos suportados | **Primitivos** (varchar, int, decimal, datetime, text) | **Arrays e objetos** (estruturas complexas) |
| Onde são usados | Admin UI, frontend, queries normais | **Service contracts e APIs** |
| Como adicionar | Data Patch + `addAttribute()` | `extension_attributes.xml` |
| Contexto | Produtos, categorias, clientes | Qualquer entidade com service contract |

> EAV = primitivos. Extension Attributes = complexos (arrays/objects). Pergunta frequente sobre qual usar.

```xml
<!-- etc/extension_attributes.xml -->
<config>
    <extension_attributes for="Magento\Sales\Api\Data\OrderInterface">
        <attribute code="custom_data" type="string"/>
    </extension_attributes>
</config>
```

---

## Customer Attributes via CustomerSetup

Para criar atributos de clientes em Data Patch, usar **`Magento\Customer\Setup\CustomerSetup`**:

```php
use Magento\Customer\Setup\CustomerSetup;
use Magento\Customer\Setup\CustomerSetupFactory;

class AddCustomAttribute implements DataPatchInterface
{
    public function __construct(
        private readonly CustomerSetupFactory $customerSetupFactory,
        private readonly ModuleDataSetupInterface $moduleDataSetup
    ) {}

    public function apply(): self
    {
        $customerSetup = $this->customerSetupFactory->create(['setup' => $this->moduleDataSetup]);

        // Método correto: addAttribute()
        $customerSetup->addAttribute(
            \Magento\Customer\Model\Customer::ENTITY,
            'custom_field',
            [
                'type'       => 'varchar',
                'label'      => 'Custom Field',
                'input'      => 'text',
                'required'   => false,
                'visible'    => true,
                'user_defined' => true,
                'position'   => 999,
                'system'     => false,
            ]
        );
        return $this;
    }
}
```

**Métodos corretos vs errados:**

| Método | Existe? |
|---|---|
| `addAttribute()` | ✅ Correto |
| `createAttribute()` | ❌ Não existe |
| `installAttribute()` | ❌ Não existe |
| `saveAttribute()` | ❌ Não existe |

> **Não** usar `db_schema.xml` para adicionar colunas ao `customer_entity` — isso bypassa o sistema EAV, que foi feito para dar flexibilidade nos atributos e integração com o Admin.

---

## Precificação

| Feature | Descrição |
|---|---|
| **Tier price** | Desconto por quantidade — preço por unidade **diminui** conforme quantidade **aumenta** |
| **Group price** | Preço específico por **customer group** (ex: Wholesale, Retail) |
| **Special price** | Preço promocional temporário com data de início/fim |
| **Bundle price** | Preço calculado dinamicamente baseado nos componentes escolhidos |
| **Volume price** | **Não existe** no Adobe Commerce out-of-the-box — armadilha do exame |

---

## Magento_QuoteConfigurable vs QuoteConfigurableOptions

| Módulo | Função |
|---|---|
| `Magento_QuoteConfigurable` | Fornece **extension points** e suporte para funcionalidade de produto configurável no quote |
| `Magento_QuoteConfigurableOptions` | **Armazena e gerencia** as seleções de opções do produto configurável no quote |

> Pergunta frequente: "Qual módulo **armazena** as seleções?" → `Magento_QuoteConfigurableOptions`

---

## URL Rewrites — Configurações SEO

| Configuração | Local | Efeito |
|---|---|---|
| **Use Categories Path for Product URLs** | Catalog > SEO | `No` = produto tem URL única sem path de categoria (evita duplicate content) |
| **Product URL Suffix** | Catalog > SEO | Muda apenas a extensão (`.html`) — **não afeta** se o category path é incluído |
| **Add Store Code to URLs** | General > Web | Adiciona/remove o código de store da URL |

> **Armadilha:** "Product URL Suffix" e "Use Categories Path" são configurações **independentes**.
> Mudar o Suffix não resolve URLs duplicadas por categoria.

---

## Customer Segmentation — Campos Disponíveis

| Campo | Disponível para segmentação? |
|---|---|
| Email | ✅ Sim |
| First Name | ✅ Sim |
| Date of Birth | ✅ Sim |
| Purchase Total | ✅ Sim (aggregate value) |
| **Password** | ❌ **Não** — campo sensível, nunca exposto |

---

## Criar Invoice Programaticamente

```php
// Criar invoice a partir de um order
$invoice = $this->invoiceService->prepareInvoice($order);
$invoice->setRequestedCaptureCase(\Magento\Sales\Model\Order\Invoice::CAPTURE_ONLINE);
$invoice->register();

$transaction = $this->transactionFactory->create()
    ->addObject($invoice)
    ->addObject($order);
$transaction->save();
```
