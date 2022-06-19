class ApiError(Exception):
    """Ошибка, выбрасываемая при некорректной работе с API."""

    pass


class SendMessageError(Exception):
    """Ошибка, выбрасываемая при отправке сообщения."""

    pass
