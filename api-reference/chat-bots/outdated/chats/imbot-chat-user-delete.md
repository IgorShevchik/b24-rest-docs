# Исключить участников из чата imbot.chat.user.delete

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../scopes/permissions.md)
>
> Кто может выполнять метод: авторизованный пользователь приложения, которое зарегистрировало чат-бота

{% note warning "DEPRECATED" %}

Развитие метода остановлено. Используйте [imbot.v2.Chat.User.delete](../../chat-bots-v2/imbot.v2/chats/chat-user-delete.md).

{% endnote %}

Метод `imbot.chat.user.delete` исключает пользователя из чата.

## Параметры метода

{% include [Сноска об обязательных параметрах](../../../../_includes/required.md) %}

#|
|| **Название**
`тип` | **Описание** ||
|| **CHAT_ID***
[`integer`](../../../data-types.md) | Идентификатор чата.

Идентификатор можно получить с помощью метода [imbot.chat.get](./imbot-chat-get.md) ||
|| **USER_ID***
[`integer`](../../../data-types.md) | Идентификатор пользователя, которого нужно удалить из чата.

Получить идентификатор пользователя можно с помощью метода [imbot.chat.user.list](./imbot-chat-user-list.md) ||
|| **BOT_ID**
[`integer`](../../../data-types.md) | Идентификатор чат-бота. Получить идентификатор бота можно с помощью метода [imbot.bot.list](../bots/imbot-bot-list.md).

Если параметр не передан, метод ищет первого бота, который зарегистрирован текущим приложением ||
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
    -d '{"CHAT_ID":2725,"USER_ID":1269,"CLIENT_ID":"**put_your_client_id_here**"}' /
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.chat.user.delete
    ```

- cURL (OAuth)

    ```bash
    curl -X POST /
    -H "Content-Type: application/json" /
    -H "Accept: application/json" /
    -d '{"CHAT_ID":2725,"USER_ID":1269,"auth":"**put_access_token_here**"}' /
    https://**put_your_bitrix24_address**/rest/imbot.chat.user.delete
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
        method: 'imbot.chat.user.delete',
        params: {
          CHAT_ID: 2725,
          USER_ID: 1269,
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('User deleted from chat:', result)
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
      async function deleteChatUser() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.chat.user.delete',
            params: {
              CHAT_ID: 2725,
              USER_ID: 1269,
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('User deleted from chat:', result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', deleteChatUser)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.chat.user.delete',
                [
                    'CHAT_ID' => 2725,
                    'USER_ID' => 1269
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        echo 'Success: ' . print_r($result, true);
        processData($result);

    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error deleting chat user: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.chat.user.delete',
        {
            CHAT_ID: 2725,
            USER_ID: 1269,
        },
        function (result)
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
        'imbot.chat.user.delete',
        [
            'CHAT_ID' => 2725,
            'USER_ID' => 1269
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
        "start": 1771936672,
        "finish": 1771936672.409352,
        "duration": 0.40935206413269043,
        "processing": 0,
        "date_start": "2026-02-24T15:37:52+03:00",
        "date_finish": "2026-02-24T15:37:52+03:00",
        "operating_reset_at": 1771937272,
        "operating": 0.23420310020446777
    }
}
```

### Возвращаемые данные

#|
|| **Название**
`тип` | **Описание** ||
|| **result**
[`boolean`](../../../data-types.md) | `true`, если пользователь удален из чата ||
|| **time**
[`time`](../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**, **403**

```json
{
    "error": "USER_ID_EMPTY",
    "error_description": "User ID can't be empty"
}
```

{% include notitle [обработка ошибок](../../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Описание** | **Значение** ||
|| `CHAT_ID_EMPTY` | Chat ID can't be empty | Не передан `CHAT_ID` ||
|| `USER_ID_EMPTY` | User ID can't be empty | Не передан `USER_ID` ||
|| `ACCESS_ERROR` | Action unavailable | Операция недоступна для этого чата ||
|| `ACCESS_ERROR` | It is forbidden to delete users of this chat | Нельзя удалять пользователей из этого чата ||
|| `ACCESS_ERROR` | LEAVE_OWNER_FORBIDDEN | Нельзя удалить владельца чата без передачи прав ||
|| `WRONG_REQUEST` | You don't have access or user isn't member in chat | Нет прав на удаление или пользователь не состоит в чате ||
|| `BOT_ID_ERROR` | Bot not found | Чат-бот не найден ||
|| `APP_ID_ERROR` | Bot was installed by another rest application | Чат-бот установлен другим приложением ||
|#

{% include [системные ошибки](../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [{#T}](./imbot-chat-add.md)
- [{#T}](./imbot-chat-user-add.md)
- [{#T}](./imbot-chat-set-manager.md)
- [{#T}](./imbot-chat-update-title.md)
- [{#T}](./imbot-chat-update-avatar.md)
- [{#T}](./imbot-chat-update-color.md)
- [{#T}](./imbot-chat-get.md)
- [{#T}](./imbot-dialog-get.md)
- [{#T}](./imbot-chat-user-list.md)
- [{#T}](./imbot-chat-leave.md)




