import pytest

from app.validation import UploadValidationError, validate_file_name, validate_size


def test_valid_name():
    assert validate_file_name("Registrazione.MP3") == ".mp3"


def test_unsupported_extension():
    with pytest.raises(UploadValidationError) as exc:
        validate_file_name("documento.docx")
    assert exc.value.code == "unsupported_extension"


def test_empty_name():
    for name in ("", "   ", ".", ".."):
        with pytest.raises(UploadValidationError) as exc:
            validate_file_name(name)
        assert exc.value.code == "empty_filename"


def test_size_limits():
    with pytest.raises(UploadValidationError) as exc:
        validate_size(0, 100)
    assert exc.value.code == "empty_file"
    with pytest.raises(UploadValidationError) as exc:
        validate_size(101 * 1024 * 1024, 100)
    assert exc.value.code == "file_too_large"
    validate_size(1024, 100)
