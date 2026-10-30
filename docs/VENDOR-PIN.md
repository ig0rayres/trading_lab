# Vendor pin — day-trader-skill

> Status: **pinado na Sprint D1** (submodule)  
> Upstream: https://github.com/Jakeschincariol/day-trader-skill

| Campo | Valor |
|-------|--------|
| Commit pinado (submodule) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Data do pin | 2026-10-30 |
| Loader | `src/original.py` |
| Env | `UPSTREAM_DIR`, opcional `UPSTREAM_COMMIT` |

Regra: upgrades do vendor exigem testes de paridade (`vendor_verify`, `parity`) e atualização desta tabela.

**Imagem Docker (N6+):** o `Dockerfile` clona este SHA em `/app/vendor/day-trader-skill` no build; `ENV UPSTREAM_COMMIT` na imagem deve coincidir com a tabela acima. Submodule local permanece para pytest/`vendor_verify` no host.

**Nota:** clone raso no submodule; para pin imutável de produção, fixar este SHA em `UPSTREAM_COMMIT` no EasyPanel após revisão humana.
