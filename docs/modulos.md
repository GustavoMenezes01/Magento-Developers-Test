# Módulos & CLI

> **Domínio 1 — Arquitetura (52%)** &nbsp;·&nbsp; Seção 1.1

---

## Estrutura de Pastas

```
app/code/Vendor/ModuleName/
├── registration.php            ← OBRIGATÓRIO: registra o módulo
├── composer.json               ← dependências via Composer
├── etc/
│   ├── module.xml              ← declara nome, versão e sequência
│   ├── di.xml                  ← injeção de dependência global
│   ├── config.xml              ← valores padrão de configuração
│   ├── acl.xml                 ← permissões de ACL
│   ├── crontab.xml             ← jobs agendados
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
│   └── ResourceModel/Collection/
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
├── Api/                        ← Service Contracts (interfaces)
│   └── Data/                   ← Data Object Interfaces
└── etc/db_schema.xml           ← Declarative Schema (moderno)
```

---

## registration.php

**Obrigatório** — sem este arquivo o Magento ignora completamente o módulo.

```php
<?php
use Magento\Framework\Component\ComponentRegistrar;

ComponentRegistrar::register(
    ComponentRegistrar::MODULE,
    'Vendor_ModuleName',
    __DIR__
);
```

---

## module.xml

Declara o módulo e define a **sequência de carregamento** de dependências.

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

> `<sequence>` garante que os módulos listados sejam carregados **antes** do seu. Isso é diferente de dependência — não impede a instalação, apenas garante a ordem.

---

## Comandos CLI Essenciais

| Comando | O que faz |
|---|---|
| `bin/magento setup:upgrade` | Aplica novos módulos, patches e schema |
| `bin/magento setup:di:compile` | Compila o container de DI (proxies, factories, interceptors) |
| `bin/magento setup:static-content:deploy` | Publica arquivos estáticos (JS, CSS, imagens) |
| `bin/magento cache:flush` | **Apaga** todo o storage de cache |
| `bin/magento cache:clean` | Invalida entradas por tag (storage permanece) |
| `bin/magento module:enable Vendor_Name` | Habilita um módulo |
| `bin/magento module:disable Vendor_Name` | Desabilita um módulo |
| `bin/magento module:status` | Lista módulos habilitados/desabilitados |
| `bin/magento indexer:reindex` | Reindexa todos os indexers |
| `bin/magento indexer:status` | Mostra status dos indexers |
| `bin/magento cron:run` | Executa jobs de cron manualmente |
| `bin/magento deploy:mode:set developer` | Muda para modo developer |
| `bin/magento deploy:mode:set production` | Muda para modo production |
| `bin/magento deploy:mode:show` | Mostra o modo atual |

---

## Ordem Correta de Deploy

> Após instalar ou atualizar módulos **sempre** seguir esta ordem:

```bash
bin/magento setup:upgrade
bin/magento setup:di:compile
bin/magento setup:static-content:deploy pt_BR en_US -f
bin/magento cache:flush
```

| Etapa | Por que esta ordem? |
|---|---|
| `setup:upgrade` | Registra módulos e aplica patches — precisa rodar primeiro |
| `setup:di:compile` | Gera proxies e factories — precisa do estado pós-upgrade |
| `setup:static-content:deploy` | Publica assets — precisa da DI compilada |
| `cache:flush` | Garante que o cache reflita tudo que foi gerado |

---

## Modos de Operação

| Modo | Comportamento | Quando usar |
|---|---|---|
| `developer` | Erros visíveis, sem cache de template, geração dinâmica de código | Desenvolvimento local |
| `production` | Erros logados (não exibidos), assets pré-gerados, máxima performance | Produção |
| `default` | Híbrido — não recomendado | Instalação inicial |
