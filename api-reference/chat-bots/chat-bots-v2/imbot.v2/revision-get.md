# Получить ревизии API imbot.v2.Revision.get

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

> Scope: [`imbot`](../../../scopes/permissions.md)
>
> Кто может выполнять метод: любой пользователь

Метод `imbot.v2.Revision.get` возвращает номера ревизий REST API и клиентских протоколов мессенджера. Используется для проверки совместимости: какие методы и возможности поддерживает конкретный Битрикс24.

## Зачем нужен метод

Облако и коробочные версии Битрикс24 могут иметь разные ревизии API. Облачные Битрикс24 обновляются автоматически, а коробочные установки могут отставать по возможностям.

Вызывая `imbot.v2.Revision.get` перед использованием новых методов или полей, приложение может:

- определить, какие возможности доступны на текущем Битрикс24
- адаптировать логику бота под ревизию API
- корректно обрабатывать сценарии, когда нужный функционал еще не доступен у клиента

В документации по методам может встречаться пометка **«доступно с ревизии N»**. Это означает, что поле или поведение появилось только начиная с указанной ревизии.

## Параметры метода

Метод не требует `botId` и `botToken`. Параметров нет.

## Как использовать

Типичный сценарий — проверка перед использованием метода или поля, которое появилось в определенной ревизии:

```js
const revision = await BX.rest.callMethod('imbot.v2.Revision.get', {});
const restRevision = revision.data().rest;

if (restRevision >= 33)
{
    await BX.rest.callMethod('imbot.v2.Chat.Message.send', {
        botId: 456,
        botToken: '...',
        dialogId: 'chat5',
        fields: { message: 'Hello', system: true }
    });
}
else
{
    // system может не работать корректно в более ранней ревизии
}
```

## Примеры кода

{% include [Сноска о примерах](../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

  ```bash
  curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.v2.Revision.get
  ```

- cURL (OAuth)

  ```bash
  curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"auth":"**put_access_token_here**"}' \
    https://**put_your_bitrix24_address**/rest/imbot.v2.Revision.get
  ```

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    // Shape of the payload returned in result (match the "response handling" section of the page)
    type RevisionResult = {
      rest: number
      web: number
      mobile: number
      desktop: number
    }

    try {
      const response = await $b24.actions.v2.call.make<RevisionResult>({
        method: 'imbot.v2.Revision.get',
        params: {},
        requestId: Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
      } else {
        const result = response.getData()!.result
        console.info('rest:', result.rest, 'web:', result.web, 'mobile:', result.mobile, 'desktop:', result.desktop)
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
      async function getRevision() {
        try {
          // Initialize the SDK inside a Bitrix24 frame
          const $b24 = await B24Js.initializeB24Frame()

          const response = await $b24.actions.v2.call.make({
            method: 'imbot.v2.Revision.get',
            params: {},
            requestId: B24Js.Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
            return
          }

          const result = response.getData().result
          console.info('rest:', result.rest, 'web:', result.web, 'mobile:', result.mobile, 'desktop:', result.desktop)
        } catch (error) {
          // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
          console.error(error)
        }
      }

      document.addEventListener('DOMContentLoaded', getRevision)
    </script>
    ```

- PHP

  ```php
  $result = $b24Service->core->call('imbot.v2.Revision.get');
  print_r($result->getResponseData()->getResult());
  ```

- BX24.js

  ```js
  BX24.callMethod('imbot.v2.Revision.get', {}, function(result) {
      if (result.error()) {
          console.error(result.error().ex);
      } else {
          console.log(result.data());
      }
  });
  ```

- PHP CRest

  ```php
  $result = CRest::call('imbot.v2.Revision.get');
  print_r($result['result']);
  ```

{% endlist %}

## Обработка ответа

HTTP-статус: **200**

```json
{
  "result": {
    "rest": 33,
    "web": 130,
    "mobile": 23,
    "desktop": 6
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
[object](../../../data-types.md) | Номера ревизий API и клиентских протоколов [(подробное описание)](#revision-object) ||
|| **time**
[time](../../../data-types.md#time) | Информация о времени выполнения запроса ||
|#

### Поля объекта Revision {#revision-object}

#|
|| **Поле**
`Тип` | **Описание** ||
|| **rest**
[`integer`](../../../data-types.md) | Ревизия серверного REST API. Основной ключ для проверки совместимости методов и полей ||
|| **web**
[`integer`](../../../data-types.md) | Ревизия протокола веб-клиента мессенджера ||
|| **mobile**
[`integer`](../../../data-types.md) | Ревизия протокола мобильного клиента ||
|| **desktop**
[`integer`](../../../data-types.md) | Ревизия протокола десктоп-приложения ||
|#

## Обработка ошибок

Метод не возвращает ошибок вызова. Возможны только стандартные ошибки авторизации REST API.

{% include notitle [Обработка ошибок](../../../../_includes/error-info.md) %}

{% include [Системные ошибки](../../../../_includes/system-errors.md) %}

## Продолжите изучение

- [{#T}](../index.md)
- [{#T}](../change-log.md)
- [{#T}](./bots/bot-register.md)
