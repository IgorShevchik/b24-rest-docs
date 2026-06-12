# Запустить бизнес-процесс bizproc.workflow.start

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`bizproc`](../scopes/permissions.md)
>
> Кто может выполнять метод: администратор

Метод `bizproc.workflow.start` запускает новый бизнес-процесс.

Запустить бизнес-процесс используя REST можно только на платных тарифах, demo лицензиях и лицензиях NFR.

## Параметры метода

{% include [Сноска об обязательных параметрах](../../_includes/required.md) %}

#|
|| **Название**
`тип` | **Описание** ||
|| **TEMPLATE_ID***
[`integer`](../data-types.md) | Идентификатор шаблона бизнес-процесса ||
|| **DOCUMENT_ID***
[`array`](../data-types.md) | Идентификатор документа для запуска бизнес-процесса в формате [`модуль`, `объект`, `ID_элемента`].

Примеры записей для разных вариантов документов:

- Лид — `['crm', 'CCrmDocumentLead', 'LEAD_777']`
- Компания — `['crm', 'CCrmDocumentCompany', 'COMPANY_777']`
- Контакт — `['crm', 'CCrmDocumentContact', 'CONTACT_777']`
- Сделка — `['crm', 'CCrmDocumentDeal', 'DEAL_777']`
- Коммерческое предложение — `['crm', 'Bitrix\Crm\Integration\BizProc\Document\Quote', 'QUOTE_777']`
- Файл диска — `['disk', 'Bitrix\Disk\BizProcDocument', '777']`
- Документ процессов в ленте новостей — `['lists', 'BizprocDocument', '777']`
- Документ списков — `['lists', 'Bitrix\Lists\BizprocDocumentLists', '777']`
- Элемент смарт-процесса — `['crm', 'Bitrix\Crm\Integration\BizProc\Document\Dynamic', 'DYNAMIC_147_1']`, где `147` — это `ID` смарт-процесса, `1` — `ID` элемента смарт-процесса
- Счет — `['crm', 'Bitrix\Crm\Integration\BizProc\Document\SmartInvoice', 'SMART_INVOICE_3']`
||
|| **PARAMETERS**
[`object`](../data-types.md) | Значения параметров шаблона бизнес-процесса.

Используется, если у шаблона есть параметры.

Для передачи значения в параметр типа «Привязка к пользователю» используйте запись вида `user_ID`. Например:

```php
PARAMETERS: {
    'resp_employee': user_14 // ID сотрудника — 14
}
```
||
|#

## Примеры кода

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"TEMPLATE_ID":1,"DOCUMENT_ID":["crm","CCrmDocumentLead","LEAD_1"],"PARAMETERS":{"Parameter1":"user_1"}}' \
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/bizproc.workflow.start
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"TEMPLATE_ID":1,"DOCUMENT_ID":["crm","CCrmDocumentLead","LEAD_1"],"PARAMETERS":{"Parameter1":"user_1"},"auth":"**put_access_token_here**"}' \
    https://**put_your_bitrix24_address**/rest/bizproc.workflow.start
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    try {
      const response = await $b24.actions.v2.call.make<string>({
        method: 'bizproc.workflow.start',
        params: {
          TEMPLATE_ID: 1,
          DOCUMENT_ID: [
            'crm',
            'CCrmDocumentLead',
            'LEAD_1',
          ],
          PARAMETERS: {
            'Parameter1': 'user_1',
          },
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Started workflow ID:', result)
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
      async function startWorkflow() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'bizproc.workflow.start',
            params: {
              TEMPLATE_ID: 1,
              DOCUMENT_ID: [
                'crm',
                'CCrmDocumentLead',
                'LEAD_1',
              ],
              PARAMETERS: {
                'Parameter1': 'user_1',
              },
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('Started workflow ID:', result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', startWorkflow)
    </script>
    ```

- PHP


    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'bizproc.workflow.start',
                [
                    'TEMPLATE_ID' => 1,
                    'DOCUMENT_ID' => [
                        'crm',
                        'CCrmDocumentLead',
                        'LEAD_1'
                    ],
                    'PARAMETERS' => [
                        'Parameter1' => 'user_1'
                    ],
                ]
            );
    
        $result = $response
            ->getResponseData()
            ->getResult();
    
        echo 'Success: ' . print_r($result, true);
        // Нужная вам логика обработки данных
        processData($result);
    
    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error starting workflow: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(	
        'bizproc.workflow.start',
        {
            TEMPLATE_ID: 1,
            DOCUMENT_ID: [
                'crm',
                'CCrmDocumentLead',
                'LEAD_1'
            ],
            PARAMETERS: {
                'Parameter1': 'user_1'
            },
        },
        function(result) {
            console.log('response', result.answer);
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
        'bizproc.workflow.start',
        [
            'TEMPLATE_ID' => 1,
            'DOCUMENT_ID' => [
                'crm',
                'CCrmDocumentLead',
                'LEAD_1'
            ],
            'PARAMETERS' => [
                'Parameter1' => 'user_1'
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
    "result": "66e81a641752f8.56521481",
    "time": {
        "start": 1726476060.581428,
        "finish": 1726476060.813776,
        "duration": 0.23234796524047852,
        "processing": 0.002630949020385742,
        "date_start": "2024-09-16T08:41:00+00:00",
        "date_finish": "2024-09-16T08:41:00+00:00",
        "operating_reset_at": 1726476660,
        "operating": 0,
    },
}
```

### Возвращаемые данные

#|
|| **Название**
`тип` | **Описание** ||
|| **result**
[`string`](../data-types.md) | Корневой элемент ответа.

Возвращает идентификатор запущенного бизнес-процесса ||
|| **time**
[`time`](../data-types.md) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**

```json
{
    "error": "ERROR_WRONG_WORKFLOW_ID",
    "error_description": "Empty TEMPLATE_ID",
}
```

{% include notitle [обработка ошибок](../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Статус** |**Код** | **Описание** | **Значение** ||
|| `400` | `ERROR_WRONG_WORKFLOW_ID` | Empty TEMPLATE_ID | Передали пустой входной параметр `TEMPLATE_ID` ||
|| `400` | `ERROR_WRONG_WORKFLOW_ID` | Template not found | Не был найден шаблон бизнес-процесса по переданному значению `TEMPLATE_ID` ||
|| `400` | Пустое значение | Wrong DOCUMENT_ID! | Передан неправильный `DOCUMENT_ID` ||
|| `400` | Пустое значение | Incorrect document type! | Не удалось определить тип документа по переданному `DOCUMENT_ID` ||
|| `400` | Пустое значение | Template type and DOCUMENT_ID mismatch! | Тип документа в шаблоне и вычисленный по `DOCUMENT_ID` тип документа не совпадают.

Попытка запустить шаблон не на той сущности, для которой он был создан ||
|| `403` | `ACCESS_DENIED` | Access denied! | Метод запустил не администратор ||
|#

{% include [системные ошибки](../../_includes/system-errors.md) %}

## Продолжите изучение 

- [{#T}](./index.md)
- [{#T}](./bizproc-workflow-instances.md)
- [{#T}](./bizproc-workflow-terminate.md)
- [{#T}](./bizproc-workflow-kill.md)
