# Обновить команду imbot.command.update

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../scopes/permissions.md)
>
> Кто может выполнять метод: пользователь приложения, которое зарегистрировало чат-бота

{% note warning "DEPRECATED" %}

Развитие метода остановлено. Используйте [imbot.v2.Command.update](../../chat-bots-v2/imbot.v2/commands/command-update.md).

{% endnote %}

Метод `imbot.command.update` обновляет параметры зарегистрированной команды чат-бота.

## Параметры метода

{% include [Сноска об обязательных параметрах](../../../../_includes/required.md) %}

#|
|| **Название**
`тип` | **Описание** ||
|| **COMMAND_ID***
[`integer`](../../../data-types.md) | Идентификатор команды для обновления ||
|| **FIELDS***
[`object`](../../../data-types.md) | Объект с полями для обновления. Структура описана [ниже](#fields) ||
|| **CLIENT_ID**
[`string`](../../../data-types.md) | Параметр обязателен только для вебхуков. Передавайте тот же CLIENT_ID, который был указан при регистрации чат-бота ||
|#

{% note warning "" %}

В `FIELDS` должен быть передан хотя бы один изменяемый параметр. Если передать пустой объект, метод вернет ошибку

{% endnote %}

### Параметр FIELDS {#fields}

#|
|| **Название**
`тип` | **Описание** ||
|| **COMMAND**
[`string`](../../../data-types.md) | Текст команды ||
|| **EVENT_COMMAND_ADD**
[`string`](../../../data-types.md) | URL обработчика события [ONIMCOMMANDADD](./events/on-im-command-add.md) ||
|| **HIDDEN**
[`string`](../../../data-types.md) | Видимость команды:
- `Y` - скрытая
- `N` - видимая ||
|| **EXTRANET_SUPPORT**
[`string`](../../../data-types.md) | Доступность для пользователей экстранета:
- `Y` - доступна
- `N` - недоступна ||
|| **LANG**
[`array`](../../../data-types.md) | Массив локализаций команды. Структура описана [ниже](#fields-lang) ||
|#

### Параметр FIELDS.LANG {#fields-lang}

#|
|| **Название**
`тип` | **Описание** ||
|| **LANGUAGE_ID***
[`string`](../../../data-types.md) | Идентификатор языка, например `ru` или `en` ||
|| **TITLE***
[`string`](../../../data-types.md) | Название команды на выбранном языке ||
|| **PARAMS**
[`string`](../../../data-types.md) | Подсказка по параметрам команды на выбранном языке ||
|#

## Примеры кода

{% include [Сноска о примерах](../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST /
    -H "Content-Type: application/json" /
    -H "Accept: application/json" /
    -d '{"COMMAND_ID":99,"FIELDS":{"COMMAND":"echo2","EVENT_COMMAND_ADD":"https://example.com/bot/command.php","HIDDEN":"N","EXTRANET_SUPPORT":"Y","LANG":[{"LANGUAGE_ID":"ru","TITLE":"Эхо 2","PARAMS":"текст"},{"LANGUAGE_ID":"en","TITLE":"Echo 2","PARAMS":"text"}]},"CLIENT_ID":"**put_your_client_id_here**"}' /
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.command.update
    ```

- cURL (OAuth)

    ```bash
    curl -X POST /
    -H "Content-Type: application/json" /
    -H "Accept: application/json" /
    -d '{"COMMAND_ID":99,"FIELDS":{"COMMAND":"echo2","EVENT_COMMAND_ADD":"https://example.com/bot/command.php","HIDDEN":"N","EXTRANET_SUPPORT":"Y","LANG":[{"LANGUAGE_ID":"ru","TITLE":"Эхо 2","PARAMS":"текст"},{"LANGUAGE_ID":"en","TITLE":"Echo 2","PARAMS":"text"}]},"auth":"**put_access_token_here**"}' /
    https://**put_your_bitrix24_address**/rest/imbot.command.update
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
        method: 'imbot.command.update',
        params: {
          COMMAND_ID: 99,
          FIELDS: {
            COMMAND: 'echo2',
            EVENT_COMMAND_ADD: 'https://example.com/bot/command.php',
            HIDDEN: 'N',
            EXTRANET_SUPPORT: 'Y',
            LANG: [
              { LANGUAGE_ID: 'ru', TITLE: 'Echo 2', PARAMS: 'text' },
              { LANGUAGE_ID: 'en', TITLE: 'Echo 2', PARAMS: 'text' },
            ],
          },
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Command updated successfully:', result)
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
      async function updateCommand() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.command.update',
            params: {
              COMMAND_ID: 99,
              FIELDS: {
                COMMAND: 'echo2',
                EVENT_COMMAND_ADD: 'https://example.com/bot/command.php',
                HIDDEN: 'N',
                EXTRANET_SUPPORT: 'Y',
                LANG: [
                  { LANGUAGE_ID: 'ru', TITLE: 'Echo 2', PARAMS: 'text' },
                  { LANGUAGE_ID: 'en', TITLE: 'Echo 2', PARAMS: 'text' },
                ],
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
          console.info('Command updated successfully:', result)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', updateCommand)
    </script>
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.command.update',
                [
                    'COMMAND_ID' => 99,
                    'FIELDS' => [
                        'COMMAND' => 'echo2',
                        'EVENT_COMMAND_ADD' => 'https://example.com/bot/command.php',
                        'HIDDEN' => 'N',
                        'EXTRANET_SUPPORT' => 'Y',
                        'LANG' => [
                            ['LANGUAGE_ID' => 'ru', 'TITLE' => 'Эхо 2', 'PARAMS' => 'текст'],
                            ['LANGUAGE_ID' => 'en', 'TITLE' => 'Echo 2', 'PARAMS' => 'text']
                        ]
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
        echo 'Error updating command: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.command.update',
        {
            COMMAND_ID: 99,
            FIELDS: {
                COMMAND: 'echo2',
                EVENT_COMMAND_ADD: 'https://example.com/bot/command.php',
                HIDDEN: 'N',
                EXTRANET_SUPPORT: 'Y',
                LANG: [
                    { LANGUAGE_ID: 'ru', TITLE: 'Эхо 2', PARAMS: 'текст' },
                    { LANGUAGE_ID: 'en', TITLE: 'Echo 2', PARAMS: 'text' }
                ]
            }
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
        'imbot.command.update',
        [
            'COMMAND_ID' => 99,
            'FIELDS' => [
                'COMMAND' => 'echo2',
                'EVENT_COMMAND_ADD' => 'https://example.com/bot/command.php',
                'HIDDEN' => 'N',
                'EXTRANET_SUPPORT' => 'Y',
                'LANG' => [
                    ['LANGUAGE_ID' => 'ru', 'TITLE' => 'Эхо 2', 'PARAMS' => 'текст'],
                    ['LANGUAGE_ID' => 'en', 'TITLE' => 'Echo 2', 'PARAMS' => 'text']
                ]
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
    "result": true,
    "time": {
        "start": 1772103002,
        "finish": 1772103003.109342,
        "duration": 1.109342098236084,
        "processing": 0,
        "date_start": "2026-02-26T13:50:02+03:00",
        "date_finish": "2026-02-26T13:50:03+03:00",
        "operating_reset_at": 1772103603,
        "operating": 0
    }
}
```

### Возвращаемые данные

#|
|| **Название**
`тип` | **Описание** ||
|| **result**
[`boolean`](../../../data-types.md) | `true`, если команда успешно обновлена ||
|| **time**
[`time`](../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

## Обработка ошибок

HTTP-статус: **400**

```json
{
    "error": "WRONG_REQUEST",
    "error_description": "Update fields can't be empty"
}
```

{% include notitle [обработка ошибок](../../../../_includes/error-info.md) %}

### Возможные коды ошибок

#|
|| **Код** | **Описание** | **Значение** ||
|| `COMMAND_ID_ERROR` | Command not found | Команда не найдена ||
|| `APP_ID_ERROR` | Command was installed by another rest application | Команда зарегистрирована другим приложением ||
|| `EVENT_COMMAND_ADD_ERROR` | Wrong handler URL | Невалидный URL обработчика события команды ||
|| `WRONG_REQUEST` | Update fields can't be empty | Не переданы поля для обновления ||
|| `WRONG_REQUEST` | Command can't be updated | Не удалось обновить команду ||
|#

{% include [системные ошибки](../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [{#T}](./imbot-command-register.md)
- [{#T}](./imbot-command-answer.md)
- [{#T}](./imbot-command-unregister.md)
- [{#T}](./events/on-im-command-add.md)




