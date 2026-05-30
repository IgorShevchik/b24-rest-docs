# Промпт: актуализация JS-примеров b24jssdk (TS + UMD)

Тебе дан **путь к одному `.md`-файлу** документации Bitrix24 REST API (обычно из `api-reference/**`).
Задача — заменить устаревший пример в табе **`- JS`** (использует `$b24.callMethod` /
`$b24.callListMethod` / `$b24.fetchListMethod`, удалённые в b24jssdk 2.0) на **два таба** —
**`- TS`** и **`- UMD`** — на актуальном API SDK. Содержание страницы не меняем, только пример.

Вход: `<PATH>` — путь к файлу.

## Жёсткие правила

1. **Меняем только пример** внутри блока `{% list tabs %}`. НЕ трогаем остальной текст:
   заголовки, описание параметров, раздел «Обработка ответа», коды ошибок, «Продолжить изучение».
2. **Удаляем таб `- JS`** (старый jsSDK) и ставим на его место по очереди: **`- TS`**, затем **`- UMD`**.
3. **НЕ трогаем** табы `cURL (Webhook)`, `cURL (OAuth)`, `PHP`, `BX24.js`, `PHP CRest` — ни код, ни порядок.
4. Параметры запроса переносим из старого JS-примера **1:1** (`taskId`, `fields`, `select`,
   `filter`, `order`, `params`, `start`, `id`, `entityTypeId` и т.д.).
5. **Комментарии и строковые значения-примеры — на английском.**
6. **В TS/UMD-примере удаляем вызовы несуществующих функций** (`processResult(...)`,
   `processData(...)` и т.п.) — заменяем осмысленным `console.info(...)` по реальным полям ответа.
   В табах PHP/BX24.js/cURL такие вызовы НЕ трогаем — они вне области правок.

## Версия API (v2 / v3)

- По умолчанию — **`actions.v2`**.
- Используй **`actions.v3`**, если файл лежит в `api-reference/rest-v3/**` ИЛИ раздел
  «Обработка ответа» возвращает `result.item` (а не `result.<entity>`).
- Если версию определить нельзя (на странице нет JSON-ответа) — бери `actions.v2` и оставь
  комментарий `// TODO: verify API version`.
- Тип результата `<T>` бери из формы ответа на странице: `{ task: {...} }`, `{ item: {...} }`,
  `{ tasks: [...] }`, `{ fields: {...} }`, `{ order: {...} }`, `boolean`-поля и т.д.
- Выбранную версию (`v2`/`v3`) применяй к **обоим** табам — и TS, и UMD. В шаблонах ниже
  `actions.v2` показан как пример по умолчанию.

## Списочные методы (`*.list`, старые `callListMethod` / `fetchListMethod`)

Используем **`actions.v2.call.make` c параметром `start`** (одностраничный вызов).
Причина: list-хелперы `callList.make` / `fetchList.make` пагинируют по id-курсору и
**не принимают `order`** (он исключён из типа их параметров — передача = ошибка `tsc`), а
сортировка в примерах обычно важна.
- читаем массив из `result.<key>` (например `result.tasks`, `result.items`);
- НАД `const response` оставляем комментарий-подсказку, что для полной выборки есть **два**
  хелпера: `$b24.actions.v2.callList.make()` (вернёт весь массив разом) и
  `$b24.actions.v2.fetchList.make()` (async-генератор по чанкам) — с пометкой `NOTE:`, что
  оба не принимают `order` (исключён из типа параметров);
- `response.getTotal()` НЕ используем (deprecated, removed в SDK 2.0) — показываем размер
  страницы через `result.<key>.length`.

## Чтение ответа: `getData()!` vs `getData()`

- TS (в ветке `else`, т.е. `isSuccess === true`): `response.getData()!.result` (с `!`).
- UMD (после `if (!isSuccess) { …; return }`): `response.getData().result` (без `!`).
- `response.getTotal()` НЕ используем — он `@deprecated` / `@removed 2.0.0` (привязан к v2-полю
  `total`, в v3 его нет). Размер страницы — `result.<key>.length`; полное число — через
  list-хелпер (`callList.make` → весь массив → `.length`) или `aggregate` (count) в v3.

## ES-модуль и версия SDK

- TS-пример — ES-модуль (есть `import` и top-level `await`); это отмечено в комментарии у
  `declare const $b24`. В обычный `<script>` без `type="module"` его вставлять нельзя.
- UMD-тег использует мажор-тег `@1` (защита от мажорных breaking-changes); типопроверка пиннится
  committed lockfile'ом `.actualize/typecheck/package-lock.json` (конкретная 1.x).
- `requestId` задаём генератором SDK: `Text.getUuidRfc4122()` (TS, `import { Text }`) и
  `B24Js.Text.getUuidRfc4122()` (UMD) — не хардкодим строку.
- Пояснительные комментарии (про ES-модуль и готовый `$b24`) ставим **первыми** строками
  TS-сниппета, до `import`. Тип импортируем как `import type { B24Frame[, ISODate] }`; поля-даты
  в типе результата — `ISODate | null` (а не `string | null`).

## Если менять нечего

Нет блока `{% list tabs %}` или таба `- JS` → выведи `SKIP: no JS tab` и не меняй файл.

## Таб TS (предполагает уже инициализированный `$b24`)

```ts
// This snippet is an ES module: top-level await requires type="module" or a bundler.
// $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
import { Text } from '@bitrix24/b24jssdk'
import type { B24Frame } from '@bitrix24/b24jssdk' // add ISODate, etc. for typed date fields

declare const $b24: B24Frame

// Shape of the payload returned in result (match the "response handling" section of the page)
type <Name>Result = {
  // ...
}

try {
  const response = await $b24.actions.v2.call.make<<Name>Result>({
    method: '<rest.method>',
    params: {
      // parameters copied 1:1 from the original example, comments in English
    },
    requestId: Text.getUuidRfc4122()
  })

  // The payload is available only on a successful response
  if (!response.isSuccess) {
    console.error(response.getErrorMessages().join('; '))
  } else {
    const result = response.getData()!.result
    console.info(/* read real response fields */)
  }
} catch (error) {
  // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
  console.error(error)
}
```

## Таб UMD (полная инициализация)

В UMD `call.make` вызывается **без** generic-параметра `<T>` (это plain JS, не TS).

```html
<!-- Load the SDK (UMD build); it is exposed as the global B24Js -->
<script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js"></script>
<script>
  async function <verbNoun>() {
    try {
      // Initialize the SDK inside a Bitrix24 frame
      const $b24 = await B24Js.initializeB24Frame()

      const response = await $b24.actions.v2.call.make({
        method: '<rest.method>',
        params: { /* same params as TS */ },
        requestId: B24Js.Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
        return
      }

      const result = response.getData().result
      console.info(/* read real response fields */)
    } catch (error) {
      // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
      console.error(error)
    }
  }

  document.addEventListener('DOMContentLoaded', <verbNoun>)
</script>
```

## Формат табов (YFM)

Каждый таб: строка `- Имя`, пустая строка, затем блок кода с отступом **4 пробела**:

```
- TS

    ```ts
    ...код...
    ```

- UMD

    ```html
    ...код...
    ```
```

## Валидация (обязательно)

> **В batch-режиме (`run-batch.sh`)** шаги ниже выполняет ОРКЕСТРАТОР, а не ты: у агента нет
> инструмента Bash (`--allowed-tools Read Edit Grep`). Просто внеси правку и остановись —
> валидацию и запись в ledger сделает раннер. Команды ниже — для **ручного** прогона.

1. `python3 .actualize/validate.py <PATH>` → должно быть `PASS`. Проверяет: структуру табов
   (нет `- JS`, есть `- TS`/`- UMD`); извлекает блоки ТОЛЬКО внутри `{% list tabs %}`;
   запрещённые токены (`callMethod`/`callListMethod`/`fetchListMethod`/`processResult`/`processData`);
   наличие `$b24.actions.v{2,3}.*` в **обоих** табах; `tsc --strict` против ПИННИНГ-версии
   `@bitrix24/b24jssdk` (= 0 ошибок); `node --check` UMD.
2. Если `FAIL` — исправь код и повтори, пока не `PASS`.

## Отметка о выполнении

> В batch-режиме это тоже делает оркестратор — ручной шаг ниже не нужен.

После `PASS`: `python3 .actualize/record.py <PATH> done` — идемпотентный upsert (одна строка на
файл: дата, sha256, статус, метод) в `.actualize/ledger.tsv`. Контроль дрейфа:
`python3 .actualize/record.py --verify-all`. Список оставшихся: `python3 .actualize/remaining.py`.

## Чек-лист перед завершением

> Не заполняется при `SKIP` (файл не менялся).

- [ ] таб `- JS` удалён, добавлены `- TS` и `- UMD`
- [ ] остальные табы и текст страницы не изменены
- [ ] нет `callMethod` / `callListMethod` / `fetchListMethod` в jsSDK-примере
- [ ] нет вызовов `processResult` / `processData`
- [ ] комментарии и значения на английском
- [ ] пояснит. комментарии (ES-модуль, `$b24`) — первыми строками; в TS `import type { B24Frame }` (+`ISODate` для дат), в UMD — `B24Js.*` без import
- [ ] `requestId` через `Text.getUuidRfc4122()` (TS) / `B24Js.Text.getUuidRfc4122()` (UMD)
- [ ] `getData()!` в TS / `getData()` в UMD; для списков — `.length` (НЕ `getTotal()`, он deprecated)
- [ ] для списков — подсказка про `callList.make` и `fetchList.make` (с `NOTE` про игнор `order`)
- [ ] `validate.py` → PASS
- [ ] `record.py ... done` выполнен

---
_Last reviewed: 2026-05-30_
