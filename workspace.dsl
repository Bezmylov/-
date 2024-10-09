workspace {
    name "Корпоративный мессенджер"
    description "Приложение для отправки сообщений в групповых и приватных чатах."

    model {
        user = person "Пользователь" {
            description "Пользователь корпоративного мессенджера."
        }
        corporate_messenger = softwareSystem "Корпоративный мессенджер" 

        userContext = softwareSystem "Пользовательская область" {
            description "Управление пользователями мессенджера."

            authService = container "Сервис аутентификации" {
                description "Управляет аутентификацией и авторизацией пользователей."
                technology "HTTP"
            }

            // Связь пользователя с сервисом аутентификации
            user -> authService "Запрашивает аутентификацию"
        }

        chatContext = softwareSystem "Чат-область" {
            description "Управление групповыми и приватными чатами."

            groupChat = container "Групповой чат" {
                description "Чат, в котором могут участвовать несколько пользователей."
                technology "WebSocket"
            }

            ptpChat = container "PtP Чат" {
                description "Личный чат между двумя пользователями."
                technology "WebSocket"
            }

            message = container "Сообщение" {
                description "Отправленное сообщение в групповом или PtP чате."
                technology "Data Model"
            }

            messageStorageService = container "Сервис хранения сообщений" {
                description "Управляет сохранением и извлечением сообщений."
                technology "HTTP"
            }

            // Связи между пользователем, чатами и сообщениями
            userContext -> groupChat "Участвует в"
            userContext -> ptpChat "Участвует в"
            user -> groupChat "Участвует в"
            user -> ptpChat "Участвует в"
            groupChat -> message "Содержит"
            ptpChat -> message "Содержит"
            groupChat -> messageStorageService "Использует для хранения"
            ptpChat -> messageStorageService "Использует для хранения"
            message -> messageStorageService "Использует для хранения"

            // Связь пользователя с сообщениями
            user -> message "Отправляет сообщения в"
            message -> user "Получает сообщения от"
        }

        notificationContext = softwareSystem "Уведомления" {
            description "Обработка уведомлений о новых сообщениях."

    notificationService = container "Сервис уведомлений" {
        description "Отправляет уведомления пользователям о новых сообщениях."
        technology "HTTP"
            }

            // Связи уведомлений
            groupChat -> notificationService "Отправляет уведомления о новых сообщениях"
            ptpChat -> notificationService "Отправляет уведомления о новых личных сообщениях"
            messageStorageService -> notificationService "Отправляет уведомления о новых сообщениях"
            user -> notificationService "Получает уведомления от"
        }

        historyContext = softwareSystem "История сообщений" {
            description "Управляет хранением и поиском истории сообщений."

            messageHistoryService = container "Сервис истории сообщений" {
                description "Управляет доступом к истории сообщений."
                technology "HTTP"
            }

            // Связи истории сообщений
            groupChat -> messageHistoryService "Запрашивает историю сообщений"
            ptpChat -> messageHistoryService "Запрашивает историю сообщений"
        }
    }

    views {
        systemContext userContext "UserContext" {
            include *
            autoLayout
            title "Контекст пользователей"
        }

        systemContext chatContext "ChatContext" {
            include *
            autoLayout
            title "Контекст чатов"
        }

        systemContext notificationContext "NotificationContext" {
            include *
            autoLayout
            title "Контекст уведомлений"
        }

        systemContext historyContext "MessageHistoryContext" {
            include *
            autoLayout
            title "Контекст истории сообщений"
        }

        // Динамические диаграммы
        dynamic corporate_messenger "SendGroupMessage" {
            autoLayout lr
            description "Сценарий отправки сообщения в групповой чат."

            user -> authService "1. Запрашивает аутентификацию"
            authService -> user "2. Возвращает токен аутентификации"
            user -> groupChat "3. Входит в групповой чат"
            groupChat -> message "4. Создает сообщение"
            message -> messageStorageService "5. Сохраняет сообщение"
            messageStorageService -> notificationService "6. Отправляет уведомление о новом сообщении"
            notificationService -> user "7. Отправляет уведомление остальным участникам чата"
        }

        dynamic corporate_messenger "SendPtpMessage" {
            autoLayout lr
            description "Сценарий отправки PtP сообщения."

            user -> authService "1. Запрашивает аутентификацию"
            authService -> user "2. Возвращает токен аутентификации"
            user -> ptpChat "3. Открывает PtP чат"
            ptpChat -> message "4. Создает PtP сообщение"
            message -> messageStorageService "5. Сохраняет сообщение"
            messageStorageService -> notificationService "6. Отправляет уведомление о новом PtP сообщении"
            notificationService -> user "7. Отправляет уведомление пользователю"
        }

        styles {
            element "SoftwareSystem" {
                background #438dd5
                color #ffffff
            }

            element "Container" {
                background #85bbf0
                color #000000
            }

            element "Person" {
                shape Person
                background #08427b
                color #ffffff
                fontSize 22
            }

            element "Dynamic" {
                background #f0ad4e
                color #000000
            }
        }
    }
}
