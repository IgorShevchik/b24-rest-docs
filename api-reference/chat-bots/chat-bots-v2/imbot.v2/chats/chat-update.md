# Обновить свойства чата imbot.v2.Chat.update

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../../scopes/permissions.md)
>
> Кто может выполнять метод: владелец зарегистрированного бота

Метод `imbot.v2.Chat.update` обновляет свойства чата. Объединяет обновление заголовка, описания, цвета и аватара в одном вызове.

## Параметры метода

{% include [Сноска о параметрах](../../../../../_includes/required.md) %}

#|
|| **Название**
`Тип` | **Описание** ||
|| **botId***
[`integer`](../../../../data-types.md) | ID бота ||
|| **botToken**
[`string`](../../../../data-types.md) | Уникальный токен авторизации бота. Обязателен при авторизации через вебхук, не нужен для OAuth.

Передавайте тот же botToken, который был указан при регистрации чат-бота ||
|| **dialogId***
[`string`](../../../../data-types.md) | ID диалога. Для групповых чатов — `chat{chatId}`, для личных — `{userId}` ||
|| **fields***
[`object`](../../../../data-types.md) | Обновляемые свойства чата. Структура объекта описана [ниже](#fields) ||
|#

### Параметр fields {#fields}

#|
|| **Название**
`Тип` | **Описание** ||
|| **title**
[`string`](../../../../data-types.md) | Новое название чата ||
|| **description**
[`string`](../../../../data-types.md) | Новое описание чата ||
|| **color**
[`string`](../../../../data-types.md) | Цвет чата — [доступные цвета](#available-colors) ||
|| **avatar**
[`file`](../../../../data-types.md) | Новый аватар чата в формате [Base64](../../../../files/how-to-upload-files.md) ||
|#

### Доступные цвета {#available-colors}

#|
|| **Код** | **HEX** ||
|| `red` | `#df532d` ||
|| `green` | `#64a513` ||
|| `mint` | `#4ba984` ||
|| `lightBlue` | `#4ba5c3` ||
|| `darkBlue` | `#3e99ce` ||
|| `purple` | `#8474c8` ||
|| `aqua` | `#1eb4aa` ||
|| `pink` | `#f76187` ||
|| `lime` | `#58cc47` ||
|| `brown` | `#ab7761` ||
|| `azure` | `#29619b` ||
|| `khaki` | `#728f7a` ||
|| `sand` | `#ba9c7b` ||
|| `marengo` | `#556574` ||
|| `gray` | `#909090` ||
|| `graphite` | `#5e5f5e` ||
|#

## Примеры кода

{% include [Сноска о примерах](../../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"botToken":"my_bot_token","dialogId":"chat5","fields":{"title":"New Title","color":"azure"}}' \
      https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.v2.Chat.update
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"dialogId":"chat5","fields":{"title":"New Title","color":"azure"},"auth":"**put_access_token_here**"}' \
      https://**put_your_bitrix24_address**/rest/imbot.v2.Chat.update
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    // Shape of the payload returned in result (match the "response handling" section of the page)
    type ChatUpdateResult = {
      result: boolean
    }

    try {
      const response = await $b24.actions.v2.call.make<ChatUpdateResult>({
        method: 'imbot.v2.Chat.update',
        params: {
          botId: 456,
          dialogId: 'chat5',
          fields: {
            title: 'New Title',
            color: 'azure',
          },
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Chat updated:', result.result)
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
      async function updateChat() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.v2.Chat.update',
            params: {
              botId: 456,
              dialogId: 'chat5',
              fields: {
                title: 'New Title',
                color: 'azure',
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
          console.info('Chat updated:', result.result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', updateChat)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.v2.Chat.update',
                [
                    'botId' => 456,
                    'dialogId' => 'chat5',
                    'fields' => [
                        'title' => 'New Title',
                        'color' => 'azure',
                    ],
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
        'imbot.v2.Chat.update',
        {
            botId: 456,
            dialogId: 'chat5',
            fields: {
                title: 'New Title',
                color: 'azure',
            },
        },
        function(result) {
            if (result.error()) {
                console.error(result.error().ex);
            } else {
                console.log(result.data());
            }
        }
    );
    ```

- PHP CRest

    ```php
    require_once('crest.php');

    $result = CRest::call(
        'imbot.v2.Chat.update',
        [
            'botId' => 456,
            'dialogId' => 'chat5',
            'fields' => [
                'title' => 'New Title',
                'color' => 'azure',
            ],
        ]
    );

    if (!empty($result['error'])) {
        echo 'Error: ' . $result['error_description'];
    } else {
        echo 'Updated';
    }
    ```

{% endlist %}

## Обработка ответа

HTTP-статус: **200**

```json
{
    "result": {
        "result": true
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
|| **result.result**
[`boolean`](../../../../data-types.md) | `true` при успешном обновлении ||
|| **time**
[`time`](../../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**, **403**

```json
{
    "error": "ACCESS_DENIED",
    "error_description": "Access denied"
}
```

{% include notitle [Обработка ошибок](../../../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Описание** | **Значение** ||
|| `BOT_TOKEN_NOT_SPECIFIED` | Bot token is not specified | Не указан `botToken`. Обязателен при авторизации через вебхук ||
|| `BOT_ID_REQUIRED` | Bot ID is required | Не указан `botId` ||
|| `BOT_NOT_FOUND` | Bot not found | Бот не найден ||
|| `BOT_OWNERSHIP_ERROR` | Bot is registered by another application | Бот зарегистрирован другим приложением ||
|| `ACCESS_DENIED` | Access denied | Бот не является участником чата ||
|#

{% include [Системные ошибки](../../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [Журнал изменений API imbot.v2](../../change-log.md)
- [{#T}](./chat-add.md)
- [{#T}](./chat-get.md)
- [{#T}](./chat-user-add.md)
- [{#T}](./chat-set-owner.md)
