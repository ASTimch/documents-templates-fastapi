template_field_type_list = [
    (1, "str", "Строка", "/^.*$/"),
    (2, "int", "Целочисленный", "/^\\d*$/"),
    (3, "float", "Вещественный", "/^\\d+(?:\\.|,)?\\d*$/"),
]

# Построение словаря соответствий type:mask
template_field_type_mask_mapping = {
    x[1]: x[3] for x in template_field_type_list
}

templates_for_write = [
    {
        "title": "Шаблон 1",
        "deleted": "False",
        "description": "Описание шаблона 1",
        "grouped_fields": [
            {
                "name": "Группа 1",
                "fields": [
                    {
                        "tag": "Тэг1",
                        "name": "Наименование 1",
                        "hint": "Описание 1",
                        "type": "str",
                        "length": 100,
                    },
                    {
                        "tag": "Тэг2",
                        "name": "Наименование 2",
                        "hint": "Описание 2",
                        "type": "int",
                        "length": 20,
                    },
                ],
            },
            {
                "name": "Группа 2",
                "fields": [
                    {
                        "tag": "Тэг3",
                        "name": "Наименование 3",
                        "hint": "Описание 3",
                        "type": "str",
                        "length": 40,
                    },
                    {
                        "tag": "Тэг4",
                        "name": "Наименование 4",
                        "hint": "Описание 4",
                        "type": "float",
                        "length": 40,
                        "default": "0.0",
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "tag": "Тэг5",
                "name": "Наименование 5",
                "hint": "Описание 5",
                "type": "str",
                "length": 100,
            },
            {
                "tag": "Тэг6",
                "name": "Наименование 6",
                "hint": "Описание 6",
                "type": "str",
                "length": 100,
            },
        ],
    },
    {
        "title": "Шаблон 2",
        "deleted": "False",
        "description": "Описание шаблона 2",
        "grouped_fields": [
            {
                "name": "Группа 3",
                "fields": [
                    {
                        "tag": "Тэг 7",
                        "name": "Наименование 7",
                        "hint": "Описание 7",
                        "type": "str",
                        "length": 100,
                    },
                    {
                        "tag": "Тэг8",
                        "name": "Наименование 8",
                        "hint": "Описание 8",
                        "type": "int",
                        "length": 20,
                    },
                ],
            },
            {
                "name": "Группа 4",
                "fields": [
                    {
                        "tag": "Тэг9",
                        "name": "Наименование 9",
                        "hint": "Описание 9",
                        "type": "str",
                        "length": 40,
                        "default": "значение по умолчанию",
                    },
                    {
                        "tag": "Тэг10",
                        "name": "Наименование 10",
                        "hint": "Описание 10",
                        "type": "float",
                        "length": 40,
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "tag": "Тэг11",
                "name": "Наименование 11",
                "hint": "Описание 11",
                "type": "str",
                "length": 100,
            },
            {
                "tag": "Тэг12",
                "name": "Наименование 12",
                "hint": "Описание 12",
                "type": "str",
                "length": 100,
            },
        ],
    },
]

templates_for_read = [
    {
        "id": 1,
        "title": "Шаблон 1",
        "deleted": False,
        "description": "Описание шаблона 1",
        "created_at": "2023-12-20T11:37:24.683Z",
        "updated_at": "2023-12-20T11:37:24.683Z",
        "category_id": None,
        "owner_id": None,
        "is_favorited": False,
        "thumbnail": None,
        "grouped_fields": [
            {
                "id": 1,
                "name": "Группа 1",
                "fields": [
                    {
                        "id": 1,
                        "tag": "Тэг1",
                        "name": "Наименование 1",
                        "hint": "Описание 1",
                        "type": "str",
                        "length": 100,
                        "mask": template_field_type_mask_mapping.get("str"),
                        "default": None,
                    },
                    {
                        "id": 2,
                        "tag": "Тэг2",
                        "name": "Наименование 2",
                        "hint": "Описание 2",
                        "type": "int",
                        "length": 20,
                        "mask": template_field_type_mask_mapping.get("int"),
                        "default": None,
                    },
                ],
            },
            {
                "id": 2,
                "name": "Группа 2",
                "fields": [
                    {
                        "id": 3,
                        "tag": "Тэг3",
                        "name": "Наименование 3",
                        "hint": "Описание 3",
                        "type": "str",
                        "length": 40,
                        "mask": template_field_type_mask_mapping.get("str"),
                        "default": None,
                    },
                    {
                        "id": 4,
                        "tag": "Тэг4",
                        "name": "Наименование 4",
                        "hint": "Описание 4",
                        "type": "float",
                        "length": 40,
                        "mask": template_field_type_mask_mapping.get("float"),
                        "default": "0.0",
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "id": 5,
                "tag": "Тэг5",
                "name": "Наименование 5",
                "hint": "Описание 5",
                "type": "str",
                "length": 100,
                "mask": template_field_type_mask_mapping.get("str"),
                "default": None,
            },
            {
                "id": 6,
                "tag": "Тэг6",
                "name": "Наименование 6",
                "hint": "Описание 6",
                "type": "str",
                "length": 100,
                "mask": template_field_type_mask_mapping.get("str"),
                "default": None,
            },
        ],
    },
    {
        "id": 2,
        "title": "Шаблон 2",
        "deleted": False,
        "description": "Описание шаблона 2",
        "created_at": "2023-12-20T11:37:24.683Z",
        "updated_at": "2023-12-20T11:37:24.683Z",
        "category_id": None,
        "is_favorited": False,
        "owner_id": None,
        "thumbnail": None,
        "grouped_fields": [
            {
                "id": 3,
                "name": "Группа 3",
                "fields": [
                    {
                        "id": 7,
                        "tag": "Тэг 7",
                        "name": "Наименование 7",
                        "hint": "Описание 7",
                        "type": "str",
                        "length": 100,
                        "mask": template_field_type_mask_mapping.get("str"),
                        "default": None,
                    },
                    {
                        "id": 8,
                        "tag": "Тэг8",
                        "name": "Наименование 8",
                        "hint": "Описание 8",
                        "type": "int",
                        "length": 20,
                        "mask": template_field_type_mask_mapping.get("int"),
                        "default": None,
                    },
                ],
            },
            {
                "id": 4,
                "name": "Группа 4",
                "fields": [
                    {
                        "id": 9,
                        "tag": "Тэг9",
                        "name": "Наименование 9",
                        "hint": "Описание 9",
                        "type": "str",
                        "length": 40,
                        "mask": template_field_type_mask_mapping.get("str"),
                        "default": "значение по умолчанию",
                    },
                    {
                        "id": 10,
                        "tag": "Тэг10",
                        "name": "Наименование 10",
                        "hint": "Описание 10",
                        "type": "float",
                        "length": 40,
                        "mask": template_field_type_mask_mapping.get("float"),
                        "default": None,
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "id": 11,
                "tag": "Тэг11",
                "name": "Наименование 11",
                "hint": "Описание 11",
                "type": "str",
                "length": 100,
                "mask": template_field_type_mask_mapping.get("str"),
                "default": None,
            },
            {
                "id": 12,
                "tag": "Тэг12",
                "name": "Наименование 12",
                "hint": "Описание 12",
                "type": "str",
                "length": 100,
                "mask": template_field_type_mask_mapping.get("str"),
                "default": None,
            },
        ],
    },
]

template_with_invalid_type_field = {
    "title": "Шаблон 1",
    "deleted": False,
    "description": "Описание шаблона 1",
    "grouped_fields": [
        {
            "name": "Группа 1",
            "fields": [
                {
                    "tag": "Тэг1",
                    "name": "Наименование 1",
                    "hint": "Описание 1",
                    "type": "invalid_type1",
                    "length": 100,
                },
                {
                    "tag": "Тэг2",
                    "name": "Наименование 2",
                    "hint": "Описание 2",
                    "type": "int",
                    "length": 20,
                },
            ],
        }
    ],
    "ungrouped_fields": [
        {
            "tag": "Тэг5",
            "name": "Наименование 5",
            "hint": "Описание 5",
            "type": "invalid_type2",
            "length": 100,
        }
    ],
}

broken_docx_path = "app/tests/service_tests/docx/broken_template1.docx"
broken_docx_error_tags = (("Тэг7",), ("Тэг6",))

documents_for_read = [
    {
        "id": 1,
        "template_id": 1,
        "description": "Наименование документа 1",
        # "created_at": "2023-12-20T11:37:24.683Z",
        # "updated_at": "2023-12-20T11:37:24.683Z",
        "owner_id": 1,
        # "thumbnail": None,
        "grouped_fields": [
            {
                "id": 1,
                "name": "Группа 1",
                "fields": [
                    {
                        "id": 1,
                        "tag": "Тэг1",
                        "name": "Наименование 1",
                        "hint": "Описание 1",
                        "type": "str",
                        "length": 100,
                        "mask": template_field_type_mask_mapping.get("str"),
                        "default": None,
                        "value": "Значение поля 1",
                    },
                    {
                        "id": 2,
                        "tag": "Тэг2",
                        "name": "Наименование 2",
                        "hint": "Описание 2",
                        "type": "int",
                        "length": 20,
                        "mask": template_field_type_mask_mapping.get("int"),
                        "default": None,
                        "value": "Значение поля 2",
                    },
                ],
            },
            {
                "id": 2,
                "name": "Группа 2",
                "fields": [
                    {
                        "id": 3,
                        "tag": "Тэг3",
                        "name": "Наименование 3",
                        "hint": "Описание 3",
                        "type": "str",
                        "length": 40,
                        "mask": template_field_type_mask_mapping.get("str"),
                        "default": None,
                        "value": "Значение поля 3",
                    },
                    {
                        "id": 4,
                        "tag": "Тэг4",
                        "name": "Наименование 4",
                        "hint": "Описание 4",
                        "type": "float",
                        "length": 40,
                        "mask": template_field_type_mask_mapping.get("float"),
                        "default": "0.0",
                        "value": "Значение поля 4",
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "id": 5,
                "tag": "Тэг5",
                "name": "Наименование 5",
                "hint": "Описание 5",
                "type": "str",
                "length": 100,
                "mask": template_field_type_mask_mapping.get("str"),
                "default": None,
                "value": "Значение поля 5",
            },
            {
                "id": 6,
                "tag": "Тэг6",
                "name": "Наименование 6",
                "hint": "Описание 6",
                "type": "str",
                "length": 100,
                "mask": template_field_type_mask_mapping.get("str"),
                "default": None,
                "value": "Значение поля 6",
            },
        ],
    },
    {
        "id": 2,
        "template_id": 1,
        "description": "Наименование документа 2",
        # "created_at": "2023-12-20T11:37:24.683Z",
        # "updated_at": "2023-12-20T11:37:24.683Z",
        "owner_id": 1,
        # "thumbnail": None,
        "grouped_fields": [
            {
                "id": 1,
                "name": "Группа 1",
                "fields": [
                    {
                        "id": 1,
                        "tag": "Тэг1",
                        "name": "Наименование 1",
                        "hint": "Описание 1",
                        "type": "str",
                        "length": 100,
                        "mask": template_field_type_mask_mapping.get("str"),
                        "default": None,
                        "value": "Значение поля 11",
                    },
                    {
                        "id": 2,
                        "tag": "Тэг2",
                        "name": "Наименование 2",
                        "hint": "Описание 2",
                        "type": "int",
                        "length": 20,
                        "mask": template_field_type_mask_mapping.get("int"),
                        "default": None,
                        "value": "Значение поля 12",
                    },
                ],
            },
            {
                "id": 2,
                "name": "Группа 2",
                "fields": [
                    {
                        "id": 3,
                        "tag": "Тэг3",
                        "name": "Наименование 3",
                        "hint": "Описание 3",
                        "type": "str",
                        "length": 40,
                        "mask": template_field_type_mask_mapping.get("str"),
                        "default": None,
                        "value": "Значение поля 13",
                    },
                    {
                        "id": 4,
                        "tag": "Тэг4",
                        "name": "Наименование 4",
                        "hint": "Описание 4",
                        "type": "float",
                        "length": 40,
                        "mask": template_field_type_mask_mapping.get("float"),
                        "default": "0.0",
                        "value": "Значение поля 14",
                    },
                ],
            },
        ],
        "ungrouped_fields": [
            {
                "id": 5,
                "tag": "Тэг5",
                "name": "Наименование 5",
                "hint": "Описание 5",
                "type": "str",
                "length": 100,
                "mask": template_field_type_mask_mapping.get("str"),
                "default": None,
                "value": "Значение поля 15",
            },
            {
                "id": 6,
                "tag": "Тэг6",
                "name": "Наименование 6",
                "hint": "Описание 6",
                "type": "str",
                "length": 100,
                "mask": template_field_type_mask_mapping.get("str"),
                "default": None,
                "value": "Значение поля 16",
            },
        ],
    },
]

documents_for_write = [
    {
        "template_id": 1,
        "description": "Наименование документа 1",
        "owner_id": 1,
        "completed": True,
        "fields": [
            {
                "field_id": 1,
                "value": "Значение поля 1",
            },
            {
                "field_id": 2,
                "value": "Значение поля 2",
            },
            {
                "field_id": 3,
                "value": "Значение поля 3",
            },
            {
                "field_id": 4,
                "value": "Значение поля 4",
            },
            {
                "field_id": 5,
                "value": "Значение поля 5",
            },
            {
                "field_id": 6,
                "value": "Значение поля 6",
            },
        ],
    },
    {
        "template_id": 1,
        "description": "Наименование документа 1",
        "owner_id": 1,
        "completed": False,
        "fields": [
            {
                "field_id": 1,
                "value": "Значение поля 11",
            },
            {
                "field_id": 2,
                "value": "Значение поля 12",
            },
            {
                "field_id": 3,
                "value": "Значение поля 13",
            },
            {
                "field_id": 4,
                "value": "Значение поля 14",
            },
            {
                "field_id": 5,
                "value": "Значение поля 15",
            },
            {
                "field_id": 6,
                "value": None,
            },
        ],
    },
]
