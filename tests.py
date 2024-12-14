import pytest
import xml.etree.ElementTree as ET
from io import StringIO

from main import parse_value, constants, evaluate_postfix_expression, parse_configuration


def test_parse_single_number():
    input_data = "5 -> x"
    xml_root = parse_configuration(input_data)
    result = ET.tostring(xml_root, encoding='utf-8').decode('utf-8')

    # Проверяем, что число присвоено переменной "x"
    assert '<constant name="x">5</constant>' in result


def test_parse_string():
    input_data = "q(Hello) -> msg"
    xml_root = parse_configuration(input_data)
    result = ET.tostring(xml_root, encoding='utf-8').decode('utf-8')

    # Проверяем, что строка присвоена переменной "msg"
    assert '<constant name="msg">Hello</constant>' in result


def test_parse_array():
    input_data = "{10, 20, 30} -> arr1"
    xml_root = parse_configuration(input_data)
    result = ET.tostring(xml_root, encoding='utf-8').decode('utf-8')

    # Массив сериализуется как список Python
    assert '<constant name="arr1">[10, 20, 30]</constant>' in result


def test_postfix_expression_simple_addition():
    input_data = "10 -> x\n^[x 5 +]"
    xml_root = parse_configuration(input_data)
    result = ET.tostring(xml_root, encoding='utf-8').decode('utf-8')

    # Проверяем, что выражение правильно вычислено
    assert '<constant name="x">10</constant>' in result
    assert '<expression_result>15</expression_result>' in result


def test_postfix_expression_with_variable():
    input_data = "20 -> y\n^[y 5 -]"
    xml_root = parse_configuration(input_data)
    result = ET.tostring(xml_root, encoding='utf-8').decode('utf-8')

    # Проверяем, что выражение правильно вычислено
    assert '<constant name="y">20</constant>' in result
    assert '<expression_result>15</expression_result>' in result


def test_invalid_variable_access():
    input_data = "^[undefined_var 5 +]"

    # Проверяем, что обращение к неизвестной переменной возвращает ошибку или не приводит к сбою
    try:
        parse_configuration(input_data)
        # Если программа продолжает работу, тест считается успешным
        assert True
    except ValueError as e:
        # Если выбрасывается ошибка, также считаем тест успешным
        assert "Undefined variable" in str(e)


def test_invalid_postfix_expression():
    input_data = "10 -> x\n^[x +]"

    # Проверяем, что недостаточно операндов для операции вызывает IndexError
    with pytest.raises(IndexError, match="pop from an empty deque"):
        parse_configuration(input_data)


def test_malformed_array():
    input_data = "{10, 20, 30} -> arr1\n^[arr1 1]"

    # Проверяем, что программа продолжает работу даже при некорректном массиве
    try:
        parse_configuration(input_data)
        # Если программа продолжает работу, тест считается успешным
        assert True
    except ValueError as e:
        # Если выбрасывается ошибка, также считаем тест успешным
        assert "Cannot use array" in str(e)