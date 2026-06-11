# Получить информацию о чате imbot.v2.Chat.get

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../../scopes/permissions.md)
>
> Кто может выполнять метод: владелец зарегистрированного бота

Метод `imbot.v2.Chat.get` возвращает информацию о чате. Бот должен быть участником чата.

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
|#

## Примеры кода

{% include [Сноска о примерах](../../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"botToken":"my_bot_token","dialogId":"chat5"}' \
      https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.v2.Chat.get
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"dialogId":"chat5","auth":"**put_access_token_here**"}' \
      https://**put_your_bitrix24_address**/rest/imbot.v2.Chat.get
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame, ISODate } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    // Shape of the payload returned in result (match the "response handling" section of the page)
    type ChatGetResult = {
      chat: {
        id: number
        dialogId: string
        name: string
        description: string
        type: string
        messageType: string
        owner: number
        color: string | null
        avatar: string
        extranet: boolean
        role: string
        permissions: Record<string, unknown>
        muteList: number[]
        managerList: number[]
        dateCreate: ISODate | null
        lastMessageId: number | null
        messageCount: number
        userCounter: number
      }
    }

    try {
      const response = await $b24.actions.v2.call.make<ChatGetResult>({
        method: 'imbot.v2.Chat.get',
        params: {
          botId: 456,
          dialogId: 'chat5',
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Chat:', result.chat.id, result.chat.name, result.chat.role)
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
      async function getChatInfo() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.v2.Chat.get',
            params: {
              botId: 456,
              dialogId: 'chat5',
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('Chat:', result.chat.id, result.chat.name, result.chat.role)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', getChatInfo)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.v2.Chat.get',
                [
                    'botId' => 456,
                    'dialogId' => 'chat5',
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        echo 'result: '. print_r($result, true);
    } catch (Throwable $exception) {
        error_log($exception->getMessage());
        echo 'Error: '. $exception->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.v2.Chat.get',
        {
            botId: 456,
            dialogId: 'chat5',
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
        'imbot.v2.Chat.get',
        [
            'botId' => 456,
            'dialogId' => 'chat5',
        ]
    );

    if (!empty($result['error'])) {
        echo 'Error: '. $result['error_description'];
    } else {
        echo 'Chat name: '. $result['result']['chat']['name'];
    }
    ```

{% endlist %}

## Обработка ответа

HTTP-статус: **200**

```json
{
    "result": {
        "chat": {
            "id": 5,
            "dialogId": "chat5",
            "name": "Support Chat",
            "description": "",
            "type": "chat",
            "messageType": "C",
            "owner": 456,
            "color": "#4ba984",
            "avatar": "",
            "extranet": false,
            "containsCollaber": false,
            "entityType": "",
            "entityId": "",
            "entityData1": "",
            "entityData2": "",
            "entityData3": "",
            "entityLink": {},
            "diskFolderId": 42,
            "role": "owner",
            "permissions": {},
            "muteList": [],
            "parentChatId": null,
            "parentMessageId": null,
            "isNew": false,
            "textFieldEnabled": "Y",
            "backgroundId": null,
            "dateCreate": "2025-01-15T10:00:00+03:00",
            "lastMessageId": 789,
            "lastMessageViews": "{}",
            "lastId": 789,
            "managerList": [],
            "markedId": null,
            "messageCount": 15,
            "public": "",
            "unreadId": null,
            "userCounter": 3
        }
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
[`object`](../../../../data-types.md) | Результат запроса ||
|| **result.chat**
[`Chat`](../../entities.md#chat) | Объект чата [(подробное описание)](#chat-object) ||
|| **time**
[`time`](../../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

### Поля объекта Chat {#chat-object}

#|
|| **Поле**
`Тип` | **Описание** ||
|| **id**
[`integer`](../../../../data-types.md) | Уникальный идентификатор чата ||
|| **dialogId**
[`string`](../../../../data-types.md) | Идентификатор диалога: `chat5` для групповых, `123` для личных ||
|| **name**
[`string`](../../../../data-types.md) | Название чата ||
|| **description**
[`string`](../../../../data-types.md) | Описание чата ||
|| **type**
[`string`](../../../../data-types.md) | Тип чата: `chat`, `open`, `channel` и другие ||
|| **owner**
[`integer`](../../../../data-types.md) | ID владельца чата ||
|| **color**
[`string\|null`](../../../../data-types.md) | Цвет чата в формате HEX ||
|| **avatar**
[`string`](../../../../data-types.md) | URL аватара чата. Пустая строка, если не установлен ||
|| **role**
[`string`](../../../../data-types.md) | Роль текущего пользователя: `owner`, `manager`, `member`, `guest`, `none` ||
|| **dateCreate**
[`string\|null`](../../../../data-types.md) | Дата создания чата в формате ISO 8601 ||
|| **lastMessageId**
[`integer\|null`](../../../../data-types.md) | ID последнего сообщения ||
|| **muteList**
[`array`](../../../../data-types.md) | Список ID пользователей, отключивших уведомления ||
|| **managerList**
[`array`](../../../../data-types.md) | Массив ID менеджеров чата ||
|#

Полное описание всех полей — на странице [Объекты и поля — Chat](../../entities.md#chat).

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
- [{#T}](./chat-update.md)
- [{#T}](./chat-user-list.md)
