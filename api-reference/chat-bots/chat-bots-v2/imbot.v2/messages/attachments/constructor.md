# Конструктор вложений ATTACH

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../../../../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../../../../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

Страница содержит практические примеры сборки `ATTACH` из разных типов блоков. Итоговое вложение зависит от набора и порядка блоков.

## Пример 1. Карточка «Баг-трекер»

Системное сообщение с карточкой задачи, ссылкой и таблицами с параметрами.

{% include [Сноска о примерах](../../../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"botToken":"my_bot_token","dialogId":"chat20921","fields":{"message":"Карточка задачи","attach":[{"USER":{"NAME":"Уведомления Mantis","AVATAR":"https://files.shelenkov.com/bitrix/images/mantis2.jpg","LINK":"https://shelenkov.com/"}},{"LINK":{"NAME":"Открыть Mantis из внешней сети","LINK":"https://shelenkov.com/"}},{"DELIMITER":{"SIZE":200,"COLOR":"#c6c6c6"}},{"GRID":[{"NAME":"Проект","VALUE":"BUGS","DISPLAY":"LINE","WIDTH":100},{"NAME":"Категория","VALUE":"im","DISPLAY":"LINE","WIDTH":100},{"NAME":"Сводка","VALUE":"Требуется реализовать возможность добавлять структурированные сущности в сообщения и уведомления мессенджера.","DISPLAY":"BLOCK"}]},{"DELIMITER":{"SIZE":200,"COLOR":"#c6c6c6"}},{"GRID":[{"NAME":"Новое обращение","VALUE":"","DISPLAY":"ROW","WIDTH":100},{"NAME":"Назначено","VALUE":"Шеленков Евгений","DISPLAY":"ROW","WIDTH":100},{"NAME":"Дедлайн","VALUE":"04.11.2015 17:50:43","DISPLAY":"ROW","WIDTH":100}]}]}}' \
      https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.v2.Chat.Message.send
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"dialogId":"chat20921","fields":{"message":"Карточка задачи","attach":[{"USER":{"NAME":"Уведомления Mantis","AVATAR":"https://files.shelenkov.com/bitrix/images/mantis2.jpg","LINK":"https://shelenkov.com/"}},{"LINK":{"NAME":"Открыть Mantis из внешней сети","LINK":"https://shelenkov.com/"}},{"DELIMITER":{"SIZE":200,"COLOR":"#c6c6c6"}},{"GRID":[{"NAME":"Проект","VALUE":"BUGS","DISPLAY":"LINE","WIDTH":100},{"NAME":"Категория","VALUE":"im","DISPLAY":"LINE","WIDTH":100},{"NAME":"Сводка","VALUE":"Требуется реализовать возможность добавлять структурированные сущности в сообщения и уведомления мессенджера.","DISPLAY":"BLOCK"}]},{"DELIMITER":{"SIZE":200,"COLOR":"#c6c6c6"}},{"GRID":[{"NAME":"Новое обращение","VALUE":"","DISPLAY":"ROW","WIDTH":100},{"NAME":"Назначено","VALUE":"Шеленков Евгений","DISPLAY":"ROW","WIDTH":100},{"NAME":"Дедлайн","VALUE":"04.11.2015 17:50:43","DISPLAY":"ROW","WIDTH":100}]}]},"auth":"**put_access_token_here**"}' \
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
      id: number,
    }

    try {
      const response = await $b24.actions.v2.call.make<SendMessageResult>({
        method: 'imbot.v2.Chat.Message.send',
        params: {
          botId: 456,
          dialogId: 'chat20921',
          fields: {
            message: 'Task card',
            attach: [
              {
                USER: {
                  NAME: 'Mantis Notifications',
                  AVATAR: 'https://files.shelenkov.com/bitrix/images/mantis2.jpg',
                  LINK: 'https://shelenkov.com/',
                },
              },
              {
                LINK: {
                  NAME: 'Open Mantis from external network',
                  LINK: 'https://shelenkov.com/',
                },
              },
              {
                DELIMITER: {
                  SIZE: 200,
                  COLOR: '#c6c6c6',
                },
              },
              {
                GRID: [
                  {
                    NAME: 'Project',
                    VALUE: 'BUGS',
                    DISPLAY: 'LINE',
                    WIDTH: 100,
                  },
                  {
                    NAME: 'Category',
                    VALUE: 'im',
                    DISPLAY: 'LINE',
                    WIDTH: 100,
                  },
                  {
                    NAME: 'Summary',
                    VALUE: 'Need to implement adding structured entities to messages and notifications in the messenger.',
                    DISPLAY: 'BLOCK',
                  },
                ],
              },
              {
                DELIMITER: {
                  SIZE: 200,
                  COLOR: '#c6c6c6',
                },
              },
              {
                GRID: [
                  {
                    NAME: 'New issue',
                    VALUE: '',
                    DISPLAY: 'ROW',
                    WIDTH: 100,
                  },
                  {
                    NAME: 'Assigned',
                    VALUE: 'Evgeny Shelenkov',
                    DISPLAY: 'ROW',
                    WIDTH: 100,
                  },
                  {
                    NAME: 'Deadline',
                    VALUE: '04.11.2015 17:50:43',
                    DISPLAY: 'ROW',
                    WIDTH: 100,
                  },
                ],
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
                message: 'Task card',
                attach: [
                  {
                    USER: {
                      NAME: 'Mantis Notifications',
                      AVATAR: 'https://files.shelenkov.com/bitrix/images/mantis2.jpg',
                      LINK: 'https://shelenkov.com/',
                    },
                  },
                  {
                    LINK: {
                      NAME: 'Open Mantis from external network',
                      LINK: 'https://shelenkov.com/',
                    },
                  },
                  {
                    DELIMITER: {
                      SIZE: 200,
                      COLOR: '#c6c6c6',
                    },
                  },
                  {
                    GRID: [
                      {
                        NAME: 'Project',
                        VALUE: 'BUGS',
                        DISPLAY: 'LINE',
                        WIDTH: 100,
                      },
                      {
                        NAME: 'Category',
                        VALUE: 'im',
                        DISPLAY: 'LINE',
                        WIDTH: 100,
                      },
                      {
                        NAME: 'Summary',
                        VALUE: 'Need to implement adding structured entities to messages and notifications in the messenger.',
                        DISPLAY: 'BLOCK',
                      },
                    ],
                  },
                  {
                    DELIMITER: {
                      SIZE: 200,
                      COLOR: '#c6c6c6',
                    },
                  },
                  {
                    GRID: [
                      {
                        NAME: 'New issue',
                        VALUE: '',
                        DISPLAY: 'ROW',
                        WIDTH: 100,
                      },
                      {
                        NAME: 'Assigned',
                        VALUE: 'Evgeny Shelenkov',
                        DISPLAY: 'ROW',
                        WIDTH: 100,
                      },
                      {
                        NAME: 'Deadline',
                        VALUE: '04.11.2015 17:50:43',
                        DISPLAY: 'ROW',
                        WIDTH: 100,
                      },
                    ],
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
    try {
        $response = $b24Service
            ->core
            ->call(
                'imbot.v2.Chat.Message.send',
                [
                    'botId' => 456,
                    'dialogId' => 'chat20921',
                    'fields' => [
                        'message' => 'Карточка задачи',
                        'attach' => [
                        [
                            'USER' => [
                                'NAME' => 'Уведомления Mantis',
                                'AVATAR' => 'https://files.shelenkov.com/bitrix/images/mantis2.jpg',
                                'LINK' => 'https://shelenkov.com/'
                            ]
                        ],
                        [
                            'LINK' => [
                                'NAME' => 'Открыть Mantis из внешней сети',
                                'LINK' => 'https://shelenkov.com/'
                            ]
                        ],
                        [
                            'DELIMITER' => [
                                'SIZE' => 200,
                                'COLOR' => '#c6c6c6'
                            ]
                        ],
                        [
                            'GRID' => [
                                [
                                    'NAME' => 'Проект',
                                    'VALUE' => 'BUGS',
                                    'DISPLAY' => 'LINE',
                                    'WIDTH' => 100
                                ],
                                [
                                    'NAME' => 'Категория',
                                    'VALUE' => 'im',
                                    'DISPLAY' => 'LINE',
                                    'WIDTH' => 100
                                ],
                                [
                                    'NAME' => 'Сводка',
                                    'VALUE' => 'Требуется реализовать возможность добавлять структурированные сущности в сообщения и уведомления мессенджера.',
                                    'DISPLAY' => 'BLOCK'
                                ]
                            ]
                        ],
                        [
                            'DELIMITER' => [
                                'SIZE' => 200,
                                'COLOR' => '#c6c6c6'
                            ]
                        ],
                        [
                            'GRID' => [
                                [
                                    'NAME' => 'Новое обращение',
                                    'VALUE' => '',
                                    'DISPLAY' => 'ROW',
                                    'WIDTH' => 100
                                ],
                                [
                                    'NAME' => 'Назначено',
                                    'VALUE' => 'Шеленков Евгений',
                                    'DISPLAY' => 'ROW',
                                    'WIDTH' => 100
                                ],
                                [
                                    'NAME' => 'Дедлайн',
                                    'VALUE' => '04.11.2015 17:50:43',
                                    'DISPLAY' => 'ROW',
                                    'WIDTH' => 100
                                ]
                            ]
                        ]
                        ]
                    ]
                ]
            );

        $result = $response->getResponseData()->getResult()['id'];
        echo 'Created message ID: ' . $result;
    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error adding message: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.v2.Chat.Message.send',
        {
            botId: 456,
            dialogId: 'chat20921',
            fields: {
                message: 'Карточка задачи',
                attach: [
                {
                    USER: {
                        NAME: 'Уведомления Mantis',
                        AVATAR: 'https://files.shelenkov.com/bitrix/images/mantis2.jpg',
                        LINK: 'https://shelenkov.com/'
                    }
                },
                {
                    LINK: {
                        NAME: 'Открыть Mantis из внешней сети',
                        LINK: 'https://shelenkov.com/'
                    }
                },
                {
                    DELIMITER: {
                        SIZE: 200,
                        COLOR: '#c6c6c6'
                    }
                },
                {
                    GRID: [
                        {
                            NAME: 'Проект',
                            VALUE: 'BUGS',
                            DISPLAY: 'LINE',
                            WIDTH: 100
                        },
                        {
                            NAME: 'Категория',
                            VALUE: 'im',
                            DISPLAY: 'LINE',
                            WIDTH: 100
                        },
                        {
                            NAME: 'Сводка',
                            VALUE: 'Требуется реализовать возможность добавлять структурированные сущности в сообщения и уведомления мессенджера.',
                            DISPLAY: 'BLOCK'
                        }
                    ]
                },
                {
                    DELIMITER: {
                        SIZE: 200,
                        COLOR: '#c6c6c6'
                    }
                },
                {
                    GRID: [
                        {
                            NAME: 'Новое обращение',
                            VALUE: '',
                            DISPLAY: 'ROW',
                            WIDTH: 100
                        },
                        {
                            NAME: 'Назначено',
                            VALUE: 'Шеленков Евгений',
                            DISPLAY: 'ROW',
                            WIDTH: 100
                        },
                        {
                            NAME: 'Дедлайн',
                            VALUE: '04.11.2015 17:50:43',
                            DISPLAY: 'ROW',
                            WIDTH: 100
                        }
                    ]
                }
                ]
            }
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
            'dialogId' => 'chat20921',
            'fields' => [
                'message' => 'Карточка задачи',
                'attach' => [
                [
                    'USER' => [
                        'NAME' => 'Уведомления Mantis',
                        'AVATAR' => 'https://files.shelenkov.com/bitrix/images/mantis2.jpg',
                        'LINK' => 'https://shelenkov.com/'
                    ]
                ],
                [
                    'LINK' => [
                        'NAME' => 'Открыть Mantis из внешней сети',
                        'LINK' => 'https://shelenkov.com/'
                    ]
                ],
                [
                    'DELIMITER' => [
                        'SIZE' => 200,
                        'COLOR' => '#c6c6c6'
                    ]
                ],
                [
                    'GRID' => [
                        [
                            'NAME' => 'Проект',
                            'VALUE' => 'BUGS',
                            'DISPLAY' => 'LINE',
                            'WIDTH' => 100
                        ],
                        [
                            'NAME' => 'Категория',
                            'VALUE' => 'im',
                            'DISPLAY' => 'LINE',
                            'WIDTH' => 100
                        ],
                        [
                            'NAME' => 'Сводка',
                            'VALUE' => 'Требуется реализовать возможность добавлять структурированные сущности в сообщения и уведомления мессенджера.',
                            'DISPLAY' => 'BLOCK'
                        ]
                    ]
                ],
                [
                    'DELIMITER' => [
                        'SIZE' => 200,
                        'COLOR' => '#c6c6c6'
                    ]
                ],
                [
                    'GRID' => [
                        [
                            'NAME' => 'Новое обращение',
                            'VALUE' => '',
                            'DISPLAY' => 'ROW',
                            'WIDTH' => 100
                        ],
                        [
                            'NAME' => 'Назначено',
                            'VALUE' => 'Шеленков Евгений',
                            'DISPLAY' => 'ROW',
                            'WIDTH' => 100
                        ],
                        [
                            'NAME' => 'Дедлайн',
                            'VALUE' => '04.11.2015 17:50:43',
                            'DISPLAY' => 'ROW',
                            'WIDTH' => 100
                        ]
                    ]
                ]
                ]
            ]
        ]
    );

    if (!empty($result['error'])) {
        echo 'Error: ' . $result['error_description'];
    } else {
        echo 'Message ID: ' . $result['result']['id'];
    }
    ```

{% endlist %}

## Пример 2. Информационное уведомление

Короткий информационный текст и изображение в составе одного вложения.

{% include [Сноска о примерах](../../../../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"botToken":"my_bot_token","dialogId":"chat20921","fields":{"message":"У вас новое уведомление","attach":{"ID":1,"COLOR":"#29619b","BLOCKS":[{"MESSAGE":"Коллеги, обновление im 16.0.0 проверено и готово к выгрузке. Необходимо поставить тег. В обновление больше не подкладываем."},{"IMAGE":{"LINK":"https://files.shelenkov.com/bitrix/images/win.jpg"}}]}}}' \
      https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/imbot.v2.Chat.Message.send
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{"botId":456,"dialogId":"chat20921","fields":{"message":"У вас новое уведомление","attach":{"ID":1,"COLOR":"#29619b","BLOCKS":[{"MESSAGE":"Коллеги, обновление im 16.0.0 проверено и готово к выгрузке. Необходимо поставить тег. В обновление больше не подкладываем."},{"IMAGE":{"LINK":"https://files.shelenkov.com/bitrix/images/win.jpg"}}]}},"auth":"**put_access_token_here**"}' \
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
      id: number,
    }

    try {
      const response = await $b24.actions.v2.call.make<SendMessageResult>({
        method: 'imbot.v2.Chat.Message.send',
        params: {
          botId: 456,
          dialogId: 'chat20921',
          fields: {
            message: 'You have a new notification',
            attach: {
              ID: 1,
              COLOR: '#29619b',
              BLOCKS: [
                { MESSAGE: 'Colleagues, im 16.0.0 update has been verified and is ready for release. A tag needs to be set. No more patches to this update.' },
                { IMAGE: { LINK: 'https://files.shelenkov.com/bitrix/images/win.jpg' } },
              ],
            },
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
                message: 'You have a new notification',
                attach: {
                  ID: 1,
                  COLOR: '#29619b',
                  BLOCKS: [
                    { MESSAGE: 'Colleagues, im 16.0.0 update has been verified and is ready for release. A tag needs to be set. No more patches to this update.' },
                    { IMAGE: { LINK: 'https://files.shelenkov.com/bitrix/images/win.jpg' } },
                  ],
                },
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
                    'dialogId' => 'chat20921',
                    'fields' => [
                        'message' => 'У вас новое уведомление',
                        'attach' => [
                            'ID' => 1,
                            'COLOR' => '#29619b',
                            'BLOCKS' => [
                                ['MESSAGE' => 'Коллеги, обновление im 16.0.0 проверено и готово к выгрузке. Необходимо поставить тег. В обновление больше не подкладываем.'],
                                ['IMAGE' => ['LINK' => 'https://files.shelenkov.com/bitrix/images/win.jpg']]
                            ]
                        ]
                    ]
                ]
            );

        $result = $response->getResponseData()->getResult()['id'];
        echo 'Created message ID: ' . $result;
    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error adding message: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'imbot.v2.Chat.Message.send',
        {
            botId: 456,
            dialogId: 'chat20921',
            fields: {
                message: 'У вас новое уведомление',
                attach: {
                    ID: 1,
                    COLOR: '#29619b',
                    BLOCKS: [
                        { MESSAGE: 'Коллеги, обновление im 16.0.0 проверено и готово к выгрузке. Необходимо поставить тег. В обновление больше не подкладываем.' },
                        { IMAGE: { LINK: 'https://files.shelenkov.com/bitrix/images/win.jpg' } }
                    ]
                }
            }
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
            'dialogId' => 'chat20921',
            'fields' => [
                'message' => 'У вас новое уведомление',
                'attach' => [
                    'ID' => 1,
                    'COLOR' => '#29619b',
                    'BLOCKS' => [
                        ['MESSAGE' => 'Коллеги, обновление im 16.0.0 проверено и готово к выгрузке. Необходимо поставить тег. В обновление больше не подкладываем.'],
                        ['IMAGE' => ['LINK' => 'https://files.shelenkov.com/bitrix/images/win.jpg']]
                    ]
                ]
            ]
        ]
    );

    if (!empty($result['error'])) {
        echo 'Error: ' . $result['error_description'];
    } else {
        echo 'Message ID: ' . $result['result']['id'];
    }
    ```

{% endlist %}

## Продолжите изучение

- [Журнал изменений API imbot.v2](../../../change-log.md)
- [{#T}](./index.md)
- [{#T}](./block-collections/index.md)
- [{#T}](../chat-message-send.md)
