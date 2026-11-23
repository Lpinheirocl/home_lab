# Versionamento de imagens

Quando um Pull Request é mesclado em `main`, `master` ou `develop`, o workflow `Tag merged pull request` cria uma tag Git SemVer no commit mesclado.

- Sem label de versão: incrementa o patch (`v0.1.0` → `v0.1.1`).
- Label `minor` ou `semver:minor`: incrementa a versão minor.
- Label `major` ou `semver:major`: incrementa a versão major.
- A primeira tag usa `v0.1.0` por padrão; as labels `minor` e `major` podem iniciar em `v0.2.0` e `v1.0.0`.

Depois de criar a tag, o workflow aciona a publicação das imagens ARM64 no GHCR com a tag da versão. Essa publicação não implanta a versão no Raspberry Pi; os pushes aos branches continuam usando o fluxo de implantação existente.
