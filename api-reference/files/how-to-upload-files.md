# Как загрузить файлы 

{% note tip "" %}

Выберите инструмент для разработки с AI-агентом:

- используйте [Битрикс24 Вайбкод](../../ai-tools/vibecode.md), чтобы создать приложение для Битрикс24 по описанию задачи без знания языков программирования. Агент напишет код и разместит приложение на сервере без ручной настройки хостинга
- используйте [MCP-сервер](../../ai-tools/mcp.md), чтобы разрабатывать интеграцию через REST API в своем проекте. Агент будет обращаться к официальной REST-документации

{% endnote %}

В Битрикс24 есть два типа файловых полей.

- **Файл.** Поле не связано с Диском, в него файлы загружаются напрямую, через строку формата Base64.

- **Файл (диск).** Поле связано с Диском, в поле хранится ID объекта диска. Формат Bаse64 в поле не обрабатывается, поэтому сначала файл загружается на Диск Битрикс24 методами [disk.folder.uploadfile](../disk/folder/disk-folder-upload-file.md) или [disk.storage.uploadfile](../disk/storage/disk-storage-upload-file.md).

Для загрузки файлов в Битрикс24 используйте стандарт кодирования Base64. Кодирование используется, когда нужно передать файл через текстовые протоколы, например HTTP.

## Как кодировать файл в Bаse64

В JavaScript можно использовать встроенный объект [FileReader](https://www.w3.org/TR/FileAPI/). Код считывает файл, который выбрал пользователь, и преобразует его в Bаse64.

```JavaScript
const fileInput = document.getElementById('fileInput'); // Поле для выбора файла

fileInput.addEventListener('change', function() {
    const file = fileInput.files[0]; // Получаем выбранный файл
    const reader = new FileReader();

    reader.onload = function() {
        const base64 = reader.result.split(',')[1]; // Получаем base64 без префикса
        console.log(base64); // Выводим результат
    };

    reader.readAsDataURL(file); // Кодируем файл в base64
});
```

В PHP можно использовать функцию [base64_encode](https://www.php.net/manual/en/function.base64-encode.php). Код читает файл с диска и кодирует его в Bаse64.

```PHP
$filePath = 'path/to/your/file.jpg'; // Путь к файлу
$fileData = file_get_contents($filePath); // Читаем файл
$base64 = base64_encode($fileData); // Кодируем в base64
```

В результате кодирования файла получим строку вида `YmFzZSDRgtC10YHRgg==`. Чем больше размер файла, тем длиннее будет строка.

## Как передать строку с Bаse64 в поле

В Битрикс24 есть 4 особенности загрузки файлов.

1. Передавайте строку с Bаse64 в поле `file`, если используете методы:

   - [documentgenerator.template.add](../document-generator/templates/document-generator-template-add.md)

   - [crm.documentgenerator.template.add](../crm/document-generator/templates/crm-document-generator-template-add.md)

    {% list tabs %}

    - JS (TS)

        ```ts
        // This snippet is an ES module: top-level await requires type="module" or a bundler.
        // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
        import { Text } from '@bitrix24/b24jssdk'
        import type { B24Frame } from '@bitrix24/b24jssdk'

        declare const $b24: B24Frame

        // Shape of the payload returned in result (match the "response handling" section of the page)
        type DocumentGeneratorTemplateAddResult = {
          id: number
        }

        try {
          const response = await $b24.actions.v2.call.make<DocumentGeneratorTemplateAddResult>({
            method: 'documentgenerator.template.add',
            params: {
              fields: {
                name: 'Sample template',
                file: 'base64_encoded_content_here', // File content encoded in base64
                code: 'example_template_code',
              },
            },
            requestId: Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
          } else {
            const result = response.getData()!.result
            console.info('Created template ID:', result.id)
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
          async function addDocumentGeneratorTemplate() {
            try {
              // Initialize the SDK inside a Bitrix24 frame
              const $b24 = await B24Js.initializeB24Frame()

              const response = await $b24.actions.v2.call.make({
                method: 'documentgenerator.template.add',
                params: {
                  fields: {
                    name: 'Sample template',
                    file: 'base64_encoded_content_here', // File content encoded in base64
                    code: 'example_template_code',
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
              console.info('Created template ID:', result.id)
            } catch (error) {
              // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
              console.error(error)
            }
          }

          document.addEventListener('DOMContentLoaded', addDocumentGeneratorTemplate)
        </script>
        ```

    - PHP
    
        ```php
        require_once('crest.php');

        $result = CRest::call(
            'documentgenerator.template.add',
            [
                'fields' => [
                    'name' => 'Пример шаблона',
                    'file' => 'base64_encoded_content_here', // Контент файла, закодированный в base64
                    'code' => 'example_template_code' 
                ]
            ]
        );
        ```

    - cURL (OAuth)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"fields":{"name":"Пример шаблона","file":"base64_encoded_content_here","code":"example_template_code"},"auth":"**put_access_token_here**"}' \
        https://**put_your_bitrix24_address**/rest/documentgenerator.template.add
        ```

    - cURL (Webhook)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"fields":{"name":"Пример шаблона","file":"base64_encoded_content_here","code":"example_template_code"}}' \
        https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/documentgenerator.template.add
        ```

    {% endlist %}

2. Передавайте массив из имени файла и строки с Bаse64, если используете методы:

   - [crm.timeline.comment.add](../crm/timeline/comments/crm-timeline-comment-add.md) — в поле `FILES`

   - [crm.item.add](../crm/universal/crm-item-add.md) — в поля типа «файл» объектов CRM
  
   - [user.add](../user/user-add.md) — в поле `PERSONAL_PHOTO`

   - [log.blogpost.add](../log/log-blogpost-add.md) — в поле `FILES`

   - [lists.element.add](../lists/elements/lists-element-add.md) — в свойства типа «файл»

   - [entity.item.add](../entity/items/entity-item-add.md) — в свойства типа «файл»

   - [bizproc.workflow.template.add](../bizproc/template/bizproc-workflow-template-add.md) — в поле `TEMPLATE_DATA`


    {% list tabs %}

    - JS (TS)

        ```ts
        // This snippet is an ES module: top-level await requires type="module" or a bundler.
        // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
        import { Text } from '@bitrix24/b24jssdk'
        import type { B24Frame } from '@bitrix24/b24jssdk'

        declare const $b24: B24Frame

        try {
          const response = await $b24.actions.v2.call.make<number>({
            method: 'bizproc.workflow.template.add',
            params: {
              DOCUMENT_TYPE: ['lists', 'BizprocDocument', 'iblock_164'],
              NAME: 'App template',
              // Business process template file content
              TEMPLATE_DATA: [
                'bp-379.bpt', // First array element — file name
                'base64_encoded_content_here', // Second array element — file content encoded in base64
              ],
            },
            requestId: Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
          } else {
            const result = response.getData()!.result
            console.info('Created template ID:', result)
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
          async function addBizprocTemplate() {
            try {
              // Initialize the SDK inside a Bitrix24 frame
              const $b24 = await B24Js.initializeB24Frame()

              const response = await $b24.actions.v2.call.make({
                method: 'bizproc.workflow.template.add',
                params: {
                  DOCUMENT_TYPE: ['lists', 'BizprocDocument', 'iblock_164'],
                  NAME: 'App template',
                  // Business process template file content
                  TEMPLATE_DATA: [
                    'bp-379.bpt', // First array element — file name
                    'base64_encoded_content_here', // Second array element — file content encoded in base64
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
              console.info('Created template ID:', result)
            } catch (error) {
              // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
              console.error(error)
            }
          }

          document.addEventListener('DOMContentLoaded', addBizprocTemplate)
        </script>
        ```

    - PHP
    
        ```php
        require_once('crest.php');

        $result = CRest::call(
            'bizproc.workflow.template.add',
            [
                'DOCUMENT_TYPE' => ['lists', 'BizprocDocument', 'iblock_164'],
                'NAME' => 'App template',
                // Контент файла с шаблоном бизнес-процесса
                'TEMPLATE_DATA' => [
                    'bp-379.bpt', // Имя файла
                    'base64_encoded_content_here' // Контент файла, закодированный в base64
                ]
            ]
        );
        ```

    - cURL (OAuth)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"DOCUMENT_TYPE":["lists","BizprocDocument","iblock_164"],"NAME":"App template","TEMPLATE_DATA":["bp-379.bpt","base64_encoded_content_here"],"auth":"**put_access_token_here**"}' \
        https://**put_your_bitrix24_address**/rest/bizproc.workflow.template.add
        ```

    - cURL (Webhook)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"DOCUMENT_TYPE":["lists","BizprocDocument","iblock_164"],"NAME":"App template","TEMPLATE_DATA":["bp-379.bpt","base64_encoded_content_here"]}' \
        https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/bizproc.workflow.template.add
        ```

    {% endlist %}

3. Передавайте объект с ключом `fileData`, который содержит массив из имени файла и строки с Bаse64, если используете методы:

   - [catalog.product.add](../catalog/product/catalog-product-add.md) — в поля `previewPicture`, `detailPicture`
   
   - [crm.lead.add](../crm/leads/crm-lead-add.md) — в поля типа «файл»

   - [crm.deal.add](../crm/deals/crm-deal-add.md) — в поля типа «файл»

   - [crm.contact.add](../crm/contacts/crm-contact-add.md) — в поля типа «файл»

   - [crm.company.add](../crm/companies/crm-company-add.md) — в поля типа «файл»

    {% list tabs %}

    - JS (TS)

        ```ts
        // This snippet is an ES module: top-level await requires type="module" or a bundler.
        // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
        import { Text } from '@bitrix24/b24jssdk'
        import type { B24Frame } from '@bitrix24/b24jssdk'

        declare const $b24: B24Frame

        // Shape of the payload returned in result (match the "response handling" section of the page)
        type CatalogProductAddResult = {
          item: {
            id: number
            name: string
            iblockId: number
          }
        }

        try {
          const response = await $b24.actions.v2.call.make<CatalogProductAddResult>({
            method: 'catalog.product.add',
            params: {
              fields: {
                iblockId: '24',
                name: 'Sample product',
                // Preview image; fileData is an array: first element is the file name, second is the base64 content
                previewPicture: {
                  fileData: [
                    'example.jpg', // Image file name
                    'base64_encoded_content_here', // Image content encoded in base64
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
            console.info('Created product ID:', result.item.id, 'Name:', result.item.name)
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
          async function addCatalogProduct() {
            try {
              // Initialize the SDK inside a Bitrix24 frame
              const $b24 = await B24Js.initializeB24Frame()

              const response = await $b24.actions.v2.call.make({
                method: 'catalog.product.add',
                params: {
                  fields: {
                    iblockId: '24',
                    name: 'Sample product',
                    // Preview image; fileData is an array: first element is the file name, second is the base64 content
                    previewPicture: {
                      fileData: [
                        'example.jpg', // Image file name
                        'base64_encoded_content_here', // Image content encoded in base64
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
              console.info('Created product ID:', result.item.id, 'Name:', result.item.name)
            } catch (error) {
              // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
              console.error(error)
            }
          }

          document.addEventListener('DOMContentLoaded', addCatalogProduct)
        </script>
        ```

    - PHP
    
        ```php
        require_once('crest.php');

        $result = CRest::call(
            'catalog.product.add',
            [
                'fields' => [
                    'iblockId' => '24', 
                    'name' => 'Пример товара', 
                    // Превью изображение товара, fileData - массив, где первый элемент - имя файла, второй - контент файла в формате base64            
                    'previewPicture' => [
                        'fileData' => [
                            'example.jpg', // Имя файла изображения
                            'base64_encoded_content_here' // Контент изображения в формате base64
                        ]
                    ]
                ]
            ]
        );
        ```

    - cURL (OAuth)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"fields":{"iblockId":"24","name":"Пример товара","previewPicture":{"fileData":["example.jpg","base64_encoded_content_here"]}},"auth":"**put_access_token_here**"}' \
        https://**put_your_bitrix24_address**/rest/catalog.product.add
        ```

    - cURL (Webhook)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"fields":{"iblockId":"24","name":"Пример товара","previewPicture":{"fileData":["example.jpg","base64_encoded_content_here"]}}}' \
        https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/catalog.product.add
        ```

    {% endlist %}

4. Передавайте параметр `fileContent`, который содержит массив из имени файла и строки с Bаse64, если используете методы:

   - [disk.file.uploadversion](../disk/file/disk-file-upload-version.md)

   - [disk.storage.uploadfile](../disk/storage/disk-storage-upload-file.md)

   - [disk.folder.uploadfile](../disk/folder/disk-folder-upload-file.md)

   - [telephony.externalCall.attachRecord](../telephony/telephony-external-call-attach-record.md)

   - [catalog.productImage.add](../catalog/product-image/catalog-product-image-add.md)

    {% list tabs %}

    - JS (TS)

        ```ts
        // This snippet is an ES module: top-level await requires type="module" or a bundler.
        // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
        import { Text } from '@bitrix24/b24jssdk'
        import type { B24Frame } from '@bitrix24/b24jssdk'

        declare const $b24: B24Frame

        // Shape of the payload returned in result (match the "response handling" section of the page)
        type DiskFileUploadVersionResult = {
          file: {
            id: number
            name: string
          }
        }

        try {
          const response = await $b24.actions.v2.call.make<DiskFileUploadVersionResult>({
            method: 'disk.file.uploadversion',
            params: {
              id: 4, // ID of the file to upload a new version for
              // Content of the file being uploaded as a new version
              fileContent: [
                '1.gif', // First array element — file name
                'base64_encoded_content_here', // Second array element — file content encoded in base64
              ],
            },
            requestId: Text.getUuidRfc4122()
          })

          // The payload is available only on a successful response
          if (!response.isSuccess) {
            console.error(response.getErrorMessages().join('; '))
          } else {
            const result = response.getData()!.result
            console.info('Uploaded file version ID:', result.file.id, 'Name:', result.file.name)
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
          async function uploadFileVersion() {
            try {
              // Initialize the SDK inside a Bitrix24 frame
              const $b24 = await B24Js.initializeB24Frame()

              const response = await $b24.actions.v2.call.make({
                method: 'disk.file.uploadversion',
                params: {
                  id: 4, // ID of the file to upload a new version for
                  // Content of the file being uploaded as a new version
                  fileContent: [
                    '1.gif', // First array element — file name
                    'base64_encoded_content_here', // Second array element — file content encoded in base64
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
              console.info('Uploaded file version ID:', result.file.id, 'Name:', result.file.name)
            } catch (error) {
              // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
              console.error(error)
            }
          }

          document.addEventListener('DOMContentLoaded', uploadFileVersion)
        </script>
        ```

    - PHP
    
        ```php
        require_once('crest.php');

        $result = CRest::call(
            'disk.file.uploadversion',
            [
                'id' => 4, // Идентификатор файла, для которого загружается новая версия
                'fileContent' => [
                    '1.gif', // Имя файла
                    'base64_encoded_content_here' // Контент файла в формате base64
                ]
            ]
        );
        ```

    - cURL (OAuth)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"id":4,"fileContent":["1.gif","base64_encoded_content_here"],"auth":"**put_access_token_here**"}' \
        https://**put_your_bitrix24_address**/rest/disk.file.uploadversion
        ```

    - cURL (Webhook)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"id":4,"fileContent":["1.gif","base64_encoded_content_here"]}' \
        https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/disk.file.uploadversion
        ```

    {% endlist %}

## Как загрузить файлы во множественное поле

Если у поля есть флаг «множественное», в него можно загрузить несколько файлов. Формат зависит от метода.

1. Передавайте массив, где каждый элемент — это имя файла и файл в формате Bаse64, если используете методы:

   - [crm.item.add](../crm/universal/crm-item-add.md) — поля типа «файл»

   - [lists.element.add](../lists/elements/lists-element-add.md) — свойства типа «файл»

   - [crm.timeline.comment.add](../crm/timeline/comments/crm-timeline-comment-add.md) — поле `FILES`

   - [log.blogpost.add](../log/log-blogpost-add.md) — поле `FILES`

    {% list tabs %}

    - JS (TS)

        ```ts
        // This snippet is an ES module: top-level await requires type="module" or a bundler.
        // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
        import { Text } from '@bitrix24/b24jssdk'
        import type { B24Frame } from '@bitrix24/b24jssdk'

        declare const $b24: B24Frame

        // Shape of the payload returned in result (match the "response handling" section of the page)
        type CrmItemAddResult = {
          item: {
            id: number
            title: string
            entityTypeId: number
          }
        }

        try {
          const response = await $b24.actions.v2.call.make<CrmItemAddResult>({
            method: 'crm.item.add',
            params: {
              entityTypeId: 2,
              fields: {
                title: 'New deal (example for REST method)',
                // Multiple file field with an array of files
                ufCrm_123456: [
                  [
                    'green_pixel.png', // File name #1
                    'base64_encoded_content_here', // Base64 content of the first file
                  ],
                  [
                    'blue_pixel.png', // File name #2
                    'base64_encoded_content_here', // Base64 content of the second file
                  ],
                  [
                    'red_pixel.png', // File name #3
                    'base64_encoded_content_here', // Base64 content of the third file
                  ],
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
            console.info('Created item ID:', result.item.id, 'Title:', result.item.title)
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
          async function addCrmItem() {
            try {
              // Initialize the SDK inside a Bitrix24 frame
              const $b24 = await B24Js.initializeB24Frame()

              const response = await $b24.actions.v2.call.make({
                method: 'crm.item.add',
                params: {
                  entityTypeId: 2,
                  fields: {
                    title: 'New deal (example for REST method)',
                    // Multiple file field with an array of files
                    ufCrm_123456: [
                      [
                        'green_pixel.png', // File name #1
                        'base64_encoded_content_here', // Base64 content of the first file
                      ],
                      [
                        'blue_pixel.png', // File name #2
                        'base64_encoded_content_here', // Base64 content of the second file
                      ],
                      [
                        'red_pixel.png', // File name #3
                        'base64_encoded_content_here', // Base64 content of the third file
                      ],
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
              console.info('Created item ID:', result.item.id, 'Title:', result.item.title)
            } catch (error) {
              // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
              console.error(error)
            }
          }

          document.addEventListener('DOMContentLoaded', addCrmItem)
        </script>
        ```

    - PHP

        ```php
        require_once('crest.php');

        $result = CRest::call(
            'crm.item.add',
            [
                'entityTypeId' => 2, 
                'fields' => [
                    'title' => 'Новая сделка (специально для примера REST методов)', 
                    // Множественное поле с массивом файлов
                    'ufCrm_123456' => [
                        [
                            'green_pixel.png', // Имя файла №1
                            'base64_encoded_content_here' // Base64-контент первого файла
                        ],
                        [
                            'blue_pixel.png', // Имя файла №2
                            'base64_encoded_content_here' // Base64-контент второго файла
                        ],
                        [
                            'red_pixel.png', // Имя файла №3
                            'base64_encoded_content_here' // Base64-контент третьего файла
                        ]
                    ]
                ]
            ]
        );
        ```

    - cURL (OAuth)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"entityTypeId":2,"fields":{"title":"Новая сделка (специально для примера REST методов)","ufCrm_123456":[["green_pixel.png","base64_encoded_content_here"],["blue_pixel.png","base64_encoded_content_here"],["red_pixel.png","base64_encoded_content_here"]]},"auth":"**put_access_token_here**"}' \
        https://**put_your_bitrix24_address**/rest/crm.item.add
        ```

    - cURL (Webhook)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"entityTypeId":2,"fields":{"title":"Новая сделка (специально для примера REST методов)","ufCrm_123456":[["green_pixel.png","base64_encoded_content_here"],["blue_pixel.png","base64_encoded_content_here"],["red_pixel.png","base64_encoded_content_here"]]}}' \
        https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/crm.item.add
        ```

    {% endlist %}

2. Передавайте массив объектов, где каждый объект содержит поле `value` с ключом `fileData`, если используете метод:

   - [catalog.product.add](../catalog/product/catalog-product-add.md) — поля типа «файл»

    {% list tabs %}

    - JS (TS)

        ```ts
        // This snippet is an ES module: top-level await requires type="module" or a bundler.
        // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
        import { Text } from '@bitrix24/b24jssdk'
        import type { B24Frame } from '@bitrix24/b24jssdk'

        declare const $b24: B24Frame

        // Shape of the payload returned in result (match the "response handling" section of the page)
        type CatalogProductAddResult = {
          item: {
            id: number
            name: string
            iblockId: number
          }
        }

        try {
          const response = await $b24.actions.v2.call.make<CatalogProductAddResult>({
            method: 'catalog.product.add',
            params: {
              fields: {
                iblockId: 1,
                name: 'Sample product',
                PROPERTY_1077: [
                  {
                    value: {
                      fileData: [
                        'blue_pixel.txt', // File name
                        'YmFzZSDRgtC10YHRgg==', // Base64 content
                      ],
                    },
                  },
                  {
                    value: {
                      fileData: [
                        'red_pixel.txt', // File name
                        'YmFzZSDRgtC10YHRgg==', // Base64 content
                      ],
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
            console.info('Created product ID:', result.item.id, 'Name:', result.item.name)
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
          async function addCatalogProductWithFiles() {
            try {
              // Initialize the SDK inside a Bitrix24 frame
              const $b24 = await B24Js.initializeB24Frame()

              const response = await $b24.actions.v2.call.make({
                method: 'catalog.product.add',
                params: {
                  fields: {
                    iblockId: 1,
                    name: 'Sample product',
                    PROPERTY_1077: [
                      {
                        value: {
                          fileData: [
                            'blue_pixel.txt', // File name
                            'YmFzZSDRgtC10YHRgg==', // Base64 content
                          ],
                        },
                      },
                      {
                        value: {
                          fileData: [
                            'red_pixel.txt', // File name
                            'YmFzZSDRgtC10YHRgg==', // Base64 content
                          ],
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
              console.info('Created product ID:', result.item.id, 'Name:', result.item.name)
            } catch (error) {
              // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
              console.error(error)
            }
          }

          document.addEventListener('DOMContentLoaded', addCatalogProductWithFiles)
        </script>
        ```

    - PHP

        ```php
        require_once('crest.php');

        $result = CRest::call(
            'catalog.product.add',
            [
                'fields' => [
                    'iblockId' => 1,
                    'name' => 'Пример товара',
                    'PROPERTY_1077' => [
                        [
                            'value' => [
                                'fileData' => [
                                    'blue_pixel.txt',
                                    'YmFzZSDRgtC10YHRgg=='
                                ]
                            ]
                        ],
                        [
                            'value' => [
                                'fileData' => [
                                    'red_pixel.txt',
                                    'YmFzZSDRgtC10YHRgg=='
                                ]
                            ]
                        ]
                    ]
                ]
            ]
        );

        echo '<PRE>';
        print_r($result);
        echo '</PRE>';
        ```        

    - cURL (Webhook)

        ```bash
        curl -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d '{"fields": {"iblockId": 1, "name": "Пример товара", "PROPERTY_1077": [{"value": {"fileData": ["blue_pixel.txt", "YmFzZSDRgtC10YHRgg=="]}}, {"value": {"fileData": ["red_pixel.txt", "YmFzZSDRgtC10YHRgg=="]}}]}}' https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/catalog.product.add
        ```

    - cURL (OAuth)

        ```bash
        curl -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d '{"fields": {"iblockId": 1, "name": "Пример товара", "PROPERTY_1077": [{"value": {"fileData": ["blue_pixel.txt", "YmFzZSDRgtC10YHRgg=="]}}, {"value": {"fileData": ["red_pixel.txt", "YmFzZSDRgtC10YHRgg=="]}}]}, "auth": "**put_access_token_here**"}' https://**put_your_bitrix24_address**/rest/catalog.product.add
        ```

    {% endlist %}

3. Передавайте массив объектов с ключом `fileData`, если используете методы:

   - [crm.lead.add](../crm/leads/crm-lead-add.md) — поля типа «файл»

   - [crm.deal.add](../crm/deals/crm-deal-add.md) — поля типа «файл»

   - [crm.contact.add](../crm/contacts/crm-contact-add.md) — поля типа «файл»

   - [crm.company.add](../crm/companies/crm-company-add.md) — поля типа «файл»

    {% list tabs %}

    - JS (TS)

        ```ts
        // This snippet is an ES module: top-level await requires type="module" or a bundler.
        // $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
        import { Text } from '@bitrix24/b24jssdk'
        import type { B24Frame } from '@bitrix24/b24jssdk'

        declare const $b24: B24Frame

        try {
          const response = await $b24.actions.v2.call.make<number>({
            method: 'crm.lead.add',
            params: {
              fields: {
                TITLE: 'Sample lead',
                UF_CRM_1711610801: [
                  {
                    fileData: [
                      'file1.png', // File name
                      'base64_1', // Base64 content
                    ],
                  },
                  {
                    fileData: [
                      'file2.png', // File name
                      'base64_2', // Base64 content
                    ],
                  },
                  {
                    fileData: [
                      'file3.png', // File name
                      'base64_3', // Base64 content
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
            console.info('Created lead ID:', result)
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
          async function addLead() {
            try {
              // Initialize the SDK inside a Bitrix24 frame
              const $b24 = await B24Js.initializeB24Frame()

              const response = await $b24.actions.v2.call.make({
                method: 'crm.lead.add',
                params: {
                  fields: {
                    TITLE: 'Sample lead',
                    UF_CRM_1711610801: [
                      {
                        fileData: [
                          'file1.png', // File name
                          'base64_1', // Base64 content
                        ],
                      },
                      {
                        fileData: [
                          'file2.png', // File name
                          'base64_2', // Base64 content
                        ],
                      },
                      {
                        fileData: [
                          'file3.png', // File name
                          'base64_3', // Base64 content
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
              console.info('Created lead ID:', result)
            } catch (error) {
              // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
              console.error(error)
            }
          }

          document.addEventListener('DOMContentLoaded', addLead)
        </script>
        ```

    - PHP

        ```php
        require_once('crest.php');

        $result = CRest::call(
            'crm.lead.add',
            [
                'fields' => [
                    'TITLE' => 'Пример лида',
                    'UF_CRM_1711610801' => [
                        [
                            'fileData' => [
                                'file1.png', // Имя файла
                                'base64_1' // Base64-контент
                            ]
                        ],
                        [
                            'fileData' => [
                                'file2.png', // Имя файла
                                'base64_2' // Base64-контент
                            ]
                        ],
                        [
                            'fileData' => [
                                'file3.png', // Имя файла
                                'base64_3' // Base64-контент
                            ]
                        ]
                    ]
                ]
            ]
        );
        ```

    - cURL (OAuth)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"fields":{"TITLE":"Пример лида","UF_CRM_1711610801":[{"fileData":["file1.png","base64_1"]},{"fileData":["file2.png","base64_2"]},{"fileData":["file3.png","base64_3"]}]},"auth":"**put_access_token_here**"}' \
        https://**put_your_bitrix24_address**/rest/crm.lead.add
        ```

    - cURL (Webhook)

        ```bash
        curl -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"fields":{"TITLE":"Пример лида","UF_CRM_1711610801":[{"fileData":["file1.png","base64_1"]},{"fileData":["file2.png","base64_2"]},{"fileData":["file3.png","base64_3"]}]}}' \
        https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/crm.lead.add
        ```

    {% endlist %}

## Ограничения при работе с файлами

- Ограничение на длину GET-запроса — 2048 символов, это длина URL-адреса. Файлы, кодированные в Bаse64, часто превышают это значение. Для передачи больших файлов используйте POST-запрос.

- Ограничение на размер POST-запроса в Битрикс24 — 2Гб. Файлы больше 2Гб обработаны не будут. Если в одном в запросе передается несколько файлов суммарно больше 2Гб — запрос прервется. Для загрузки нескольких файлов большого размера передавайте данные в отдельных запросах.

- Ограничение на время выполнения запроса — 60 секунд для облачного Битрикс24. Запрос прервется по таймауту, если обработка занимает дольше 60 секунд. Проверить время выполнения запроса можно в объекте [time](../data-types.md#time) ответа на запрос, параметр `duration`.

- Если при передаче файла, закодированного строку в Bаse64, метод выполняется в адресной строке GET-запросом или метод выполняется через curl — Bаse64 нужно дополнительно [закодировать в urlencode](../../settings/how-to-call-rest-api/data-encoding.md), иначе файл не прочитается.
