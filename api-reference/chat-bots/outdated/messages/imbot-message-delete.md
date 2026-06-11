# Удалить сообщение imbot.message.delete

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../scopes/permissions.md)
>
> Кто может выполнять метод: авторизованный пользователь приложения, которое зарегистрировало чат-бота. Метод работает только с ботами этого приложения.

{% note warning "DEPRECATED" %}

Развитие метода остановлено. Используйте [imbot.v2.Chat.Message.delete](../../chat-bots-v2/imbot.v2/messages/chat-message-delete.md).

{% endnote %}

Метод `imbot.message.delete` удаляет сообщение чат-бота.

## Параметры метода

{% include [Сноска о параметрах](../../../../_includes/required.md) %}

#|
|| **Название**
`Тип` | **Описание** ||
|| **BOT_ID**
[`integer`](../../../data-types.md) | Идентификатор чат-бота. Получить идентификатор бота можно с помощью метода [imbot.bot.list](../bots/imbot-bot-list.md).

Если параметр не передан, метод ищет первого бота, который зарегистрирован текущим приложением ||
|| **MESSAGE_ID***
[`integer`](../../../data-types.md) | Идентификатор сообщения для удаления. Значение должно быть больше `0`.

Для сообщений, которые отправлены ботом через REST, идентификатор возвращает метод [imbot.message.add](./imbot-message-add.md) ||
|| **COMPLETE**
[`string`](../../../data-types.md) | Режим удаления.

Допустимые значения:
- `Y` — удалить полностью, без отметки об удалении
- `N` — обычное удаление, значение по умолчанию ||
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
      -d '{"BOT_ID":39,"MESSAGE_ID":19880117,"COMPLETE":"N","CLIENT_ID":"**put_your_client_id_here**"}' /
      https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.message.delete
    ```

- cURL (OAuth)

    ```bash
    curl -X POST /
      -H "Content-Type: application/json" /
      -H "Accept: application/json" /
      -d '{"BOT_ID":39,"MESSAGE_ID":19880117,"COMPLETE":"N","auth":"**put_access_token_here**"}' /
      https://**put_your_bitrix24_address**/rest/imbot.message.delete
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
        method: 'imbot.message.delete',
        params: {
          BOT_ID: 39,
          MESSAGE_ID: 19880117,
          COMPLETE: 'N',
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Message deleted:', result)
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
      async function deleteMessage() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.message.delete',
            params: {
              BOT_ID: 39,
              MESSAGE_ID: 19880117,
              COMPLETE: 'N',
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('Message deleted:', result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', deleteMessage)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.message.delete',
                [
                    'BOT_ID' => 39,
                    'MESSAGE_ID' => 19880117,
                    'COMPLETE' => 'N',
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        if ($result->error()) {
            echo 'Error: ' . $result->error();
        } else {
            echo 'Deleted: ' . ($result->data() ? 'true' : 'false');
        }
    } catch (Throwable $exception) {
        error_log($exception->getMessage());
        echo 'Error deleting message: ' . $exception->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.message.delete',
        {
            BOT_ID: 39,
            MESSAGE_ID: 19880117,
            COMPLETE: 'N',
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
        'imbot.message.delete',
        [
            'BOT_ID' => 39,
            'MESSAGE_ID' => 19880117,
            'COMPLETE' => 'N',
        ]
    );

    if (!empty($result['error'])) {
        echo 'Error: ' . $result['error_description'];
    } else {
        echo 'Deleted: ' . ($result['result'] ? 'true' : 'false');
    }
    ```

{% endlist %}

## Обработка ответа

HTTP-код: **200**

```json
{
    "result": true,
    "time": {
        "start": 1728626400.123,
        "finish": 1728626400.234,
        "duration": 0.111,
        "processing": 0.045,
        "date_start": "2024-10-11T10:00:00+03:00",
        "date_finish": "2024-10-11T10:00:00+03:00",
        "operating_reset_at": 1762349466,
        "operating": 0
    }
}
```

## Возвращаемые данные

#|
|| **Название**
`Тип` | **Описание** ||
|| **result**
[`boolean`](../../../data-types.md) | `true`, если сообщение удалено без ошибки ||
|| **time**
[`time`](../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**, **403**

```json
{
    "error": "CANT_EDIT_MESSAGE",
    "error_description": "Time has expired for modification or you don't have access"
}
```

{% include notitle [Обработка ошибок](../../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Описание** | **Значение** ||
|| `BOT_ID_ERROR` | Bot not found | Бот не найден или у приложения нет доступного бота для автоподстановки `BOT_ID` ||
|| `APP_ID_ERROR` | Bot was installed by another rest application | Переданный `BOT_ID` принадлежит другому приложению ||
|| `MESSAGE_ID_ERROR` | Message ID can't be empty | Не передан корректный идентификатор сообщения `MESSAGE_ID` ||
|| `CANT_EDIT_MESSAGE` | Time has expired for modification or you don't have access | Истекло время удаления сообщения или нет доступа к сообщению ||
|#

{% include [Системные ошибки](../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [{#T}](./imbot-message-add.md)
- [{#T}](./imbot-message-update.md)
- [{#T}](./imbot-message-like.md)
- [{#T}](./events/on-imbot-message-delete.md)
- [Пример ЭхоБота](https://dev.1c-bitrix.ru/~b24bots)



