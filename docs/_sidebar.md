* **[⚠️ Pegadinhas](pegadinhas)** — Leia antes do exame
  * [di.xml e dados sensíveis](pegadinhas#dixmll--lida-com-dados-sensíveis)
  * [addAttribute — visible_on_front](pegadinhas#addattribute--parâmetros-exatos)
  * [Plugin — atributos válidos](pegadinhas#plugin--atributos-válidos-em-dixmll)
  * [module.xml — sintaxe sequence](pegadinhas#modulexml--sintaxe-exata)
  * [JS: $.mage.__() oficial](pegadinhas#js-translation--funções-exatas)
  * [Cloud: snapshot:create](pegadinhas#cloud-cli--comandos-exatos)
  * [Cloud: dirs read-only vs writable](pegadinhas#diretórios-cloud--read-only-vs-writable)
  * [system.xml vs config.xml](pegadinhas#systemxml-vs-configxml--diferença-crítica)
  * [Ficheiros que não existem no M2](pegadinhas#ficheiros-que-não-existem-no-magento-2)

---

* **[Início](/)** — Visão geral do exame

---

* **📦 Módulos & CLI**
  * [Estrutura de Módulo](modulos#estrutura-de-pastas)
  * [registration.php](modulos#registrationphp)
  * [module.xml & Sequência](modulos#modulexml)
  * [Comandos CLI](modulos#comandos-cli-essenciais)
  * [Ordem de Deploy](modulos#ordem-correta-de-deploy)

---

* **🔌 DI & Plugins**
  * [Como funciona o DI](di-plugins#como-funciona-o-di)
  * [Preference](di-plugins#preference)
  * [Plugin — Before/After/Around](di-plugins#plugin-interceptor)
  * [Virtual Type](di-plugins#virtual-type)
  * [Quando usar cada um](di-plugins#quando-usar-cada-mecanismo)
  * [Observers & Events](di-plugins#observers-e-events)
  * [Eventos mais cobrados](di-plugins#eventos-mais-comuns)
  * [CRON — crontab.xml](di-plugins#cron)

---

* **🗄️ DB & Cache**
  * [Indexers](database#indexers)
  * [Tipos de Cache](database#tipos-de-cache)
  * [Backends de Cache](database#backends-de-cache)
  * [EAV](database#eav-e-database)
  * [Declarative Schema](database#declarative-schema)
  * [Data Patches](database#data-patches)
  * [Service Contracts](database#service-contracts)
  * [SearchCriteria](database#searchcriteria)
  * [Store Hierarchy](database#hierarquia-de-store)
  * [Escopos de Configuração](database#escopos-de-configuracao)
  * [Traduções](database#traducoes)
  * [URL Rewrites](database#url-rewrites)

---

* **🏪 Stores & Store Views**
  * [Cenários Rápidos](stores#cenários-rápidos--o-cliente-quer)
  * [Hierarquia Website→Store→View](stores#hierarquia-website--store--store-view)
  * [Escopos de Configuração](stores#escopos-de-configuração)
  * [Escopos de Produto](stores#escopos-de-produto)
  * [Customer Account Sharing](stores#customer-accounts--compartilhamento)
  * [Price Scope](stores#price-scope--configuração)
  * [Editar Conteúdo por Store View](stores#como-editar-conteúdo-por-store-view-admin)
  * [Root Category por Store](stores#root-category--catálogos-separados-por-store)
  * [StoreManagerInterface](stores#websites-stores-store-views--tabela-de-ids)
  * [core_config_data](stores#configuração-por-escopo--config-table)
  * [O que nunca muda de escopo](stores#o-que-nunca-muda-de-escopo)

---

* **📦 Produtos**
  * [Cenários Rápidos](produtos#cenários-rápidos--o-cliente-quer)
  * [Tipos de Produto](produtos#tipos-de-produto--comparação-detalhada)
  * [Attribute Input Types](produtos#atributos--tipos-de-input)
  * [Attribute Properties](produtos#atributos--propriedades-importantes)
  * [Attribute Sets](produtos#attribute-sets)
  * [Todos os Tipos de Preço](produtos#preços--todos-os-tipos)
  * [Visibilidade & Status](produtos#visibilidade-do-produto)
  * [Atributos Mínimos](produtos#criar-produto--atributos-mínimos-obrigatórios)
  * [Layered Navigation Setup](produtos#layered-navigation--setup-completo)
  * [Vídeos na Galeria](produtos#vídeos-na-galeria-do-produto)
  * [Related vs Upsell vs Crosssell](produtos#product-associations--onde-aparece-cada-uma)
  * [URLs & SEO](produtos#url-de-produto--configurações-seo)

---

* **🛍️ Catálogo & Sales**
  * [Tipos de Produto](catalogo#tipos-de-produto)
  * [Criar Produto](catalogo#criar-produto-programaticamente)
  * [Attribute Types](catalogo#attribute-types)
  * [Fluxo do Pedido](catalogo#fluxo-de-pedido)
  * [Quote vs Order](catalogo#quote-vs-order)
  * [Order States](catalogo#order-states-e-statuses)
  * [Customizar Checkout](catalogo#customizar-checkout)
  * [Total Collectors](catalogo#total-collectors)
  * [Customer Programaticamente](catalogo#customer-programaticamente)

---

* **🖥️ Frontend & Admin**
  * [Layout XML — Nomenclatura](frontend#layout-xml--nomenclatura)
  * [UI Components — Diretórios](frontend#ui-components--estrutura-de-diretórios)
  * [system.xml — Estrutura](frontend#admin-configuration-systemxml)
  * [config.xml vs system.xml](frontend#ficheiros-de-configuração-importantes)
  * [Entry Points (pub/index.php)](frontend#entry-points-e-routing)
  * [Traduções PHP — __()](frontend#traduções-em-php)
  * [Traduções JS — $.mage.__()](frontend#traduções-em-javascript)
  * [Workflow i18n](frontend#workflow-de-internacionalização-i18n)
  * [Layered Navigation — Anchor](frontend#layered-navigation-navegação-filtrada)
  * [Product Recommendations PDP vs Cart](frontend#product-recommendations-pdp-vs-cart)

---

* **🔗 APIs**
  * [REST — webapi.xml](apis#rest-api)
  * [Autenticação REST](apis#tipos-de-autenticacao)
  * [Obter Tokens](apis#obter-tokens)
  * [GraphQL — schema.graphqls](apis#graphql)
  * [SaaS Services](apis#adobe-saas-services)
  * [Fluxo de Dados SaaS](apis#fluxo-de-dados-saas)
  * [API Mesh](apis#api-mesh)

---

* **☁️ Cloud**
  * [Ambientes Cloud](cloud#ambientes)
  * [Starter vs Pro — Nº de envs](cloud#planos-starter-vs-pro)
  * [Tech Stack Pro (Fastly/NGINX/GlusterFS)](cloud#tech-stack-do-pro)
  * [Dirs Read-Only vs Writable](cloud#diretórios-read-only-vs-writable)
  * [snapshot:create (backup)](cloud#snapshots-backup-de-ambiente)
  * [Ficheiros config — qual para quê](cloud#ficheiros-de-configuração-cloud--resumo)
  * [.magento.app.yaml](cloud#magentoappyaml)
  * [services.yaml](cloud#servicesyaml)
  * [routes.yaml](cloud#routesyaml)
  * [.magento.env.yaml](cloud#magentoenvyaml)
  * [CLI do Cloud](cloud#cli-do-cloud)
  * [Variáveis de Ambiente](cloud#variaveis-de-ambiente)
  * [ECE-Tools & Scenarios](cloud#ece-tools-e-deploy-scenarios)
  * [Hooks de Deploy](cloud#hooks-de-deploy)
