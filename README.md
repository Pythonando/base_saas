# SaaS em Django (Autenticacao + Planos + Dashboard Admin)

Projeto Django com:
- autenticacao por e-mail (cadastro, login, logout, reset de senha),
- controle de plano por usuario,
- webhook de pagamentos (Zouti),
- dashboard administrativa com metricas SaaS (MRR, churn, conversao, etc.).

## Requisitos

- Python 3.12+ (recomendado 3.14, usado no projeto)
- `pip`
- SQLite (ja embutido no Python)

## 1) Setup local

No diretorio do projeto:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install django python-decouple requests pysendpulse
```

Dependencias opcionais:

```bash
pip install whitenoise django-debug-toolbar django-q
```

## 2) Variaveis de ambiente

Crie um arquivo `.env` na raiz do projeto (mesmo nivel do `manage.py`).

Exemplo:

```env
# Django
DJANGO_SECRET_KEY=sua-chave-secreta-aqui
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# E-mail
DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=caio@pythonando.com.br

# SendPulse (necessario se for enviar e-mail real via API SendPulse)
CLIENT_ID_SENDPULSE=
CLIENT_SECRET_SENDPULSE=

# Webhook de pagamento (opcional, mas recomendado em producao)
ZOUTI_WEBHOOK_SECRET=
```

### O que e obrigatorio?

- Para subir o projeto local: nenhuma variavel e estritamente obrigatoria (existem defaults).
- Para ambiente real: defina ao menos `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` e `DJANGO_ALLOWED_HOSTS`.
- Para envio real de e-mail via SendPulse: `CLIENT_ID_SENDPULSE` e `CLIENT_SECRET_SENDPULSE`.
- Para validar webhook com seguranca: `ZOUTI_WEBHOOK_SECRET`.

## 3) Banco e migracoes

```bash
python manage.py migrate
```

## 4) Criar usuario admin

```bash
python manage.py createsuperuser
```

## 5) Rodar aplicacao

```bash
python manage.py runserver
```

Acesse:
- App: `http://127.0.0.1:8000/auth/login/`
- Admin Django: `http://127.0.0.1:8000/admin/`
- Dashboard admin custom: `http://127.0.0.1:8000/auth/admin/dashboard/`

## 6) Configuracao dos planos (MRR)

O MRR da dashboard usa o campo `price_monthly` do modelo `Plan`.

Passos:
1. Entre no Django Admin.
2. Abra `Plans > Plans`.
3. Ajuste o valor de `price_monthly` dos planos.

Sem esse valor, o MRR fica `0.00`.

## 7) Webhook de pagamentos (Zouti)

Endpoint:

`POST /webhooks/zouti/`

Comportamento atual:
- identifica `customer.email` e `items[0].product_offer_id`,
- cria/atualiza usuario,
- cria/atualiza `UserPlan` (`ACTIVE` quando status do payload for `PAID`, senao `CANCELLED`),
- opcionalmente envia e-mail de boas-vindas para novo usuario ativo.

Se `ZOUTI_WEBHOOK_SECRET` estiver configurado, o header `X-Zouti-Secret` precisa bater com esse valor.

## 8) Comandos uteis

```bash
# Checagem de integridade Django
python manage.py check

# Shell Django
python manage.py shell
```

## 9) Estrutura principal

- `accounts/`: autenticacao, views de login/cadastro/dashboard e servicos de e-mail.
- `plans/`: modelos de plano/assinatura, webhook e middleware de acesso por plano.
- `templates/`: telas HTML (Tailwind + Chart.js na dashboard admin).
- `core/settings.py`: configuracoes globais do projeto.


