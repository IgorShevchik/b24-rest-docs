# Список участников чата imbot.v2.Chat.User.list

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../../scopes/permissions.md)
>
> Кто может выполнять метод: владелец зарегистрированного бота

Метод `imbot.v2.Chat.User.list` возвращает список участников чата.

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
[`string`](../../../../data-types.md) | ID диалога. Для групповых чатов — `chat{chatId}` ||
|| **order**
[`object`](../../../../data-types.md) | Сортировка.

Доступные поля: `id`, `lastSendMessageId`, `userId`. Значение: `ASC` или `DESC`.

Пример: `{"id": "ASC"}` ||
|| **limit**
[`integer`](../../../../data-types.md) | Количество записей (1–200). По умолчанию `50` ||
|#

## Примеры кода

{% include [Сноска о примерах](../../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"botToken":"my_bot_token","dialogId":"chat5","order":{"id":"ASC"},"limit":50}' \
      https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.v2.Chat.User.list
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"dialogId":"chat5","order":{"id":"ASC"},"limit":50,"auth":"**put_access_token_here**"}' \
      https://**put_your_bitrix24_address**/rest/imbot.v2.Chat.User.list
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame, ISODate } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    // Shape of each ChatUserItem returned in result[]
    type ChatUserItem = {
      id: number
      active: boolean
      name: string
      firstName: string
      lastName: string
      workPosition: string
      color: string
      avatar: string
      gender: string
      birthday: string
      extranet: boolean
      bot: boolean
      connector: boolean
      externalAuthId: string
      status: string
      idle: boolean
      lastActivityDate: ISODate | null
      absent: boolean
      departments: number[]
      phones: false | Record<string, string>
      type: string
    }

    try {
      // imbot.v2.Chat.User.list returns a single page (max 50 records). For the whole result set
      // use a list helper: $b24.actions.v2.callList.make() returns every record as one
      // array, $b24.actions.v2.fetchList.make() yields them in chunks (async generator).
      // NOTE: the list helpers do not accept `order` (it is excluded from their params, so
      // passing it is a TS error) — keep this call.make + `start` variant when sort matters.
      const response = await $b24.actions.v2.call.make<ChatUserItem[]>({
        method: 'imbot.v2.Chat.User.list',
        params: {
          botId: 456,
          dialogId: 'chat5',
          order: { id: 'ASC' },
          limit: 50,
          start: 0,
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Chat users:', result.length, result)
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
      async function getChatUserList() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          // imbot.v2.Chat.User.list returns a single page (max 50 records). For the whole result set
          // use a list helper: $b24.actions.v2.callList.make() returns every record as one
          // array, $b24.actions.v2.fetchList.make() yields them in chunks (async generator).
          // NOTE: the list helpers do not accept `order` (it is excluded from their params, so
          // passing it is a TS error) — keep this call.make + `start` variant when sort matters.
          const response = await $b24.actions.v2.call.make({
            method: 'imbot.v2.Chat.User.list',
            params: {
              botId: 456,
              dialogId: 'chat5',
              order: { id: 'ASC' },
              limit: 50,
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
          console.info('Chat users:', result.length, result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', getChatUserList)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.v2.Chat.User.list',
                [
                    'botId' => 456,
                    'dialogId' => 'chat5',
                    'order' => ['id' => 'ASC'],
                    'limit' => 50,
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
        'imbot.v2.Chat.User.list',
        {
            botId: 456,
            dialogId: 'chat5',
            order: { id: 'ASC' },
            limit: 50,
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
        'imbot.v2.Chat.User.list',
        [
            'botId' => 456,
            'dialogId' => 'chat5',
            'order' => ['id' => 'ASC'],
            'limit' => 50,
        ]
    );

    if (!empty($result['error'])) {
        echo 'Error: ' . $result['error_description'];
    } else {
        foreach ($result['result'] as $user) {
            echo $user['id'] . ': ' . $user['name'] . "\n";
        }
    }
    ```

{% endlist %}

## Обработка ответа

HTTP-статус: **200**

```json
{
    "result": [
        {
            "id": 1,
            "active": true,
            "name": "John Smith",
            "firstName": "John",
            "lastName": "Smith",
            "workPosition": "Developer",
            "color": "#ab7761",
            "avatar": "",
            "gender": "M",
            "birthday": "15-03",
            "extranet": false,
            "bot": false,
            "connector": false,
            "externalAuthId": "default",
            "status": "online",
            "idle": false,
            "lastActivityDate": "2025-01-15T14:25:00+03:00",
            "absent": false,
            "departments": [7],
            "phones": false,
            "type": "employee"
        },
        {
            "id": 2,
            "active": true,
            "name": "Anna Davis",
            "firstName": "Anna",
            "lastName": "Davis",
            "workPosition": "Manager",
            "color": "#5b7e91",
            "avatar": "",
            "gender": "F",
            "birthday": "22-08",
            "extranet": false,
            "bot": false,
            "connector": false,
            "externalAuthId": "default",
            "status": "online",
            "idle": false,
            "lastActivityDate": "2025-01-15T14:20:00+03:00",
            "absent": false,
            "departments": [12],
            "phones": false,
            "type": "employee"
        }
    ],
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
[`User[]`](../../entities.md#user) | Массив участников чата. Описание полей объекта — [User](../../entities.md#user) ||
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
- [{#T}](./chat-user-add.md)
- [{#T}](./chat-user-delete.md)
- [{#T}](./chat-manager-add.md)
