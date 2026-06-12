# Получить список шаблонов bizproc.workflow.template.list

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`bizproc`](../../scopes/permissions.md)
>
> Кто может выполнять метод: администратор

Метод получает список шаблонов бизнес-процессов.

## Параметры метода

#|
|| **Название**
`тип` | **Описание** ||
|| **SELECT**
[`array`](../../data-types.md) | Массив содержит список [полей](#fields), которые необходимо выбрать.

Можно указать только те поля, которые необходимы.

Значение по умолчанию — `['ID']` ||
|| **FILTER**
[`object`](../../data-types.md) | Объект для фильтрации списка шаблонов бизнес-процессов в формате `{"field_1": "value_1", ... "field_N": "value_N"}`, где
- `field_N` — [поле](#fields) шаблона для фильтра
- `value_N` — значение поля

Перед названием фильтруемого поля можно указать тип фильтрации:
- `!` — не равно
- `<` — меньше
- `<=` — меньше либо равно
- `>` — больше
- `>=` — больше либо равно | ||
|| **ORDER**
[`object`](../../data-types.md) | Объект для сортировки списка запущенных бизнес-процессов в формате `{"field_1": "value_1", ... "field_N": "value_N"}`, где
- `field_N` — [поле](#fields) шаблона для сортировки
- `value_N` — направление сортировки

Направление сортировки может принимать значения:
- `asc` — по возрастанию
- `desc` — по убыванию
  
Можно указать несколько полей для сортировки, например, `{NAME: 'ASC', ID: 'DESC'}`.

Значение по умолчанию — `{ID: 'ASC'}` ||
|| **start**
[`integer`](../../data-types.md) | Параметр используется для управления постраничной навигацией.

Размер страницы результатов всегда статичный — 50 записей.

Чтобы выбрать вторую страницу результатов, необходимо передавать значение `50`. Чтобы выбрать третью страницу результатов — значение `100` и так далее.

Формула расчета значения параметра `start`:

`start = (N - 1) * 50`, где `N` — номер нужной страницы ||
|#

### Поля шаблона {#fields}

#|
|| **Название**
`тип` | **Описание**||
|| **ID**
[`integer`](../../data-types.md) | Идентификатор шаблона бизнес-процесса ||
|| **MODULE_ID**
[`string`](../../data-types.md) | Идентификатор модуля по документу. Возможные значения:
- `crm` — CRM
- `lists` — универсальные списки
- `disk` — диск ||
|| **ENTITY**
[`string`](../../data-types.md) | Идентификатор объекта по документу. Возможные значения:

CRM
- `CCrmDocumentLead` — лиды
- `CCrmDocumentContact` — контакты
- `CCrmDocumentCompany` — компании
- `CCrmDocumentDeal` — сделки
- `Bitrix\Crm\Integration\BizProc\Document\Quote` — коммерческие предложения
- `Bitrix\Crm\Integration\BizProc\Document\SmartInvoice` — счета
- `Bitrix\Crm\Integration\BizProc\Document\Dynamic` — смарт-процессы

Списки
- `BizprocDocument` — процессы в ленте новостей
- `Bitrix\Lists\BizprocDocumentLists` — списки в группах

Диск
- `Bitrix\Disk\BizProcDocument` ||
|| **DOCUMENT_TYPE**
[`integer`](../../data-types.md) | Тип документа. Возможные значения:
crm:
- `LEAD` — лиды
- `CONTACT` — контакты
- `COMPANY` — компании
- `DEAL` — сделки
- `QUOTE` — коммерческие предложения
- `SMART_INVOICE` — счета
- `DYNAMIC_XXX` — смарт-процессы, где XXX — идентификатор смарт-процесса

списки:
- `iblock_XXX` — информационный блок, где XXX — идентификатор информационного блока

диск:
- `STORAGE_XXX` — хранилище диска, где XXX — идентификатор хранилища
 ||
|| **AUTO_EXECUTE**
[`integer`](../../data-types.md) | Флаг автозапуска. Может принимать значения:

- `0` — без автозапуска
- `1` — запуск на создание
- `2` — запуск на изменение
- `3` — запуск на создание и изменение
||
|| **NAME**
[`string`](../../data-types.md) | Название шаблона ||
|| **TEMPLATE**
[`array`](../../data-types.md) | Массив с описанием структуры действий шаблона ||
|| **PARAMETERS**
[`array`](../../data-types.md) | Параметры шаблона ||
|| **VARIABLES**
[`array`](../../data-types.md) | Переменные шаблона ||
|| **CONSTANTS**
[`array`](../../data-types.md) | Константы шаблона ||
|| **MODIFIED**
[`datetime`](../../data-types.md) | Дата последнего изменения ||
|| **IS_MODIFIED**
[`boolean`](../../data-types.md) | Был ли изменен шаблон. Возможные значения:
- `Y` — да, был изменен
- `N` — нет

Опция нужна для [типовых шаблонов](https://helpdesk.bitrix24.ru/open/5415841/) бизнес-процессов ||
|| **USER_ID**
[`integer`](../../data-types.md) | Идентификатор пользователя, который создал или изменил шаблон ||
|| **SYSTEM_CODE**
[`string`](../../data-types.md) | Системный код шаблона.

Нужен для идентификации шаблонов типовых бизнес-процессов или шаблонов, созданных приложением ||
|#

## Примеры кода

{% include [Сноска о примерах](../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"select":["ID","NAME","USER_ID","SYSTEM_CODE"],"filter":{"MODULE_ID":"lists","AUTO_EXECUTE":0},"order":{"ID":"DESC"}}' \
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/bizproc.workflow.template.list
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"select":["ID","NAME","USER_ID","SYSTEM_CODE"],"filter":{"MODULE_ID":"lists","AUTO_EXECUTE":0},"order":{"ID":"DESC"},"auth":"**put_access_token_here**"}' \
    https://**put_your_bitrix24_address**/rest/bizproc.workflow.template.list
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    // Shape of each WorkflowTemplateItem returned in result[]
    type WorkflowTemplateItem = {
      ID: string
      NAME: string
      USER_ID: string
      SYSTEM_CODE: string
    }

    try {
      // bizproc.workflow.template.list returns a single page (max 50 records). For the whole result set
      // use a list helper: $b24.actions.v2.callList.make() returns every record as one
      // array, $b24.actions.v2.fetchList.make() yields them in chunks (async generator).
      // NOTE: the list helpers do not accept `order` (it is excluded from their params, so
      // passing it is a TS error) — keep this call.make + `start` variant when sort matters.
      const response = await $b24.actions.v2.call.make<WorkflowTemplateItem[]>({
        method: 'bizproc.workflow.template.list',
        params: {
          select: [
            'ID',
            'NAME',
            'USER_ID',
            'SYSTEM_CODE',
          ],
          filter: {
            MODULE_ID: 'lists',
            AUTO_EXECUTE: 0,
          },
          order: {
            ID: 'DESC',
          },
          start: 0,
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Templates on this page:', result.length, result)
      }
    } catch (error) {
      // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
      console.error(error)
    }
    ```

- JS (UMD)

    ```html
    <!-- Load the SDK (UMD build); it is exposed as the global B24Js -->
    <script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js"></script>
    <script>
      async function fetchWorkflowTemplateList() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          // bizproc.workflow.template.list returns a single page (max 50 records). For the whole result set
          // use a list helper: $b24.actions.v2.callList.make() returns every record as one
          // array, $b24.actions.v2.fetchList.make() yields them in chunks (async generator).
          // NOTE: the list helpers do not accept `order` (it is excluded from their params, so
          // passing it is a TS error) — keep this call.make + `start` variant when sort matters.
          const response = await $b24.actions.v2.call.make({
            method: 'bizproc.workflow.template.list',
            params: {
              select: [
                'ID',
                'NAME',
                'USER_ID',
                'SYSTEM_CODE',
              ],
              filter: {
                MODULE_ID: 'lists',
                AUTO_EXECUTE: 0,
              },
              order: {
                ID: 'DESC',
              },
              start: 0,
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('Templates on this page:', result.length, result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', fetchWorkflowTemplateList)
    </script>
    ```

- PHP

	```php
	try {
		$result = $serviceBuilder
			->getBizProcScope()
			->template()
			->list(
				['ID', 'MODULE_ID', 'ENTITY', 'DOCUMENT_TYPE', 'AUTO_EXECUTE', 'NAME', 'TEMPLATE', 'PARAMETERS', 'VARIABLES', 'CONSTANTS', 'MODIFIED', 'IS_MODIFIED', 'USER_ID', 'SYSTEM_CODE'],
				[]
			);
		foreach ($result->getTemplates() as $template) {
			print("ID: " . $template->ID . "\n");
			print("MODULE_ID: " . $template->MODULE_ID . "\n");
			print("ENTITY: " . $template->ENTITY . "\n");
			print("DOCUMENT_TYPE: " . json_encode($template->DOCUMENT_TYPE) . "\n");
			print("AUTO_EXECUTE: " . ($template->AUTO_EXECUTE ? $template->AUTO_EXECUTE->value : 'null') . "\n");
			print("NAME: " . $template->NAME . "\n");
			print("TEMPLATE: " . json_encode($template->TEMPLATE) . "\n");
			print("PARAMETERS: " . json_encode($template->PARAMETERS) . "\n");
			print("VARIABLES: " . json_encode($template->VARIABLES) . "\n");
			print("CONSTANTS: " . json_encode($template->CONSTANTS) . "\n");
			print("MODIFIED: " . ($template->MODIFIED ? $template->MODIFIED->format(DATE_ATOM) : 'null') . "\n");
			print("IS_MODIFIED: " . ($template->IS_MODIFIED ? 'true' : 'false') . "\n");
			print("USER_ID: " . $template->USER_ID . "\n");
			print("SYSTEM_CODE: " . $template->SYSTEM_CODE . "\n");
			print("\n");
		}
	} catch (Throwable $e) {
		print("Error: " . $e->getMessage() . "\n");
	}
	```

- BX24.js

    ```js
    BX24.callMethod(
        'bizproc.workflow.template.list',
        {
            select: [
                'ID',
                'NAME',
                'USER_ID',
                'SYSTEM_CODE'
            ],
            filter: {
                MODULE_ID: 'lists',
                AUTO_EXECUTE: 0
            },
            order: {
                ID: 'DESC'
            }
        },
        function(result)
        {
            if(result.error())
                alert("Error: " + result.error());
            else
                console.log(result.data());
        }
    );
    ```

- PHP CRest

    ```php
    require_once('crest.php');

    $result = CRest::call(
        'bizproc.workflow.template.list',
        [
            'select' => [
                'ID',
                'NAME',
                'USER_ID',
                'SYSTEM_CODE'
            ],
            'filter' => [
                'MODULE_ID' => 'lists',
                'AUTO_EXECUTE' => 0
            ],
            'order' => [
                'ID' => 'DESC'
            ]
        ]
    );

    echo '<PRE>';
    print_r($result);
    echo '</PRE>';
    ```

{% endlist %}

## Обработка ответа

HTTP-статус: **200**

```json
{
    "result": [
        {
            "ID": "525",
            "NAME": "Вывести время",
            "USER_ID": "503",
            "SYSTEM_CODE": "rest_app_5"
        },
        {
           "ID": "379",
           ... 
        }
        ...
    ],
    "total": 34,
    "time": {
        "start": 1737535822.539526,
        "finish": 1737535822.564579,
        "duration": 0.025053024291992188,
        "processing": 0.0019738674163818359,
        "date_start": "2025-01-22T11:50:22+03:00",
        "date_finish": "2025-01-22T11:50:22+03:00",
        "operating_reset_at": 1737536422,
        "operating": 0
    }
}
```

### Возвращаемые данные

#|
|| **Название**
`тип` | **Описание** ||
|| **result**
[`object`](../../data-types.md) | Корневой элемент ответа. 

Cодержит массив объектов с информацией о шаблонах бизнес-процессов.

Каждый объект содержит [поля](#fields) шаблона, указанные в параметре `SELECT` ||
|| **total**
[`integer`](../../data-types.md) | Общее количество найденных записей ||
|| **time**
[`time`](../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**

```json
{
    "error": "ACCESS_DENIED",
    "error_description": "Access denied!",
}
```

{% include notitle [обработка ошибок](../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Сообщение об ошибке** | **Описание** ||
|| `ACCESS_DENIED` | Access denied! | Метод запустил не администратор ||
|#

{% include [системные ошибки](../../../_includes/system-errors.md) %}

## Продолжите изучение 

- [{#T}](./index.md)
- [{#T}](./bizproc-workflow-template-add.md)
- [{#T}](./bizproc-workflow-template-update.md)
- [{#T}](./bizproc-workflow-template-delete.md)