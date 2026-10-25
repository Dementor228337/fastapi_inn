class RosstatBaseError(Exception):
    """Базовая ошибка при работе с сайтом Росстата"""
    ...

class SiteUnreachableError(RosstatBaseError):
    """Сайт недоступен"""
    ...

class NoDataError(RosstatBaseError):
    """По указанному ИНН данные не найдены"""
    ...

class FileSaveError(RosstatBaseError):
    """Не удалось сохранить файл (открыт в Excel или нет прав)"""
    ...