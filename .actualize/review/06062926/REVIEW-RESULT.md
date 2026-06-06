# Ревью актуализации jsSDK-примеров (TS + UMD)

Замена таба `- JS` (`callMethod`/`callListMethod`/`fetchListMethod`, удалены в b24jssdk 2.0) на `- JS (TS)` + `- JS (UMD)` на actions API. Форк `@ 7f667d9`.

**Итог:** просмотрено 82/82 · с замечаниями: 1 · ок: 28 · пропущено: 54.

## Замечания

### crm/deals (29)

#### `index.md` — [файл](https://github.com/IgorShevchik/b24-rest-docs/blob/main/api-reference/crm/deals/index.md) · [доки](https://apidocs.bitrix24.ru/api-reference/crm/deals/index.html)
> ⚠️ Пример `crm.item.update`: на странице **нет JSON-ответа** → результат оставлен **нетипизированным** с комментарием `// TODO: verify API version`. Проверить версию API и тип результата вручную.

api-reference/crm/deals/crm-deal-update.md - тут описано что возвращает вызываемый метод

Проведи анализ - исправь что нужно - сними TODO
