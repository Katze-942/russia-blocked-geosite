# Katze GeoSite

Форк собирает облегчённый `geosite.dat` с категориями из [списка](categories/geosite-katze.txt). Для сборки используются только необходимые категории и их зависимости из [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) и [runetfreedom/russia-domains-list](https://github.com/runetfreedom/russia-domains-list). Полная база, отдельная российская база и текстовые списки не публикуются.

Сборка запускается каждые 6 часов и вручную через GitHub Actions. Релиз также содержит SHA-256, список категорий и `KATZE_GEODATA_SOURCE` с коммитами исходных репозиториев и хешем списка категорий.

- [geosite.dat](https://raw.githubusercontent.com/Katze-942/russia-blocked-geosite/release/geosite.dat)
- [SHA-256](https://raw.githubusercontent.com/Katze-942/russia-blocked-geosite/release/geosite.dat.sha256sum)
- [Облегчённая база GeoIP](https://github.com/Katze-942/russia-blocked-geoip)

Проект основан на [runetfreedom/russia-blocked-geosite](https://github.com/runetfreedom/russia-blocked-geosite) и использует генератор [runetfreedom/domain-list-custom](https://github.com/runetfreedom/domain-list-custom).
