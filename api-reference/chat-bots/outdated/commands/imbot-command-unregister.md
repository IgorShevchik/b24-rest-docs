# Удалить команду imbot.command.unregister

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../scopes/permissions.md)
>
> Кто может выполнять метод: пользователь приложения, которое зарегистрировало чат-бота

{% note warning "DEPRECATED" %}

Развитие метода остановлено. Используйте [imbot.v2.Command.unregister](../../chat-bots-v2/imbot.v2/commands/command-unregister.md).

{% endnote %}

Метод `imbot.command.unregister` удаляет зарегистрированную команду чат-бота.

## Параметры метода

{% include [Сноска об обязательных параметрах](../../../../_includes/required.md) %}

#|
|| **Название**
`тип` | **Описание** ||
|| **COMMAND_ID***
[`integer`](../../../data-types.md) | Идентификатор команды для удаления ||
|| **CLIENT_ID**
[`string`](../../../data-types.md) | Параметр обязателен только для вебхуков. Передавайте тот же CLIENT_ID, который был указан при регистрации чат-бота ||
|#

## Примеры кода

{% include [Сноска о примерах](../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST /
    -H "Content-Type: application/json" /
    -H "Accept: application/json" /
    -d '{"COMMAND_ID":99,"CLIENT_ID":"**put_your_client_id_here**"}' /
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.command.unregister
    ```

- cURL (OAuth)

    ```bash
    curl -X POST /
    -H "Content-Type: application/json" /
    -H "Accept: application/json" /
    -d '{"COMMAND_ID":99,"auth":"**put_access_token_here**"}' /
    https://**put_your_bitrix24_address**/rest/imbot.command.unregister
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    try {
      const response = await $b24.actions.v2.call.make<boolean>({
        method: 'imbot.command.unregister',
        params: {
          COMMAND_ID: 99,
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Command unregistered:', result)
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
      async function unregisterCommand() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.command.unregister',
            params: {
              COMMAND_ID: 99,
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('Command unregistered:', result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', unregisterCommand)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.command.unregister',
                [
                    'COMMAND_ID' => 99
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        echo 'Success: ' . print_r($result, true);
        processData($result);

    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error unregistering command: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.command.unregister',
        {
            COMMAND_ID: 99
        },
        function(result)
        {
            if (result.error())
                console.error(result.error());
            else
                console.dir(result.data());
        }
    );
    ```

- PHP CRest

    ```php
    require_once('crest.php');

    $result = CRest::call(
        'imbot.command.unregister',
        [
            'COMMAND_ID' => 99
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
    "result": true,
    "time": {
        "start": 1772105363,
        "finish": 1772105363.56206,
        "duration": 0.5620601177215576,
        "processing": 0,
        "date_start": "2026-02-26T14:29:23+03:00",
        "date_finish": "2026-02-26T14:29:23+03:00",
        "operating_reset_at": 1772105963,
        "operating": 0
    }
}
```

### Возвращаемые данные

#|
|| **Название**
`тип` | **Описание** ||
|| **result**
[`boolean`](../../../data-types.md) | `true`, если команда успешно удалена ||
|| **time**
[`time`](../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**

```json
{
    "error": "COMMAND_ID_ERROR",
    "error_description": "Command not found"
}
```

{% include notitle [обработка ошибок](../../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Описание** | **Значение** ||
|| `COMMAND_ID_ERROR` | Command not found | Команда не найдена ||
|| `APP_ID_ERROR` | Command was installed by another rest application | Команда зарегистрирована другим приложением ||
|| `WRONG_REQUEST` | Command can't be deleted | Не удалось удалить команду ||
|#

{% include [системные ошибки](../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [{#T}](./imbot-command-register.md)
- [{#T}](./imbot-command-update.md)
- [{#T}](./imbot-command-answer.md)
- [{#T}](./events/on-im-command-add.md)




