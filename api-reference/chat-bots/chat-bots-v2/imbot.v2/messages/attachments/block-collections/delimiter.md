# Блок с разделителем DELIMITER

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

Блок `DELIMITER` добавляет визуальный разделитель между частями вложения.

![Блок с разделителем](./_images/delimiter.png){width=420}

## Параметры блока

#|
|| **Название**
`тип` | **Описание** ||
|| **SIZE**
[`integer`](../../../../../../data-types.md) | Ширина разделителя в пикселях. Если значение не задано или некорректно, используется `200` ||
|| **COLOR**
[`string`](../../../../../../data-types.md) | HEX-цвет разделителя (`#RGB` или `#RRGGBB`) ||
|#

## Пример

{% include [Сноска о примерах](../../../../../../../_includes/examples.md) %}

{% list tabs %}

- JS (TS)

    ```ts
    // This snippet is an ES module: top-level await requires type="module" or a bundler.
    // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
    import { Text } from '@bitrix24/b24jssdk'
    import type { B24Frame } from '@bitrix24/b24jssdk'

    declare const $b24: B24Frame

    try {
      const response = await $b24.actions.v2.call.make<{ id: number }>({
        method: 'imbot.v2.Chat.Message.send',
        params: {
          botId: 456,
          dialogId: 'chat20921',
          fields: {
            message: 'Task card with delimiter',
            attach: [
              {
                DELIMITER: {
                  SIZE: 200,
                  COLOR: '#c6c6c6',
                },
              },
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
              dialogId: 'chat20921',
              fields: {
                message: 'Task card with delimiter',
                attach: [
                  {
                    DELIMITER: {
                      SIZE: 200,
                      COLOR: '#c6c6c6',
                    },
                  },
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
    [
        'DELIMITER' => [
            'SIZE' => 200,
            'COLOR' => '#c6c6c6'
        ]
    ]
    ```

{% endlist %}

## Продолжите изучение

- [Журнал изменений API imbot.v2](../../../../change-log.md)
- [{#T}](./index.md)
- [{#T}](./text.md)
- [{#T}](./grid.md)
