import os.path
from datetime import datetime

MAX_FILE_SIZE_MB = 50.0


def check_author_access(author_role, is_project_member):
    """Проверяет, может ли автор загружать версии макетов в проект."""
    if not is_project_member:
        return False
    if author_role == "designer" or author_role == "lead":
        return True
    return False


def check_file_format(file_path):
    """Проверяет, что файл макета имеет поддерживаемый формат."""
    file_name = os.path.basename(file_path).lower()
    return (
        file_name.endswith(".fig")
        or file_name.endswith(".psd")
        or file_name.endswith(".sketch")
    )


def parse_file_size(size_text):
    """Преобразует размер файла из строки ("12,5") в число мегабайт."""
    return float(size_text.strip().replace(",", "."))


def get_upload_error(has_access, is_format_ok, size_mb):
    """Возвращает причину отказа в загрузке или пустую строку."""
    if not has_access:
        return "У автора нет прав на загрузку версий в этот проект"
    elif not is_format_ok:
        return "Неподдерживаемый формат файла (нужен .fig, .psd или .sketch)"
    elif size_mb <= 0:
        return "Файл пустой"
    elif size_mb > MAX_FILE_SIZE_MB:
        return f"Файл слишком большой (максимум {MAX_FILE_SIZE_MB} МБ)"
    else:
        return ""


def get_next_version_number(current_version):
    """Вычисляет номер новой версии макета."""
    return current_version + 1


def format_version_label(project_name, mockup_name, version_number):
    """Формирует название версии: «Проект / Макет / vN»."""
    return f"{project_name} / {mockup_name} / v{version_number}"


def main():
    project_name = "Мобильный банк"
    mockup_name = "Экран авторизации"
    author_name = "Анна Смирнова"
    author_role = "designer"
    is_project_member = True
    current_version = 3
    file_path = "uploads/login_screen.fig"
    file_size_text = "12,5"
    comment = "Изменен цвет кнопки входа"

    has_access = check_author_access(author_role, is_project_member)
    is_format_ok = check_file_format(file_path)
    size_mb = parse_file_size(file_size_text)
    error = get_upload_error(has_access, is_format_ok, size_mb)

    print(f"Проект: {project_name}")
    print(f"Макет: {mockup_name}")
    print(f"Автор: {author_name} ({author_role})")
    print(f"Файл: {os.path.basename(file_path)}, {size_mb} МБ")

    if error:
        print(f"Загрузка отклонена: {error}")
        print(f"Актуальной остается версия v{current_version}")
        return

    new_version = get_next_version_number(current_version)
    version_label = format_version_label(
        project_name, mockup_name, new_version
    )
    created_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    print("Новая версия успешно сохранена")
    print(f"Версия: {version_label}")
    print(f"Дата загрузки: {created_at}")
    print(f"Комментарий: {comment}")


if __name__ == "__main__":
    main()
