# Adobe Commerce Developer Professional

## AD0-E724 — Guia de Estudos

> **Exame:** AD0-E724 &nbsp;|&nbsp; **Questões:** 50 &nbsp;|&nbsp; **Tempo:** 100 min &nbsp;|&nbsp; **Aprovação:** 39/50 (78%) &nbsp;|&nbsp; **Custo:** $125

---

## Estrutura do Exame

| Domínio | Peso | ~Questões | Seção neste guia |
|---|---|---|---|
| 1 — Arquitetura | **52%** | ~26 | [Módulos](modulos), [DI & Plugins](di-plugins), [DB & Cache](database) |
| 2 — Customizações | **36%** | ~18 | [Catálogo & Sales](catalogo), [APIs](apis) |
| 3 — Cloud | **12%** | ~6 | [Cloud](cloud) |

---

## Como usar este guia

Navega pelas abas no topo para ir direto ao tema. A barra lateral mostra todos os subtópicos disponíveis. Use **Ctrl+K** (ou a caixa de busca) para encontrar qualquer conceito.

---

## Perguntas de Exemplo

### Arquitetura

**Q:** Um plugin `around` foi declarado em `Magento\Catalog\Model\Product`, mas nunca executa. Causa mais provável?

> **R:** O método interceptado é `final`, `private` ou `static`. Plugins só funcionam em métodos **públicos não-finais**. Solução: usar Preference.

---

**Q:** Diferença entre `cache:clean` e `cache:flush`?

> **R:** `cache:clean` invalida entradas por tag (storage permanece). `cache:flush` **apaga todo o storage**. Em produção com Redis compartilhado, prefira `cache:clean` para não afetar outros processos.

---

**Q:** Novo módulo está desabilitado. Sequência correta para ativá-lo?

> **R:**
> 1. `bin/magento module:enable Vendor_ModuleName`
> 2. `bin/magento setup:upgrade`
> 3. `bin/magento setup:di:compile`
> 4. `bin/magento cache:flush`

---

### Customizações

**Q:** Diferença entre `Observer` e `Plugin` ao modificar um save de produto?

> **R:** Plugin intercepta o método diretamente e pode **modificar argumentos e retorno**. Observer reage ao evento de forma desacoplada mas **não altera o fluxo** nem retorna valores. Use Plugin para controle; Observer para side-effects.

---

**Q:** Campo "Certificate Number" precisa aparecer no frontend e na API REST. Passos?

> **R:**
> 1. Criar atributo via Data Patch (tipo `varchar`)
> 2. Adicionar ao Attribute Set
> 3. API: atributo EAV já é exposto via `ProductInterface` se `is_visible = true`
> 4. Frontend: renderizar via layout XML no template do produto

---

### Cloud

**Q:** Como mudar a versão do PHP de 8.1 para 8.2 no Cloud?

> **R:** Editar `.magento.app.yaml`, alterar `type: php:8.1` → `type: php:8.2`, commitar e fazer push para o branch de integration.

---

## Links Oficiais

- [Developer Documentation](https://developer.adobe.com/commerce/docs/)
- [PHP Developer Guide](https://developer.adobe.com/commerce/php/development/)
- [Commerce on Cloud Guide](https://experienceleague.adobe.com/en/docs/commerce-on-cloud)
- [REST API Reference](https://developer.adobe.com/commerce/webapi/rest/)
- [GraphQL Reference](https://developer.adobe.com/commerce/webapi/graphql/)
- [Plugins DevDocs](https://developer.adobe.com/commerce/php/development/components/plugins/)
- [Events & Observers](https://developer.adobe.com/commerce/php/development/components/events-and-observers/)
- [Declarative Schema](https://developer.adobe.com/commerce/php/development/components/declarative-schema/)
