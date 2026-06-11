# Получить ссылку для скачивания файла im.v2.File.download

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`im`](../../../../scopes/permissions.md)
>
> Кто может выполнять метод: авторизованный пользователь

Метод `im.v2.File.download` возвращает ссылку для скачивания файла из чата.

## Параметры метода

{% include [Сноска о параметрах](../../../../../_includes/required.md) %}

#|
|| **Название**
`Тип` | **Описание** ||
|| **dialogId***
[`string`](../../../../data-types.md) | ID диалога. Для групповых чатов — `chat{chatId}`, для личных — `{userId}` ||
|| **fileId***
[`integer`](../../../../data-types.md) | ID файла на Диске. Можно получить из ответа метода [im.v2.File.upload](./file-upload.md) ||
|#

## Примеры кода

{% include [Сноска о примерах](../../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"dialogId":"chat5","fileId":138}' \
      https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/im.v2.File.download
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"dialogId":"chat5","fileId":138,"auth":"**put_access_token_here**"}' \
      https://**put_your_bitrix24_address**/rest/im.v2.File.download
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    // Shape of the payload returned in result (match the "response handling" section of the page)
    type FileDownloadResult = {
      downloadUrl: string
    }

    try {
      const response = await $b24.actions.v2.call.make<FileDownloadResult>({
        method: 'im.v2.File.download',
        params: {
          dialogId: 'chat5',
          fileId: 138,
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info(result.downloadUrl)
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
      async function downloadFile() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'im.v2.File.download',
            params: {
              dialogId: 'chat5',
              fileId: 138,
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info(result.downloadUrl)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', downloadFile)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'im.v2.File.download',
                [
                    'dialogId' => 'chat5',
                    'fileId' => 138,
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        echo 'result: ' . print_r($result, true);
    } catch (Throwable $exception) {
        error_log($exception->getMessage());
        echo 'Error: ' . $exception->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'im.v2.File.download',
        {
            dialogId: 'chat5',
            fileId: 138,
        },
        function(result) {
            if (result.error()) {
                console.error(result.error().ex);
            } else {
                const downloadUrl = result.data().downloadUrl;
                window.open(downloadUrl);
            }
        }
    );
    ```

- PHP CRest

    ```php
    require_once('crest.php');

    $result = CRest::call(
        'im.v2.File.download',
        [
            'dialogId' => 'chat5',
            'fileId' => 138,
        ]
    );

    if (!empty($result['error'])) {
        echo 'Error: ' . $result['error_description'];
    } else {
        echo 'Download URL: ' . $result['result']['downloadUrl'];
    }
    ```

{% endlist %}

## Обработка ответа

HTTP-статус: **200**

```json
{
    "result": {
        "downloadUrl": "https://**put_your_bitrix24_address**/rest/download.json?token=im%7CaW..."
    },
    "time": {
        "start": 1728626400.123,
        "finish": 1728626400.234,
        "duration": 0.111,
        "processing": 0.045,
        "date_start": "2024-10-11T10:00:00+03:00",
        "date_finish": "2024-10-11T10:00:00+03:00"
    }
}
```

## Возвращаемые данные

#|
|| **Название**
`Тип` | **Описание** ||
|| **result**
[`object`](../../../../data-types.md) | Результат операции ||
|| **result.downloadUrl**
[`string`](../../../../data-types.md) | Одноразовая ссылка для скачивания файла. Ссылка содержит авторизационный токен, повторное использование не гарантируется ||
|| **time**
[`time`](../../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**, **403**

```json
{
    "error": "FILE_NOT_FOUND",
    "error_description": "File not found"
}
```

{% include notitle [Обработка ошибок](../../../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Описание** | **Значение** ||
|| `FILE_NOT_FOUND` | File not found | Файл не найден в указанном чате ||
|| `FILE_ACCESS_ERROR` | File access error | Нет прав на скачивание файла — файл не принадлежит указанному чату ||
|| `ACCESS_DENIED` | Access denied | Нет доступа к чату ||
|#

{% include [Системные ошибки](../../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [Журнал изменений API imbot.v2](../../change-log.md)
- [{#T}](./file-upload.md)
