# .actualize — процесс актуализации JS-примеров b24jssdk

Инструменты для замены устаревших jsSDK-примеров (`$b24.callMethod` / `callListMethod` /
`fetchListMethod`) на актуальные табы **TS** и **UMD** через `@bitrix24/b24jssdk` (actions-API).
В текущем `@latest` (1.2.0) actions-API уже доступен, а старые методы помечены deprecated
(удаляются в 2.0). Это служебная папка процесса — в PR с правками документации её можно не включать.

## Файлы

| Файл | Назначение |
|------|------------|
| `PROMPT.md` | Главный промпт: по нему гоняем актуализацию одного файла (или папки — по файлу за раз). |
| `PROMPT-REVIEW.md` | Второй промпт: ревью уже актуализированного файла. |
| `validate.py` | Структура табов + запрещённые токены + `tsc --strict` (lockfile-пиннинг) + `node --check`. |
| `record.py` | Идемпотентный журнал `ledger.tsv` (upsert, атомарная запись); `--verify-all` — контроль дрейфа. |
| `remaining.py` | Сколько файлов ещё не обработано (и список). |
| `ledger.tsv` | Журнал: дата, файл, sha256, статус, метод (в тулинг-PR — пустой). |
| `typecheck/` | Зафиксированное окружение типопроверки (`package.json` + `package-lock.json`). |

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
python3 .actualize/record.py --verify-all
```

Первый запуск `validate.py` ставит зависимости из committed `.actualize/typecheck/package-lock.json`
(через `npm ci --ignore-scripts`) в `.actualize/.tscheck/` (в `.gitignore`). UMD-тег примеров —
мажор-тег `@1`; типопроверка пиннится lockfile'ом (конкретная 1.x). **Бамп версии SDK:** обновить
`.actualize/typecheck/package.json` + `package-lock.json` и прогнать `validate.py` по `done`-файлам.

**Журнал и порядок мёржа.** Тулинг и доковые правки — в разных PR; тулинг-PR мёржится **первым**.
`ledger.tsv` в тулинг-PR пустой (только заголовок) — строки добавляются по мере обработки файлов
(вместе с их контентом), иначе `--verify-all` на `main` покажет дрейф до влития доков. Конфликты
`ledger.tsv` при параллельных PR гасит `merge=union` (`.gitattributes`) + идемпотентный upsert.

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
