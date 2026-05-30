# .actualize — процесс актуализации JS-примеров b24jssdk

Инструменты для замены устаревших jsSDK-примеров (`$b24.callMethod` / `callListMethod` /
`fetchListMethod`) на актуальные табы **TS** и **UMD** через `@bitrix24/b24jssdk` (actions-API).
В актуальном `@1` actions-API уже доступен, а старые методы помечены deprecated
(удаляются в 2.0). Это служебная папка процесса — в PR с правками документации её можно не включать.

## Файлы

| Файл | Назначение |
|------|------------|
| `PROMPT.md` | Главный промпт для актуализации **одного файла**. Папку обходим по одному файлу (`remaining.py --list`). |
| `PROMPT-REVIEW.md` | Второй промпт: ревью уже актуализированного файла. |
| `validate.py` | Структура табов + запрещённые токены + `tsc --strict` (lockfile-пиннинг) + `node --check`. Опц. `--project DIR` — каталог sandbox (для параллельных прогонов). |
| `record.py` | Идемпотентный журнал `ledger.tsv` (upsert, атомарная запись); `--verify-all` / `--verify <path>` — контроль дрейфа по sha256. |
| `remaining.py` | Сколько файлов ещё не обработано (и список). |
| `_tabs.py` | Общие regex разбора табов (используют `validate.py` и `record.py`). |
| `ledger.tsv` | Журнал: дата, файл, sha256, статус, метод (в тулинг-PR — пустой). |
| `typecheck/` | Зафиксированное окружение типопроверки (`package.json` + `package-lock.json`). |
| `tests/` | Офлайн unit-тесты тулинга (`python -m unittest discover -s .actualize/tests`). |

## Как гонять

```bash
# что осталось
python3 .actualize/remaining.py api-reference                 # счётчик
python3 .actualize/remaining.py api-reference/tasks --list    # список

# актуализировать файл по PROMPT.md (LLM-агент), затем проверить и отметить:
python3 .actualize/validate.py api-reference/tasks/tasks-task-get.md   # -> PASS
python3 .actualize/record.py   api-reference/tasks/tasks-task-get.md done

# (опц.) ревью по PROMPT-REVIEW.md:
python3 .actualize/record.py   api-reference/tasks/tasks-task-get.md reviewed

# контроль дрейфа после правок
python3 .actualize/record.py --verify-all                                     # все
python3 .actualize/record.py --verify api-reference/tasks/tasks-task-get.md   # один файл

# офлайн-тесты тулинга (без сети)
python -m unittest discover -s .actualize/tests -p 'test_*.py'
```

Первый запуск `validate.py` ставит зависимости из committed `.actualize/typecheck/package-lock.json`
(через `npm ci --ignore-scripts`) в `.actualize/.tscheck/` (в `.gitignore`). UMD-тег примеров —
мажор-тег `@1`; типопроверка пиннится lockfile'ом (конкретная 1.x). **Бамп версии SDK:** обновить
`.actualize/typecheck/package.json` + `package-lock.json` и прогнать `validate.py` по `done`-файлам.

**Журнал и порядок мёржа.** Тулинг и доковые правки — в разных PR; тулинг-PR мёржится **первым**.
`ledger.tsv` в тулинг-PR пустой (только заголовок) — строки добавляются по мере обработки файлов
(вместе с их контентом), иначе `--verify-all` на `main` покажет дрейф до влития доков. Конфликты
`ledger.tsv` при параллельных PR гасит `merge=union` (`.actualize/.gitattributes`) + идемпотентный
upsert (`load()` дополнительно дедуплицирует строки по файлу при чтении).

## Принятые решения (зафиксированы в PROMPT.md)

- Вместо одного таба `JS` → два таба: **TS** (предполагает готовый `$b24`) и **UMD**
  (полная инициализация через `B24Js.initializeB24Frame()`).
- Обработка ответа: `try/catch` + проверка `response.isSuccess`; в TS — `getData()!`,
  в UMD — `getData()`; для списков — `getTotal()`.
- Комментарии и строковые значения — на английском (SDK ориентирован на международных
  разработчиков). Табы PHP/BX24.js/cURL остаются как есть, включая русские комментарии и
  пред-существующие `processData()` — это вне области правок.
- Версия: по умолчанию `actions.v2`; `actions.v3` — для `rest-v3/**` и ответов `result.item`.
- Списочные методы: один вариант — `call.make` со `start` (+ комментарий про `fetchList.make`).

## Отложенные пункты

Стратегические задачи (политика версий SDK, batch-runner на ~1547 файлов) — в
[`FOLLOWUPS.md`](FOLLOWUPS.md) (GitHub Issues в репозитории отключены).

---
_Last reviewed: 2026-05-30_
