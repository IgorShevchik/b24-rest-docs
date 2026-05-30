# .actualize — процесс актуализации JS-примеров b24jssdk

Инструменты для замены устаревших jsSDK-примеров (`$b24.callMethod` / `callListMethod` /
`fetchListMethod`) на актуальные табы **TS** и **UMD** через `@bitrix24/b24jssdk` (actions-API).
В актуальном `@1` actions-API уже доступен, а старые методы помечены deprecated
(удаляются в 2.0). Это служебная папка процесса — в PR с правками документации её можно не включать.

## Файлы

| Файл | Назначение |
|------|------------|
| `PROMPT.md` | Промпт для актуализации **одного файла**. Оркестрация — через `run-batch.sh` или вручную (`remaining.py --list`). |
| `PROMPT-REVIEW.md` | Второй промпт: ревью уже актуализированного файла. |
| `validate.py` | Структура табов + запрещённые токены + `tsc --strict` (lockfile-пиннинг) + `node --check`. Опц. `--project DIR` — каталог sandbox (для параллельных прогонов). |
| `record.py` | Идемпотентный журнал `ledger.tsv` (upsert, атомарная запись); `--verify-all` / `--verify <path>` — контроль дрейфа по sha256. |
| `remaining.py` | Сколько файлов ещё не обработано (и список). |
| `run-batch.sh` | Оркестратор батча поверх трёх скриптов: правит файлы агентом (параллельно), валидирует и пишет ledger (серийно), коммитит прошедшие. **Dry-run по умолчанию** (нужен `RUN=1`); ⚠️ EXPERIMENTAL — боевым прогоном пока не обкатан. Требует GNU bash ≥ 4. |
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

### Массовый прогон (batch-runner)

> ⚠️ **EXPERIMENTAL.** Скрипт проверен синтаксически и в dry-run, но боевым `RUN=1`-прогоном
> по корпусу ещё не обкатывался. Первый реальный запуск делай малым (`N=3 PAR=1`) на throwaway-ветке
> под наблюдением. Требует **GNU bash ≥ 4** (macOS по умолчанию bash 3.2 — поставь новее или Linux).

`run-batch.sh` гоняет связку «агент → `validate.py` → `record.py`» батчами: шаг правки —
параллельно (`xargs -0 -P`, файлы разные); **валидация — тоже параллельно**, но у каждого воркера
свой sandbox `--project` (hardlink-клон прогретого `.tscheck` через `cp -al`, общие inode'ы
`node_modules` — почти бесплатно); **запись ledger — серийно** (один писатель, без гонки). Прошедшие
коммитятся; упавшие откатываются и остаются в `remaining` на следующий проход.

**Dry-run по умолчанию.** Без `RUN=1` скрипт только печатает план (какие файлы тронул бы) и
выходит — ничего не правит и не коммитит. Это защита: скрипт сам переходит в корень репозитория,
поэтому случайный запуск не должен молча менять файлы. Дополнительно, с `RUN=1` скрипт **не
стартует на грязном рабочем дереве** — так батч может закоммитить только свои правки и никогда не
смешает посторонние изменения. Запускай из ветки для **доковых** правок, не из тулинг-PR.

**Защита от prompt-injection (blast-radius check).** Контент `.md` для агента — недоверенные
данные: системный префикс запрещает трогать что-либо кроме `<PATH>`. Но главная защита —
**не на доверии к модели**: после фазы правки скрипт сверяет фактически изменённые файлы (tracked +
untracked) с планом батча. Любой выход за план (соседний файл, новый untracked, запись секрета) →
**весь батч откатывается, ничего не коммитится** (`SECURITY ABORT`). Так инъекция, заставившая
агента писать вне `<PATH>`, не сможет ничего протащить в коммит.

```bash
# план без изменений (dry-run): ROOT, N (файлов в батче, 0 = все), PAR (параллельных правок)
.actualize/run-batch.sh api-reference/tasks 20 4

# реальный прогон одного батча (требует чистого дерева):
RUN=1 .actualize/run-batch.sh api-reference/tasks 20 4

# крутить раздел до нуля (каждый запуск возобновляем через ledger):
while python3 .actualize/remaining.py api-reference/tasks --limit 1 \
        | grep -q 'not done): [1-9]'; do
  RUN=1 .actualize/run-batch.sh api-reference/tasks 30 4 || break
done
```

Тумблеры: `RUN=1` (реальный прогон), `EDIT_TIMEOUT` (сек на файл, дефолт 600, требует `timeout` в
PATH), `KEEP_FAILED=1` (не откатывать упавшие + сохранить логи), `NO_COMMIT=1` (не коммитить),
`CLAUDE_MODEL`, `CLAUDE_BIN` (бинарь агента, для тестов), `VALIDATE_PAR` (параллелизм валидации,
дефолт = `PAR`). Третий позиционный аргумент `PAR` задаёт параллелизм и правок, и валидации. Итог
батча печатается строкой `batch summary: PASSED=… FAILED=… SKIPPED=…`. Логи правок/валидации — во временном каталоге
(`mktemp -d`, печатается при старте; удаляется в конце, кроме `KEEP_FAILED` при падениях), в коммит
не попадают.

**SKIP — это норма.** Если агент не изменил файл (нет таба `- JS`, либо ответ `SKIP`), файл не
пишется в ledger и остаётся в `remaining` — повторные SKIP в логах ожидаемы.

**Прерывание (Ctrl-C).** В фазе правки — безопасно (ещё ничего не закоммичено). В фазе
валидации/записи — в дереве могут остаться правки и/или строки ledger, записанные но не
закоммиченные; скрипт печатает подсказку — проверь `git status` и либо закоммить, либо откати.

**Внимание:** `validate.py` — структурный гейт (табы, токены, `tsc`, `node --check`); семантику
(выбор `v2`/`v3`, маппинг полей `result`) он **не** проверяет — прогоняй выборку через
`PROMPT-REVIEW.md` и ставь `reviewed`.

**Журнал и порядок мёржа.** Тулинг и доковые правки — в разных PR; тулинг-PR мёржится **первым**.
`ledger.tsv` в тулинг-PR пустой (только заголовок) — строки добавляются по мере обработки файлов
(вместе с их контентом), иначе `--verify-all` на `main` покажет дрейф до влития доков. Конфликты
`ledger.tsv` при параллельных PR гасит `merge=union` (`.actualize/.gitattributes`) + идемпотентный
upsert (`load()` дополнительно дедуплицирует строки по файлу при чтении).

## Принятые решения (зафиксированы в PROMPT.md)

- Вместо одного таба `JS` → два таба: **TS** (предполагает готовый `$b24`) и **UMD**
  (полная инициализация через `B24Js.initializeB24Frame()`).
- Обработка ответа: `try/catch` + проверка `response.isSuccess`; в TS — `getData()!`,
  в UMD — `getData()`; для списков — `result.<key>.length` (`getTotal()` deprecated/removed 2.0).
- `requestId` генерируется SDK: `Text.getUuidRfc4122()` (TS, `import { Text }`) /
  `B24Js.Text.getUuidRfc4122()` (UMD).
- Шапка TS: пояснительные комментарии (ES-модуль, `$b24`) — первыми строками; тип импортируется
  как `import type { B24Frame[, ISODate] }`; поля-даты в типе результата — `ISODate | null`.
- Комментарии и строковые значения — на английском (SDK ориентирован на международных
  разработчиков). Табы PHP/BX24.js/cURL остаются как есть, включая русские комментарии и
  пред-существующие `processData()` — это вне области правок.
- Версия: по умолчанию `actions.v2`; `actions.v3` — для `rest-v3/**` и ответов `result.item`.
- Списочные методы: один вариант — `call.make` со `start` (сохраняет `order`). Над `const response`
  — подсказка про оба хелпера `callList.make` / `fetchList.make` с `NOTE`, что они НЕ принимают
  `order` (исключён из их типа — `tsc`-ошибка при передаче).

## Отложенные пункты

Стратегические задачи (политика версий SDK, доработки batch-runner) — в
[`FOLLOWUPS.md`](FOLLOWUPS.md) (GitHub Issues в репозитории отключены).

---
_Last reviewed: 2026-05-30_
