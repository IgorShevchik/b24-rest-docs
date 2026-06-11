# Создать чат от лица чат-бота imbot.chat.add

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../scopes/permissions.md)
>
> Кто может выполнять метод: пользователь приложения, которое зарегистрировало чат-бота

{% note warning "DEPRECATED" %}

Развитие метода остановлено. Используйте [imbot.v2.Chat.add](../../chat-bots-v2/imbot.v2/chats/chat-add.md).

{% endnote %}

Метод `imbot.chat.add` создает чат от лица чат-бота.

## Параметры метода

{% include [Сноска об обязательных параметрах](../../../../_includes/required.md) %}

#|
|| **Название**
`тип` | **Описание** ||
|| **TYPE**
[`string`](../../../data-types.md) | Тип чата. Возможные значения:
- `OPEN` — открытый чат
- `CHAT` — закрытый чат

По умолчанию — `CHAT` ||
|| **TITLE**
[`string`](../../../data-types.md) | Заголовок чата ||
|| **DESCRIPTION**
[`string`](../../../data-types.md) | Описание чата ||
|| **COLOR**
[`string`](../../../data-types.md) | Цвет чата для мобильного приложения. Возможные значения:
- `RED` — красный
- `GREEN` — зеленый
- `MINT` — мятный
- `LIGHT_BLUE` — светло-синий
- `DARK_BLUE` — темно-синий
- `PURPLE` — фиолетовый
- `AQUA` — аквамариновый
- `PINK` — розовый
- `LIME` — лаймовый
- `BROWN` — коричневый
- `AZURE` — лазурный
- `KHAKI` — хаки
- `SAND` — песочный
- `MARENGO` — маренго
- `GRAY` — серый
- `GRAPHITE` — графитовый ||
|| **MESSAGE**
[`string`](../../../data-types.md) | Приветственное сообщение в чате ||
|| **USERS**
[`array`](../../../data-types.md) | Массив участников чата ||
|| **AVATAR**
[`string`](../../../data-types.md) | Аватар чата в формате [Base64](../../../files/how-to-upload-files.md).

Максимальный размер изображения — 5000х5000 ||
|| **ENTITY_TYPE**
[`string`](../../../data-types.md) | Тип объекта для привязки чата к внешнему контексту ||
|| **ENTITY_ID**
[`string`](../../../data-types.md) | Идентификатор объекта в рамках `ENTITY_TYPE`. 

При создании чата можно передать произвольную пару `ENTITY_TYPE` и `ENTITY_ID`. Параметры используются для получения идентификатора чата методом [imbot.chat.get](./imbot-chat-get.md) и для определения контекста в обработчиках событий [ONIMBOTMESSAGEADD](../messages/events/on-imbot-message-add.md), [ONIMBOTMESSAGEUPDATE](../messages/events/on-imbot-message-update.md), [ONIMBOTMESSAGEDELETE](../messages/events/on-imbot-message-delete.md) ||
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
    -d '{"TYPE":"CHAT","TITLE":"Новый чат","DESCRIPTION":"Важные новости","COLOR":"GREEN","MESSAGE":"Добро пожаловать!","USERS":[1271],"AVATAR":"/9j/4AAQSkZJRgABAQEBLAEsAAD/4QBwRXhp...+gKlSv+1v/2Q==","ENTITY_TYPE":"CHAT","ENTITY_ID":"13","BOT_ID":1291,"CLIENT_ID":"**put_your_client_id_here**"}' /
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.chat.add
    ```

- cURL (OAuth)

    ```bash
    curl -X POST /
    -H "Content-Type: application/json" /
    -H "Accept: application/json" /
    -d '{"TYPE":"CHAT","TITLE":"Новый чат","DESCRIPTION":"Важные новости","COLOR":"GREEN","MESSAGE":"Добро пожаловать!","USERS":[1271],"AVATAR":"/9j/4AAQSkZJRgABAQEBLAEsAAD/4QBwRXhp...+gKlSv+1v/2Q==","ENTITY_TYPE":"CHAT","ENTITY_ID":"13","BOT_ID":1291,"auth":"**put_access_token_here**"}' /
    https://**put_your_bitrix24_address**/rest/imbot.chat.add
    ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    try {
      const response = await $b24.actions.v2.call.make<number>({
        method: 'imbot.chat.add',
        params: {
          TYPE: 'CHAT',
          TITLE: 'New Chat',
          DESCRIPTION: 'Important News',
          COLOR: 'GREEN',
          MESSAGE: 'Welcome!',
          USERS: [1271],
          AVATAR: '/9j/4AAQSkZJRgABAQEBLAEsAAD/4QBwRXhp...+gKlSv+1v/2Q==',
          ENTITY_TYPE: 'CHAT',
          ENTITY_ID: '13',
          BOT_ID: 1291,
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Created chat with ID:', result)
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
      async function createChat() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.chat.add',
            params: {
              TYPE: 'CHAT',
              TITLE: 'New Chat',
              DESCRIPTION: 'Important News',
              COLOR: 'GREEN',
              MESSAGE: 'Welcome!',
              USERS: [1271],
              AVATAR: '/9j/4AAQSkZJRgABAQEBLAEsAAD/4QBwRXhp...+gKlSv+1v/2Q==',
              ENTITY_TYPE: 'CHAT',
              ENTITY_ID: '13',
              BOT_ID: 1291,
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('Created chat with ID:', result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', createChat)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.chat.add',
                [
                    'TYPE' => 'CHAT',
                    'TITLE' => 'Новый чат',
                    'DESCRIPTION' => 'Важные новости',
                    'COLOR' => 'GREEN',
                    'MESSAGE' => 'Добро пожаловать!',
                    'USERS' => [1271],
                    'AVATAR' => '/9j/4AAQSkZJRgABAQEBLAEsAAD/4QBwRXhp...+gKlSv+1v/2Q==',
                    'ENTITY_TYPE' => 'CHAT',
                    'ENTITY_ID' => '13',
                    'BOT_ID' => 1291
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        echo 'Success: ' . print_r($result, true);
        processData($result);

    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error adding chat: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.chat.add',
        {
            TYPE: 'CHAT',
            TITLE: 'Новый чат',
            DESCRIPTION: 'Важные новости',
            COLOR: 'GREEN',
            MESSAGE: 'Добро пожаловать!',
            USERS: [1271],
            AVATAR: '/9j/4AAQSkZJRgABAQEBLAEsAAD/4QBwRXhp...+gKlSv+1v/2Q==',
            ENTITY_TYPE: 'CHAT',
            ENTITY_ID: '13',
            BOT_ID: 1291
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
        'imbot.chat.add',
        [
            'TYPE' => 'CHAT',
            'TITLE' => 'Новый чат',
            'DESCRIPTION' => 'Важные новости',
            'COLOR' => 'GREEN',
            'MESSAGE' => 'Добро пожаловать!',
            'USERS' => [1271],
            'AVATAR' => '/9j/4AAQSkZJRgABAQEBLAEsAAD/4QBwRXhp...+gKlSv+1v/2Q==',
            'ENTITY_TYPE' => 'CHAT',
            'ENTITY_ID' => '13',
            'BOT_ID' => 1291
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
  "result": 2725,
  "time": {
      "start": 1771928379,
      "finish": 1771928380.102187,
      "duration": 1.102186918258667,
      "processing": 1,
      "date_start": "2026-02-24T13:19:39+03:00",
      "date_finish": "2026-02-24T13:19:40+03:00",
      "operating_reset_at": 1771928979,
      "operating": 0.3226499557495117
    }
}
```

### Возвращаемые данные

#|
|| **Название**
`тип` | **Описание** ||
|| **result**
[`integer`](../../../data-types.md) | Идентификатор созданного чата ||
|| **time**
[`time`](../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**

```json
{
    "error": "WRONG_REQUEST",
    "error_description": "Chat can't be created"
}
```

{% include notitle [обработка ошибок](../../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Описание** | **Значение** ||
|| `INVALID_FORMAT` | Parameter USERS has wrong type | Параметр `USERS` передан в неверном формате ||
|| `BOT_ID_ERROR` | Bot not found | Чат-бот не найден ||
|| `APP_ID_ERROR` | Bot was installed by another rest application | Указанный чат-бот установлен другим приложением ||
|| `WRONG_REQUEST` | Chat can't be created | Не удалось создать чат ||
|#

{% include [системные ошибки](../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [{#T}](./imbot-chat-user-add.md)
- [{#T}](./imbot-chat-set-manager.md)
- [{#T}](./imbot-chat-update-title.md)
- [{#T}](./imbot-chat-update-avatar.md)
- [{#T}](./imbot-chat-update-color.md)
- [{#T}](./imbot-chat-get.md)
- [{#T}](./imbot-dialog-get.md)
- [{#T}](./imbot-chat-user-list.md)
- [{#T}](./imbot-chat-user-delete.md)
- [{#T}](./imbot-chat-leave.md)




