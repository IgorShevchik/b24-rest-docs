# Как вызывать методы чат-бота и обновлять токен авторизации

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

Страница показывает базовый подход к вызову REST-методов чат-бота и поясняет, когда нужно обновлять OAuth-токен, а когда достаточно webhook-авторизации.

{% note info "" %}

Для новых интеграций используйте методы [`imbot.v2`](./chat-bots-v2/index.md)

{% endnote %}

## Базовый вызов метода

Ниже приведен типовой пример вызова метода [imbot.v2.Chat.Message.send](./chat-bots-v2/imbot.v2/messages/chat-message-send.md) в стандартных форматах, которые используются в документации.

{% include [Сноска о примерах](../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

  ```bash
  curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"botId":456,"botToken":"my_bot_token","dialogId":"chat5","fields":{"message":"Введите строку поиска"}}' \
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.v2.Chat.Message.send
  ```

- cURL (OAuth)

  ```bash
  curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"botId":456,"dialogId":"chat5","fields":{"message":"Введите строку поиска"},"auth":"**put_access_token_here**"}' \
    https://**put_your_bitrix24_address**/rest/imbot.v2.Chat.Message.send
  ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    // Shape of the payload returned in result (match the "response handling" section of the page)
    type SendMessageResult = {
      id: number
    }

    try {
      const response = await $b24.actions.v2.call.make<SendMessageResult>({
        method: 'imbot.v2.Chat.Message.send',
        params: {
          botId: 456,
          dialogId: 'chat5',
          fields: {
            message: 'Enter search string',
          },
        },
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('Created message ID:', result.id)
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
      async function sendMessage() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.v2.Chat.Message.send',
            params: {
              botId: 456,
              dialogId: 'chat5',
              fields: {
                message: 'Enter search string',
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
          console.info('Created message ID:', result.id)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', sendMessage)
    </script>
    ```

- PHP

  ```php
  try {
      $response = $b24Service
          ->core
          ->call(
              'imbot.v2.Chat.Message.send',
              [
                  'botId' => 456,
                  'dialogId' => 'chat5',
                  'fields' => [
                      'message' => 'Введите строку поиска',
                  ],
              ]
          );

      $result = $response
          ->getResponseData()
          ->getResult()['id'];

      echo 'Created message ID: ' . $result;
  } catch (Throwable $e) {
      error_log($e->getMessage());
      echo 'Error: ' . $e->getMessage();
  }
  ```

- BX24.js

  ```js
  BX24.callMethod(
      'imbot.v2.Chat.Message.send',
      {
          botId: 456,
          dialogId: 'chat5',
          fields: {
              message: 'Введите строку поиска',
          },
      },
      function(result) {
          if (result.error()) {
              console.error(result.error().ex);
          } else {
              console.log('Message ID:', result.data().id);
          }
      }
  );
  ```

- PHP CRest

  ```php
  require_once('crest.php');

  $result = CRest::call(
      'imbot.v2.Chat.Message.send',
      [
          'botId' => 456,
          'dialogId' => 'chat5',
          'fields' => [
              'message' => 'Введите строку поиска',
          ],
      ]
  );

  if (!empty($result['error'])) {
      echo 'Error: ' . $result['error_description'];
  } else {
      echo 'Message ID: ' . $result['result']['id'];
  }
  ```

{% endlist %}

{% note info "" %}

Если вы используете собственную PHP-обертку для REST, она может повторять логику стандартных примеров выше: формировать HTTP-запрос, передавать параметры метода и, при необходимости, добавлять OAuth-авторизацию.

{% endnote %}

## Сценарии вызова

Есть два основных сценария вызова методов:

1. Входящий вебхук
2. OAuth-авторизация

### Входящий вебхук

Если вы вызываете методы через входящий вебхук, обновлять OAuth-токен не нужно. Для методов `imbot.v2` в webhook-сценарии дополнительно передается `botToken`, который был задан при регистрации бота.

### OAuth

Если вы вызываете REST через OAuth, у запроса есть `access_token` и `refresh_token`. В этом случае токен доступа может истечь, и его нужно обновлять через `refresh_token`.

Для такого сценария полезна функция `restAuth`.

#### Функция `restAuth`

Используйте эту функцию только для OAuth-сценария.

```php
/**
 * Refresh OAuth token.
 *
 * @param array $auth OAuth authorization data
 *
 * @return bool|array
 */
function restAuth($auth)
{
    if (!CLIENT_ID || !CLIENT_SECRET)
    {
        return false;
    }

    if (
        !isset($auth['refresh_token'])
        || !isset($auth['scope'])
        || !isset($auth['domain'])
    )
    {
        return false;
    }

    $queryUrl = 'https://' . $auth['domain'] . '/oauth/token/';
    $queryData = http_build_query(
        [
            'grant_type' => 'refresh_token',
            'client_id' => CLIENT_ID,
            'client_secret' => CLIENT_SECRET,
            'refresh_token' => $auth['refresh_token'],
            'scope' => $auth['scope'],
        ]
    );

    $curl = curl_init();

    curl_setopt_array(
        $curl,
        [
            CURLOPT_HEADER => 0,
            CURLOPT_RETURNTRANSFER => 1,
            CURLOPT_URL => $queryUrl . '?' . $queryData,
        ]
    );

    $result = curl_exec($curl);
    curl_close($curl);

    return json_decode($result, true);
}
```

## Что учитывать для `imbot.v2`

- для webhook-вызовов методов бота передавайте `botToken`
- для OAuth-вызовов `botToken` не нужен, но нужен `auth`
- параметры большинства методов `imbot.v2` вложены в `fields.*`
- режим получения событий зависит от `eventMode` бота: `fetch` или `webhook`

## Продолжите изучение

- [{#T}](./chat-bots-v2/quick-start.md)
- [{#T}](./chat-bots-v2/imbot.v2/bots/bot-register.md)
- [{#T}](./chat-bots-v2/imbot.v2/messages/chat-message-send.md)
- [{#T}](./chat-bots-v2/imbot.v2/events/event-get.md)
- [{#T}](./outdated/send-command.md)

