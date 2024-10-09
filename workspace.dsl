workspace {
    name "Корпоративный мессенджер"
    description "Приложение для отправки сообщений в групповых и приватных чатах."
    
    model {
        user = person "User" {
            description "Пользователь корпоративного мессенджера."
        }

        corporate_messenger = softwareSystem "Корпоративный мессенджер" {
            description "Система для отправки сообщений в групповых и приватных чатах."
            
            api = container "API" {
                description "API для взаимодействия с пользователями через веб-приложение."
                technology "HTTP"
            }
            
            web_app = container "Web-приложение" {
                description "Интерфейс для взаимодействия с мессенджером через браузер."
                technology "React"
            }

            database = container "База данных" {
                description "База данных для хранения информации о пользователях и сообщениях."
                technology "SQLite"
            }
            
            user -> web_app "Использует"
            web_app -> api "Запросы к API"
            api -> database "Чтение/Запись данных"
        }
    }

    views {
        systemContext corporate_messenger "Context" {
            include *
            autoLayout
        }

        container corporate_messenger "Containers" {
            include *
            autoLayout
        }

        dynamic corporate_messenger "SendGroupMessage" {
            autoLayout lr
            description "Отправка сообщения в групповой чат"

            user -> web_app "1. Открывает групповой чат и вводит сообщение"
            web_app -> api "2. Передает запрос на отправку сообщения"
            api -> database "3. Сохраняет сообщение в базе данных"
            api -> web_app "4. Возвращает результат пользователю"
            web_app -> user "5. Уведомляет остальных участников чата"
        }

        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
                fontSize 22
            }

            element "SoftwareSystem" {
                background #438dd5
                color #ffffff
            }

            element "Container" {
                background #85bbf0
                color #000000
            }

            element "Database" {
                shape Cylinder
            }

            element "MobileApp" {
                shape MobileDevicePortrait
            }
        }
    }
}
