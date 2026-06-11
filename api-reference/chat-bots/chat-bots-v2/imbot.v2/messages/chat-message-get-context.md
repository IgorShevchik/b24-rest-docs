# Получить контекст сообщения imbot.v2.Chat.Message.getContext

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../../scopes/permissions.md)
>
> Кто может выполнять метод: владелец зарегистрированного бота

Метод `imbot.v2.Chat.Message.getContext` возвращает окно сообщений вокруг указанного. Используется для анализа истории диалога.

{% note warning "" %}

Метод доступен только для ботов типа `supervisor` и `personal`. Подробнее — [Типы ботов](../../index.md#bot-types).

{% endnote %}

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
|| **messageId***
[`integer`](../../../../data-types.md) | ID центрального сообщения ||
|| **range**
[`integer`](../../../../data-types.md) | Количество сообщений в каждую сторону от центрального (1–50). По умолчанию `50` ||
|#

## Примеры кода

{% include [Сноска о примерах](../../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"botToken":"my_bot_token","messageId":789,"range":20}' \
      https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.v2.Chat.Message.getContext
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"messageId":789,"range":20,"auth":"**put_access_token_here**"}' \
      https://**put_your_bitrix24_address**/rest/imbot.v2.Chat.Message.getContext
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame, ISODate } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    // Shape of the payload returned in result (match the "response handling" section of the page)
    type GetContextResult = {
      messages: {
        id: number
        chatId: number
        authorId: number
        date: ISODate | null
        text: string
        isSystem: boolean
        uuid: string
        forward: object | null
        params: object
        viewedByOthers: boolean
      }[]
      users: {
        id: number
        active: boolean
        name: string
        bot: boolean
        type: string
      }[]
      hasPrevPage: boolean
      hasNextPage: boolean
    }

    try {
      const response = await $b24.actions.v2.call.make<GetContextResult>({
        method: 'imbot.v2.Chat.Message.getContext',
        params: {
          botId: 456,
          messageId: 789,
          range: 20,
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info(result.messages.map(m => `${m.id}: ${m.text}`))
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
      async function getMessageContext() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.v2.Chat.Message.getContext',
            params: {
              botId: 456,
              messageId: 789,
              range: 20,
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info(result.messages.map(m => `${m.id}: ${m.text}`))
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', getMessageContext)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.v2.Chat.Message.getContext',
                [
                    'botId' => 456,
                    'messageId' => 789,
                    'range' => 20,
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
        'imbot.v2.Chat.Message.getContext',
        {
            botId: 456,
            messageId: 789,
            range: 20,
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
        'imbot.v2.Chat.Message.getContext',
        [
            'botId' => 456,
            'messageId' => 789,
            'range' => 20,
        ]
    );

    if (!empty($result['error'])) {
        echo 'Error: '. $result['error_description'];
    } else {
        foreach ($result['result']['messages'] as $message) {
            echo $message['id']. ': '. $message['text']. "\n";
        }
    }
    ```

{% endlist %}

## Обработка ответа

HTTP-статус: **200**

```json
{
    "result": {
        "messages": [
            {
                "id": 785,
                "chatId": 5,
                "authorId": 1,
                "date": "2026-03-19T14:25:00+03:00",
                "text": "Добрый день!",
                "isSystem": false,
                "uuid": "",
                "forward": null,
                "params": {},
                "viewedByOthers": true
            },
            {
                "id": 789,
                "chatId": 5,
                "authorId": 2,
                "date": "2026-03-19T14:30:00+03:00",
                "text": "Привет! Как дела?",
                "isSystem": false,
                "uuid": "",
                "forward": null,
                "params": {},
                "viewedByOthers": true
            }
        ],
        "users": [
            {
                "id": 1,
                "active": true,
                "name": "John Smith",
                "bot": false,
                "type": "employee"
            },
            {
                "id": 2,
                "active": true,
                "name": "Anna Davis",
                "bot": false,
                "type": "employee"
            }
        ],
        "hasPrevPage": false,
        "hasNextPage": true
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
|| **result.messages**
[`Message[]`](../../entities.md#message) | Массив сообщений от старых к новым [(подробное описание)](#message-object) ||
|| **result.users**
[`User[]`](../../entities.md#user) | Авторы сообщений [(подробное описание)](#user-object) ||
|| **result.hasPrevPage**
[`boolean`](../../../../data-types.md) | Есть ли более ранние сообщения ||
|| **result.hasNextPage**
[`boolean`](../../../../data-types.md) | Есть ли более поздние сообщения ||
|| **time**
[`time`](../../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

### Поля объекта Message {#message-object}

#|
|| **Поле**
`Тип` | **Описание** ||
|| **id**
[`integer`](../../../../data-types.md) | Идентификатор сообщения ||
|| **chatId**
[`integer`](../../../../data-types.md) | Идентификатор чата ||
|| **authorId**
[`integer`](../../../../data-types.md) | Идентификатор автора сообщения ||
|| **date**
[`string`](../../../../data-types.md) | Дата отправки сообщения ||
|| **text**
[`string`](../../../../data-types.md) | Текст сообщения ||
|| **isSystem**
[`boolean`](../../../../data-types.md) | Системное сообщение ||
|| **uuid**
[`string`](../../../../data-types.md) | Внешний идентификатор сообщения ||
|| **forward**
[`object`](../../../../data-types.md) | Данные о пересланном сообщении ||
|| **params**
[`object`](../../../../data-types.md) | Дополнительные параметры сообщения ||
|| **viewedByOthers**
[`boolean`](../../../../data-types.md) | Сообщение просмотрено другими участниками ||
|#

### Поля объекта User {#user-object}

#|
|| **Поле**
`Тип` | **Описание** ||
|| **id**
[`integer`](../../../../data-types.md) | Идентификатор пользователя ||
|| **active**
[`boolean`](../../../../data-types.md) | Пользователь активен ||
|| **name**
[`string`](../../../../data-types.md) | Имя и фамилия пользователя ||
|| **bot**
[`boolean`](../../../../data-types.md) | Признак пользователя-бота ||
|| **type**
[`string`](../../../../data-types.md) | Тип пользователя ||
|#

Полное описание всех полей объектов — на странице [Объекты и поля](../../entities.md)

### Пагинация

Для загрузки следующей страницы вызовите метод повторно, передав в `messageId` ID последнего сообщения из текущей выборки. Для предыдущей — ID первого сообщения.

## Обработка ошибок

HTTP-статус: **400**, **403**

```json
{
    "error": "BOT_TYPE_NOT_ALLOWED",
    "error_description": "Bot type not allowed"
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
|| `BOT_TYPE_NOT_ALLOWED` | Bot type not allowed | Метод доступен только для ботов типа `supervisor` и `personal` ||
|| `MESSAGE_NOT_FOUND` | Message not found | Сообщение не найдено ||
|| `MESSAGE_ACCESS_DENIED` | Message access denied | Бот не является участником чата с этим сообщением или не имеет доступа к истории ||
|#

{% include [Системные ошибки](../../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [Журнал изменений API imbot.v2](../../change-log.md)
- [{#T}](./chat-message-get.md)
- [{#T}](./chat-message-send.md)
- [{#T}](../../index.md#bot-types)
