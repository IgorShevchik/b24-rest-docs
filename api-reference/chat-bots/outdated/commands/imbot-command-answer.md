# Отправить ответ на команду imbot.command.answer

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../scopes/permissions.md)
>
> Кто может выполнять метод: пользователь приложения, которое зарегистрировало чат-бота

{% note warning "DEPRECATED" %}

Развитие метода остановлено. Используйте [imbot.v2.Command.answer](../../chat-bots-v2/imbot.v2/commands/command-answer.md).

{% endnote %}

Метод `imbot.command.answer` публикует ответ на команду чат-бота.

## Параметры метода

{% include [Сноска об обязательных параметрах](../../../../_includes/required.md) %}

#|
|| **Название**
`тип` | **Описание** ||
|| **COMMAND_ID***
[`integer`](../../../data-types.md) | Идентификатор команды. Обязателен, если не передан `COMMAND` ||
|| **COMMAND***
[`string`](../../../data-types.md) | Текст команды. Обязателен, если не передан `COMMAND_ID` ||
|| **MESSAGE_ID***
[`integer`](../../../data-types.md) | Идентификатор сообщения, на которое отправляется ответ.

Идентификатор можно узнать из входящего события [ONIMCOMMANDADD](./events/on-im-command-add.md) ||
|| **MESSAGE***
[`string`](../../../data-types.md) | Текст ответа ||
|| **ATTACH**
[`object`](../../../data-types.md) | Объект с вложением к сообщению. Минимальный формат: 

```json
{
  "BLOCKS": [
    { "MESSAGE": "Текст блока" }
  ]
}
```

[Подробное описание](../../../chats/messages/attachments.md)||
|| **KEYBOARD**
[`object`](../../../data-types.md) | Клавиатура сообщения. Минимальный формат:

```json
{
  "BUTTONS": [
    { "TEXT": "Повторить", "COMMAND": "echo repeat" }
  ]
}
```

[Подробное описание](../../../chats/messages/keyboards.md) ||
|| **MENU**
[`object`](../../../data-types.md) | Контекстное меню сообщения. Минимальный формат:

```json
[
  { "TEXT": "bitrix24", "LINK": "https://bitrix24.ru" }
]
```

[Подробное описание](../../../chats/messages/menu.md) ||
|| **SYSTEM**
[`string`](../../../data-types.md) | Тип сообщения:
- `Y` - системное сообщение
- `N` - обычное сообщение

По умолчанию - `N` ||
|| **URL_PREVIEW**
[`string`](../../../data-types.md) | Преобразование ссылок в rich-ссылки:
- `Y` - включено
- `N` - выключено

По умолчанию - `Y`.

Работает для ссылок, переданных в поле `MESSAGE` ||
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
    -d '{"COMMAND_ID":99,"MESSAGE_ID":33871,"MESSAGE":"Принято. Выполняю команду.","SYSTEM":"N","URL_PREVIEW":"Y","ATTACH":{"BLOCKS":[{"MESSAGE":"Детали задачи"},{"DELIMITER":true},{"LINK":{"NAME":"Открыть","LINK":"https://example.com"}}]},"KEYBOARD":{"BUTTONS":[{"TEXT":"Повторить","COMMAND":"echo repeat"}]},"MENU":[{"TEXT":"bitrix24","LINK":"https://bitrix24.ru"}],"CLIENT_ID":"**put_your_client_id_here**"}' /
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.command.answer
    ```

- cURL (OAuth)

    ```bash
    curl -X POST /
    -H "Content-Type: application/json" /
    -H "Accept: application/json" /
    -d '{"COMMAND_ID":99,"MESSAGE_ID":33871,"MESSAGE":"Принято. Выполняю команду.","SYSTEM":"N","URL_PREVIEW":"Y","ATTACH":{"BLOCKS":[{"MESSAGE":"Детали задачи"},{"DELIMITER":true},{"LINK":{"NAME":"Открыть","LINK":"https://example.com"}}]},"KEYBOARD":{"BUTTONS":[{"TEXT":"Повторить","COMMAND":"echo repeat"}]},"MENU":[{"TEXT":"bitrix24","LINK":"https://bitrix24.ru"}],"auth":"**put_access_token_here**"}' /
    https://**put_your_bitrix24_address**/rest/imbot.command.answer
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
        method: 'imbot.command.answer',
        params: {
          COMMAND_ID: 99,
          MESSAGE_ID: 33871,
          MESSAGE: 'Accepted. Executing command.',
          SYSTEM: 'N',
          URL_PREVIEW: 'Y',
          ATTACH: {
            BLOCKS: [
              { MESSAGE: 'Task details' },
              { DELIMITER: true },
              { LINK: { NAME: 'Open', LINK: 'https://example.com' } },
            ],
          },
          KEYBOARD: {
            BUTTONS: [
              { TEXT: 'Repeat', COMMAND: 'echo repeat' },
            ],
          },
          MENU: [
            { TEXT: 'bitrix24', LINK: 'https://bitrix24.ru' },
          ],
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Sent message ID:', result)
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
      async function answerCommand() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.command.answer',
            params: {
              COMMAND_ID: 99,
              MESSAGE_ID: 33871,
              MESSAGE: 'Accepted. Executing command.',
              SYSTEM: 'N',
              URL_PREVIEW: 'Y',
              ATTACH: {
                BLOCKS: [
                  { MESSAGE: 'Task details' },
                  { DELIMITER: true },
                  { LINK: { NAME: 'Open', LINK: 'https://example.com' } },
                ],
              },
              KEYBOARD: {
                BUTTONS: [
                  { TEXT: 'Repeat', COMMAND: 'echo repeat' },
                ],
              },
              MENU: [
                { TEXT: 'bitrix24', LINK: 'https://bitrix24.ru' },
              ],
            },
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('Sent message ID:', result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', answerCommand)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.command.answer',
                [
                    'COMMAND_ID' => 99,
                    'MESSAGE_ID' => 33871,
                    'MESSAGE' => 'Принято. Выполняю команду.',
                    'SYSTEM' => 'N',
                    'URL_PREVIEW' => 'Y',
                    'ATTACH' => [
                        'BLOCKS' => [
                            ['MESSAGE' => 'Детали задачи'],
                            ['DELIMITER' => true],
                            ['LINK' => ['NAME' => 'Открыть', 'LINK' => 'https://example.com']]
                        ]
                    ],
                    'KEYBOARD' => [
                        'BUTTONS' => [
                            ['TEXT' => 'Повторить', 'COMMAND' => 'echo repeat']
                        ]
                    ],
                    'MENU' => [
                        ['TEXT' => 'bitrix24', 'LINK' => 'https://bitrix24.ru']
                    ]
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        echo 'Success: ' . print_r($result, true);
        processData($result);

    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error answering command: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.command.answer',
        {
            COMMAND_ID: 99,
            MESSAGE_ID: 33871,
            MESSAGE: 'Принято. Выполняю команду.',
            SYSTEM: 'N',
            URL_PREVIEW: 'Y',
            ATTACH: {
                BLOCKS: [
                    {MESSAGE: 'Детали задачи'},
                    {DELIMITER: true},
                    {LINK: {NAME: 'Открыть', LINK: 'https://example.com'}}
                ]
            },
            KEYBOARD: {
                BUTTONS: [
                    {TEXT: 'Повторить', COMMAND: 'echo repeat'}
                ]
            },
            MENU: [
                    {TEXT: 'bitrix24', LINK: 'https://bitrix24.ru'}
            ]
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
        'imbot.command.answer',
        [
            'COMMAND_ID' => 99,
            'MESSAGE_ID' => 33871,
            'MESSAGE' => 'Принято. Выполняю команду.',
            'SYSTEM' => 'N',
            'URL_PREVIEW' => 'Y',
            'ATTACH' => [
                'BLOCKS' => [
                    ['MESSAGE' => 'Детали задачи'],
                    ['DELIMITER' => true],
                    ['LINK' => ['NAME' => 'Открыть', 'LINK' => 'https://example.com']]
                ]
            ],
            'KEYBOARD' => [
                'BUTTONS' => [
                    ['TEXT' => 'Повторить', 'COMMAND' => 'echo repeat']
                ]
            ],
            'MENU' => [
                ['TEXT' => 'bitrix24', 'LINK' => 'https://bitrix24.ru']
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
    "result": 33879,
    "time": {
        "start": 1772102358,
        "finish": 1772102359.061859,
        "duration": 1.061858892440796,
        "processing": 1,
        "date_start": "2026-02-26T13:39:18+03:00",
        "date_finish": "2026-02-26T13:39:19+03:00",
        "operating_reset_at": 1772102958,
        "operating": 0
    }
}
```

### Возвращаемые данные

#|
|| **Название**
`тип` | **Описание** ||
|| **result**
[`integer`](../../../data-types.md) | Идентификатор отправленного сообщения-ответа ||
|| **time**
[`time`](../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**

```json
{
    "error": "MESSAGE_EMPTY",
    "error_description": "Message can't be empty"
}
```

{% include notitle [обработка ошибок](../../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Описание** | **Значение** ||
|| `COMMAND_ID_ERROR` | Command not found | Команда не найдена ||
|| `APP_ID_ERROR` | Command was installed by another rest application | Команда зарегистрирована другим приложением ||
|| `MESSAGE_ID_EMPTY` | Message ID can't be empty | Не передан `MESSAGE_ID` ||
|| `MESSAGE_EMPTY` | Message can't be empty | Не передан текст сообщения ||
|| `ATTACH_ERROR` | Incorrect attach params | Невалидный объект `ATTACH` ||
|| `ATTACH_OVERSIZE` | You have exceeded the maximum allowable size of attach | Размер `ATTACH` превышает допустимый ||
|| `KEYBOARD_ERROR` | Incorrect keyboard params | Невалидный объект `KEYBOARD` ||
|| `KEYBOARD_OVERSIZE` | You have exceeded the maximum allowable size of keyboard | Размер `KEYBOARD` превышает допустимый ||
|| `MENU_ERROR` | Incorrect menu params | Невалидный объект `MENU` ||
|| `WRONG_REQUEST` | Message isn't added | Не удалось отправить сообщение ||
|#

{% include [системные ошибки](../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [{#T}](./imbot-command-register.md)
- [{#T}](./imbot-command-update.md)
- [{#T}](./imbot-command-unregister.md)
- [{#T}](./events/on-im-command-add.md)
- [{#T}](../../../chats/messages/keyboards.md)
- [{#T}](../../../chats/messages/attachments.md)
- [{#T}](../../../chats/messages/menu.md)





