# DI & Plugins

> **Domínio 1 — Arquitetura (52%)** &nbsp;·&nbsp; Seções 1.2, 1.3, 1.4

---

## Como funciona o DI

O Magento usa um container de DI que injeta dependências automaticamente via construtor. Nunca use `new ClassName()` para classes injetáveis — tudo vem pelo construtor.

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Model;

use Magento\Catalog\Api\ProductRepositoryInterface;
use Psr\Log\LoggerInterface;

class MyService
{
    public function __construct(
        private readonly ProductRepositoryInterface $productRepository,
        private readonly LoggerInterface $logger
    ) {}
}
```

---

## Tipos de Configuração em di.xml

### Preference

Substitui **completamente** uma classe ou interface por outra implementação.

```xml
<preference for="Magento\Catalog\Api\ProductRepositoryInterface"
            type="Vendor\Module\Model\ProductRepository"/>
```

> **Risco:** pode quebrar compatibilidade com outros módulos que também usam Preference para a mesma interface. Use como **último recurso** — prefira Plugin ou Observer.

---

### Plugin (Interceptor)

Intercepta chamadas a métodos públicos sem substituir a classe original.

```xml
<!-- etc/di.xml -->
<type name="Magento\Catalog\Model\Product">
    <plugin name="vendor_module_product_plugin"
            type="Vendor\Module\Plugin\ProductPlugin"
            sortOrder="10"
            disabled="false"/>
</type>
```

**Tipos de método:**

| Tipo | Assinatura | O que faz |
|---|---|---|
| `beforeMethod` | `before` + nome do método (PascalCase) | Executa antes, pode **modificar argumentos** |
| `afterMethod` | `after` + nome do método | Executa depois, pode **modificar o retorno** |
| `aroundMethod` | `around` + nome do método | Envolve toda a execução, decide se o original roda |

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Plugin;

use Magento\Catalog\Model\Product;

class ProductPlugin
{
    // Before: retorna array com os novos argumentos (ou null para não alterar)
    public function beforeSetName(Product $subject, string $name): array
    {
        return [strtoupper($name)];
    }

    // After: recebe e retorna o resultado do método original
    public function afterGetName(Product $subject, string $result): string
    {
        return $result . ' (modificado)';
    }

    // Around: decide se chama $proceed() — o método original
    // Product::save() não tem argumentos — correto sem parâmetros extras
    public function aroundSave(Product $subject, callable $proceed): mixed
    {
        // lógica antes
        $result = $proceed();
        // lógica depois
        return $result;
    }

    // Around em método COM argumentos: devem ser declarados E repassados
    // Exemplo: interceptando um método fictício execute(int $id, string $note)
    public function aroundExecute(
        Product $subject,
        callable $proceed,
        int $id,       // <- argumento original do método
        string $note   // <- argumento original do método
    ): bool {
        // lógica antes
        $result = $proceed($id, $note); // <- DEVE repassar os argumentos
        // lógica depois
        return $result;
    }
}
```

> **Após criar um Plugin:** rodar `bin/magento setup:di:compile`

---

### Virtual Type

Cria uma "instância configurada" de uma classe existente **sem criar nova classe PHP**. Útil para reutilizar a mesma implementação com parâmetros diferentes.

```xml
<virtualType name="Vendor\Module\Model\CustomLogger"
             type="Magento\Framework\Logger\Monolog">
    <arguments>
        <argument name="name" xsi:type="string">custom_channel</argument>
    </arguments>
</virtualType>

<!-- Injetar o virtual type em outra classe -->
<type name="Vendor\Module\Model\MyService">
    <arguments>
        <argument name="logger" xsi:type="object">Vendor\Module\Model\CustomLogger</argument>
    </arguments>
</type>
```

---

### Arguments — Injeção de Parâmetros

```xml
<type name="Vendor\Module\Model\MyClass">
    <arguments>
        <argument name="myString"  xsi:type="string">valor</argument>
        <argument name="isEnabled" xsi:type="boolean">true</argument>
        <argument name="maxItems"  xsi:type="number">100</argument>
        <argument name="myArray"   xsi:type="array">
            <item name="key1" xsi:type="string">value1</item>
        </argument>
    </arguments>
</type>
```

---

## Quando Usar Cada Mecanismo

| Situação | Mecanismo correto |
|---|---|
| Modificar comportamento de método público | **Plugin** |
| Substituir implementação de interface | **Preference** (último recurso) |
| Reagir a um evento sem retorno | **Observer** |
| Mesma classe com configuração diferente | **Virtual Type** |
| Método é `private`, `final` ou `static` | Plugin **NÃO funciona** → Preference |
| Lógica deve rodar após qualquer save de produto | **Observer** (`catalog_product_save_after`) |
| Precisa modificar o retorno de um getter | **Plugin** (after) |

---

## Ordem de preferência de extensibilidade

```
Plugin → Observer → Preference
```

> Preference é sempre o último recurso porque substitui completamente a implementação e pode entrar em conflito com outros módulos.

---

## Observers e Events

### Como Funciona

O `EventManager::dispatch()` emite eventos nomeados. Observers são ouvintes desacoplados que reagem a esses eventos.

```xml
<!-- etc/frontend/events.xml ou etc/events.xml -->
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Event/etc/events.xsd">
    <event name="catalog_product_save_after">
        <observer name="vendor_module_product_save"
                  instance="Vendor\Module\Observer\ProductSaveObserver"/>
    </event>
</config>
```

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Observer;

use Magento\Framework\Event\ObserverInterface;
use Magento\Framework\Event\Observer;

class ProductSaveObserver implements ObserverInterface
{
    public function execute(Observer $observer): void
    {
        $product = $observer->getData('product');
        // sua lógica aqui — sem retorno de valor
    }
}
```

---

## Eventos Mais Comuns

> Estes eventos são frequentemente cobrados na prova:

| Evento | Quando dispara |
|---|---|
| `catalog_product_save_before` | Antes de salvar produto |
| `catalog_product_save_after` | Depois de salvar produto |
| `catalog_product_delete_before` | Antes de deletar produto |
| `checkout_cart_add_product_complete` | Produto adicionado ao carrinho |
| `sales_order_place_after` | Pedido finalizado |
| `customer_login` | Cliente faz login |
| `customer_register_success` | Cliente criado com sucesso |
| `controller_action_predispatch` | Antes de qualquer action de controller |
| `cms_page_render` | Antes de renderizar página CMS |

---

## DI por Área — Precedência

Quando o mesmo plugin/configuração está em `etc/di.xml` **e** em `etc/frontend/di.xml`:

> **Area-specific configuration overrides global configuration.**

```
etc/di.xml                ← aplica a TODAS as áreas (global)
etc/frontend/di.xml       ← sobrescreve para área frontend
etc/adminhtml/di.xml      ← sobrescreve para área adminhtml
```

Para plugins que devem rodar **apenas em admin:**
```
<module>/etc/adminhtml/di.xml   ← correto
<module>/etc/admin/di.xml       ← não existe
<module>/etc/backend/di.xml     ← não existe
```

---

## Desativar um Plugin

```xml
<!-- Correto: disabled="true" -->
<type name="Vendor\Module\Model\Service">
    <plugin name="myPlugin" disabled="true"/>
</type>

<!-- Incorreto — atributos que NÃO existem: -->
<!-- active="false"   ← não reconhecido -->
<!-- status="disabled"← não reconhecido -->
```

> O que acontece quando `disabled="true"`: o **DI system ignora completamente a execução** do plugin. Não é "carregado mas inativo" — é completamente pulado.

**Atributos válidos de `<plugin>`:**

| Atributo | Valores | Uso |
|---|---|---|
| `name` | string | Identificador único (obrigatório) |
| `type` | class FQCN | Classe do plugin (obrigatório) |
| `sortOrder` | int | Ordem de execução entre plugins |
| `disabled` | `true`/`false` | Desativar sem remover código |

---

## cron:install — O que faz

```bash
bin/magento cron:install
```

> Adiciona os jobs de cron do Commerce à **crontab do servidor**, **dentro de marcadores** `#~ MAGENTO START` e `#~ MAGENTO END`.

**Não** executa tarefas — isso é `cron:run`.
**Não** remove cron jobs existentes — preserva tudo fora dos marcadores MAGENTO.

```bash
# Atualizar após mudanças no crontab.xml
bin/magento cron:install --mode=update

# Resultado em /etc/crontab ou crontab -l:
#~ MAGENTO START <hash>
* * * * * /usr/bin/php /var/www/html/bin/magento cron:run 2>&1
* * * * * /usr/bin/php /var/www/html/update/cron.php 2>&1
#~ MAGENTO END <hash>
# (outros jobs do sistema ficam intactos)
```

---

## CRON

### Declarar um Job em crontab.xml

```xml
<!-- etc/crontab.xml -->
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:module:Magento_Cron:etc/crontab.xsd">
    <group id="default">
        <job name="vendor_module_daily_sync"
             instance="Vendor\Module\Cron\DailySync"
             method="execute">
            <schedule>0 2 * * *</schedule> <!-- todo dia às 02:00 -->
        </job>
    </group>
</config>
```

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Cron;

use Psr\Log\LoggerInterface;

class DailySync
{
    public function __construct(
        private readonly LoggerInterface $logger
    ) {}

    public function execute(): void
    {
        $this->logger->info('DailySync started');
        // lógica do job
    }
}
```

### Grupos de Cron

| Grupo | Finalidade |
|---|---|
| `default` | Jobs gerais da aplicação |
| `index` | Indexação de dados |
| `catalog_event` | Eventos de catálogo agendados |
| `consumers` | Message queue consumers |

> Para rodar um grupo específico: `bin/magento cron:run --group=default`

---

## Factory e Proxy — Gerados Automaticamente

Você **não precisa declarar** Factory ou Proxy em `di.xml`. Basta type-hintar com o sufixo correto:

| Sufixo | O que faz | Quando usar |
|---|---|---|
| `ClassNameFactory` | Cria nova instância de `ClassName` | Dentro de loops, múltiplas instâncias |
| `ClassNameProxy` | Instanciação lazy (atrasa até primeiro uso) | Dependência pesada raramente usada |

```php
use Magento\Catalog\Api\Data\ProductInterfaceFactory;
use Magento\Catalog\Model\ProductRepository;
use Magento\Catalog\Model\ProductRepositoryProxy; // lazy load

class MyService
{
    public function __construct(
        private readonly ProductInterfaceFactory $productFactory,   // cria instâncias
        private readonly ProductRepositoryProxy $repositoryProxy    // lazy: só instancia quando usado
    ) {}

    public function doWork(): void
    {
        $product = $this->productFactory->create(); // nova instância
        $product->setName('Test');
    }
}
```

> **Gerado em:** `setup:di:compile` → diretório `generated/code/`.  
> **Armadilha:** Usar `new Product()` diretamente é proibido para classes injetáveis — use a Factory.

---

## Plugins — Limitações Completas

Plugins **não funcionam** em:

| Situação | Motivo |
|---|---|
| Métodos `final` | Não podem ser sobrescritos |
| Métodos `private` | Não visíveis externamente |
| Métodos `static` | Sem polimorfismo de instância |
| Construtores `__construct` | DI não intercepta |
| Classes com `final` na declaração | Não podem ter subclasses (interceptors) |
| Virtual Types | Não são classes reais, não geram interceptors |

> **Regra do exame:** Se precisar interceptar um método `final`, `private`, `static` ou o `__construct` → use **Preference** (último recurso).

---

## sortOrder — Ordem de Execução entre Plugins

Quando múltiplos plugins interceptam o mesmo método:

```xml
<type name="Magento\Catalog\Model\Product">
    <plugin name="plugin_a" type="..." sortOrder="10"/>
    <plugin name="plugin_b" type="..." sortOrder="20"/>
    <plugin name="plugin_c" type="..." sortOrder="10"/> <!-- mesmo sortOrder: ordem indeterminada -->
</type>
```

**Ordem de execução:**

```
before (sortOrder ASC) → método original → after (sortOrder DESC)
```

| Tipo | Execução |
|---|---|
| `before` | Menor sortOrder executa **primeiro** |
| `after` | Menor sortOrder executa **por último** (reverso) |
| `around` | Menor sortOrder é o mais externo |

> `around` com sortOrder 10 envolve o `around` com sortOrder 20: `A_before → B_before → original → B_after → A_after`

---

## Desabilitar Plugin de Outro Módulo

Para desativar um plugin de terceiro sem remover o código:

```xml
<!-- seu módulo: etc/di.xml -->
<type name="Magento\Catalog\Model\Product">
    <plugin name="nome_exato_do_plugin_alvo" disabled="true"/>
</type>
```

> O `name` deve ser exatamente o mesmo definido pelo módulo original. Se errar o nome, o Magento simplesmente ignora — não desativa nada e não dá erro.
