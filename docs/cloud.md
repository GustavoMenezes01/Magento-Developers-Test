# Cloud

> **Domínio 3 — Cloud (12%)** &nbsp;·&nbsp; Seções 3.1 – 3.4

---

## Ambientes

```
Production  (live — tráfego real)
    ↑  merge
Staging     (pré-prod, clone da produção)
    ↑  merge
Integration (desenvolvimento)
    ├── feature/branch-a
    └── feature/branch-b
```

---

## Planos Starter vs Pro

| | Starter | Pro |
|---|---|---|
| Ambientes Integration | **2** (máximo ativo) | **Ilimitados** |
| Ambientes totais | 4 (Prod + Staging + 2 Integration) | Production + Staging + N Integration |
| Produção | Servidor único | Cluster: 3 nós web + MySQL master/slave |
| Redis | Sim | Sim |
| Elasticsearch/OpenSearch | Sim | Sim |
| CDN | Fastly | Fastly |
| Escala automática | Não | Sim |

> **Starter = máximo 2 Integration environments ativos.**
> **Pro = Integration environments ilimitados para desenvolvimento paralelo.**

---

## Tech Stack do Pro

| Componente | Tecnologia | Função |
|---|---|---|
| CDN | **Fastly** | Content Delivery, Full-page cache (não é Akamai) |
| Web server | **NGINX** | Web server e load balancer (não é Apache) |
| File storage | **GlusterFS** | Armazenamento distribuído entre nós (não é NFS) |
| Cache / Sessions | **Redis** | Cache de aplicação e sessões (não é Memcached) |
| Search | **Elasticsearch / OpenSearch** | Indexação de catálogo e busca |
| Database | **Galera (MySQL Galera Cluster)** | Alta disponibilidade de banco de dados |

> Armadilhas do exame: Akamai ≠ Fastly · Apache ≠ NGINX · NFS ≠ GlusterFS · Memcached ≠ Redis

---

## Diretórios: Read-Only vs Writable

> Esta pergunta aparece com frequência. Saber de cor.

| Diretório | Estado em Production | Motivo |
|---|---|---|
| `app/code` | **Read-only** | Código da aplicação — não pode ser alterado em runtime |
| `app/design` | **Read-only** | Ficheiros de tema — protegidos em runtime |
| `pub/static` | **Writable** | Geração dinâmica de assets estáticos |
| `pub/media` | **Writable** | Upload de imagens e media |
| `var` | **Writable** | Cache, logs, ficheiros temporários |
| `generated` | **Writable** | Código gerado (DI, interceptors) |
| `/tmp` | **Writable** | Ficheiros temporários do sistema |

> Resposta para "writable during runtime": `var, pub/static, pub/media, /tmp`
> Resposta para "read-only after deployment": `app/code, app/design`

---

## .magento.app.yaml

Configuração da aplicação: runtime, hooks, web server, relacionamentos com serviços.

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
            allow: false
            rules:
                '\.(ico|jpg|jpeg|png|gif|svg|js|css|swf|eot|ttf|otf|woff|woff2)$':
                    allow: true

relationships:
    database:       'mysql:mysql'
    redis:          'redis:redis'
    elasticsearch:  'elasticsearch:elasticsearch'
```

---

## services.yaml

Define os serviços de infraestrutura disponíveis.

```yaml
mysql:
    type: mysql:10.6
    disk: 2048

redis:
    type: redis:7.0

elasticsearch:
    type: elasticsearch:8.5
    disk: 1024

rabbitmq:
    type: rabbitmq:3.11
    disk: 512
```

---

## routes.yaml

Define como as URLs são roteadas para a aplicação.

```yaml
"https://www.{default}/":
    type: upstream
    upstream: "myapp:http"
    cache:
        enabled: true
        headers: [ Accept, Accept-Language, X-Language ]

"https://{default}/":
    type: redirect
    to: "https://www.{default}/"
```

---

## .magento.env.yaml

Configura variáveis de deploy por stage (global, build, deploy, post-deploy).

```yaml
stage:
    global:
        SKIP_HTML_MINIFICATION: true
        SCD_ON_DEMAND: true

    build:
        SCD_STRATEGY: compact
        SCD_COMPRESSION_LEVEL: 4
        VERBOSE_COMMANDS: enabled

    deploy:
        SEARCH_CONFIGURATION:
            engine: elasticsearch7
            elasticsearch_server_hostname: elasticsearch.internal
            elasticsearch_server_port: '9200'
            elasticsearch_index_prefix: magento2

        CACHE_CONFIGURATION:
            _merge: true
            frontend:
                default:
                    backend: Cm_Cache_Backend_Redis
                    backend_options:
                        server: redis.internal
                        port: '6379'
                        database: '0'
                page_cache:
                    backend: Cm_Cache_Backend_Redis
                    backend_options:
                        server: redis.internal
                        port: '6379'
                        database: '1'

    post_deploy:
        WARM_UP_PAGES:
            - '/'
            - '/category-page'
```

---

## CLI do Cloud

| Comando | O que faz |
|---|---|
| `magento-cloud login` | Autenticar na conta Adobe |
| `magento-cloud environment:list` | Listar todos os ambientes |
| `magento-cloud environment:checkout <branch>` | Fazer checkout de um ambiente |
| `magento-cloud ssh` | SSH no ambiente ativo |
| `magento-cloud environment:push` | Push do branch atual |
| `magento-cloud environment:merge` | Merge para o ambiente pai |
| `magento-cloud environment:delete <id>` | Deletar ambiente de integration |
| `magento-cloud log:tail --type=deploy` | Logs de deploy em tempo real |
| `magento-cloud log:tail --type=error` | Logs de erro |
| `magento-cloud db:sql` | Acesso SQL interativo ao banco |
| `magento-cloud tunnel:open` | Tunnel para serviços (DB, Redis) |
| `magento-cloud variable:set VAR valor` | Definir variável de ambiente |
| `magento-cloud variable:get VAR` | Ler variável |
| `magento-cloud activity:list` | Ver histórico de atividades |
| **`magento-cloud snapshot:create`** | **Criar backup do ambiente** |

---

## Snapshots (Backup de Ambiente)

> Pergunta que aparece em todos os testes.

```bash
# CORRETO — criar backup
magento-cloud snapshot:create

# INCORRETO — este comando NÃO EXISTE
magento-cloud environment:backup    ← não existe no CLI padrão

# INCOMPLETO — falta o verbo de ação
magento-cloud environment:snapshot  ← incompleto, precisa de :create
```

**Regra:** `magento-cloud snapshot:create` — o namespace é `snapshot`, o verbo é `create`.

---

## Ficheiros de Configuração Cloud — Resumo

> Saber qual ficheiro serve para quê — perguntado com frequência.

| Ficheiro | Propósito |
|---|---|
| `.magento.app.yaml` | Configuração **da aplicação** (PHP version, hooks, web server, relationships, `disk`) |
| `.magento/services.yaml` | Define **serviços de infraestrutura** (MySQL, Redis, Elasticsearch, RabbitMQ) |
| `.magento/routes.yaml` | Define **roteamento de URLs** |
| `.magento.env.yaml` | Define **variáveis de deploy** por stage (build, deploy, post-deploy) |
| ~~`.magento.config.yaml`~~ | **NÃO EXISTE** — armadilha frequente no exame |

```yaml
# .magento/services.yaml — serviços de infraestrutura
mysql:
    type: mysql:10.6
    disk: 2048
redis:
    type: redis:7.0
elasticsearch:
    type: elasticsearch:8.5
    disk: 1024
```

> Para ajustar **disk space da aplicação** → `.magento.app.yaml` com a chave `disk`.
> Para ajustar **disk space de um serviço** (ex: MySQL) → `.magento/services.yaml` com a chave `disk`.

---

## Variáveis de Ambiente

### Níveis

| Nível | Scope | Comando |
|---|---|---|
| Project | Todos os ambientes do projeto | `magento-cloud variable:set --level=project` |
| Environment | Ambiente específico | `magento-cloud variable:set --level=environment` |

### Variáveis Sensíveis

```bash
# Nunca commitar chaves de API no git — usar variáveis sensíveis
magento-cloud variable:set \
    --level=environment \
    --sensitive=true \
    --name=PAYMENT_API_KEY \
    --value="sk_live_xxxxx"
```

> Variáveis com `--sensitive=true` são mascaradas nos logs e na UI do Cloud Console.

---

## ECE-Tools e Deploy Scenarios

O `ece-tools` orquestra o deploy via cenários XML. Cada cenário é uma sequência de steps configuráveis.

| Cenário | Quando roda | O que faz |
|---|---|---|
| `scenario/build/generate.xml` | Hook `build` | DI compile, código gerado |
| `scenario/build/transfer.xml` | Hook `build` | Copia assets para o deploy slot |
| `scenario/deploy.xml` | Hook `deploy` | `setup:upgrade`, configurações de serviços |
| `scenario/post-deploy.xml` | Hook `post_deploy` | Warm-up de cache, health checks |

---

## Hooks de Deploy

| Hook | Acesso a serviços? | Tráfego servido? | Uso típico |
|---|---|---|---|
| `build` | **Não** | **Não** | Instalar deps, compilar código, gerar assets estáticos |
| `deploy` | **Sim** | **Não** (maintenance mode) | `setup:upgrade`, configurar cache/search |
| `post_deploy` | **Sim** | **Sim** | Warm-up de cache, notificações, health checks |

> O hook `build` não tem acesso a serviços (DB, Redis) porque roda antes do ambiente estar ativo. Todo o código que precisa de banco deve ficar no `deploy` ou `post_deploy`.
