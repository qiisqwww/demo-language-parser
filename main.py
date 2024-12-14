import re
import xml.etree.ElementTree as ET
from collections import deque

# Регулярные выражения для различных конструкций
NAME_REGEX = r'[a-zA-Z][_a-zA-Z0-9]*'  # Имена переменных
NUMBER_REGEX = r'\d+'  # Числа
STRING_REGEX = r'q\((.*?)\)'  # Строки в формате q(...)
ARRAY_REGEX = r'\{(.*?)\}'  # Массивы в формате {...}
COMMENT_SINGLE_LINE_REGEX = r'%.*'  # Однострочные комментарии
COMMENT_MULTI_LINE_START = r'#='  # Начало многострочного комментария
COMMENT_MULTI_LINE_END = r'=#'  # Конец многострочного комментария

# Хранилище констант
constants = {}


# Функция для парсинга числа
def parse_number(value):
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid number: {value}")


# Функция для парсинга строки
def parse_string(value):
    match = re.match(STRING_REGEX, value)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Invalid string format: {value}")


# Функция для парсинга массива
def parse_array(value):
    items = value.split(',')
    return [parse_value(item.strip()) for item in items]


# Функция для парсинга значения (число, строка, массив или переменная)
def parse_value(value):
    if value.isdigit():
        return parse_number(value)
    elif value.startswith('q('):  # Проверка на строку
        return parse_string(value)
    elif value.startswith('{'):  # Проверка на массив
        array_content = value[1:-1]  # Убираем фигурные скобки
        return parse_array(array_content)
    else:
        # Обработка переменных
        if re.match(NAME_REGEX, value):
            if value in constants:
                return constants[value]
            else:
                raise ValueError(f"Undefined variable: {value}")
        else:
            raise ValueError(f"Invalid value format: {value}")


# Функция для выполнения постфиксных выражений
def evaluate_postfix_expression(expression):
    stack = deque()
    tokens = expression.split()

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.isdigit():
            stack.append(int(token))
        elif re.match(NAME_REGEX, token):  # Если это переменная
            if token in constants:
                stack.append(constants[token])
            else:
                raise ValueError(f"Undefined variable: {token}")
        elif token.startswith("{"):  # Массив
            array_name = token
            i += 1
            index = int(tokens[i])  # индекс массива
            if array_name in constants:
                array = constants[array_name]
                stack.append(array[index])  # добавляем элемент массива по индексу
            else:
                raise ValueError(f"Undefined variable: {array_name}")
        elif token == '+':
            b = stack.pop()
            a = stack.pop()
            if isinstance(a, int) and isinstance(b, int):
                stack.append(a + b)  # Для чисел сложение
            elif isinstance(a, str) and isinstance(b, str):
                stack.append(a + b)  # Для строк конкатенация
            else:
                raise TypeError("Cannot add string and number")
        elif token == '-':
            b = stack.pop()
            a = stack.pop()
            if isinstance(a, int) and isinstance(b, int):
                stack.append(a - b)  # Вычитание
            else:
                raise TypeError("Subtraction can only be performed on integers")
        elif token == 'chr()':
            value = stack.pop()
            if isinstance(value, int):
                stack.append(chr(value))
            else:
                raise TypeError("chr() can only be applied to an integer")
        elif token == 'mod()':
            b = stack.pop()
            a = stack.pop()
            if isinstance(a, int) and isinstance(b, int):
                stack.append(a % b)  # Для модуля
            else:
                raise TypeError("mod() can only be applied to integers")
        else:
            raise ValueError(f"Unknown operator: {token}")

        i += 1

    return stack.pop()


# Основной парсер конфигурации
def parse_configuration(input_data):
    lines = input_data.split('\n')
    xml_root = ET.Element("configuration")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Пропуск комментариев
        if re.match(COMMENT_SINGLE_LINE_REGEX, line):
            i += 1
            continue
        if line.startswith(COMMENT_MULTI_LINE_START):
            while not line.endswith(COMMENT_MULTI_LINE_END):
                i += 1
                line = lines[i].strip()
            i += 1
            continue

        try:
            # Обработка присваивания значений
            if "->" in line:
                value, name = line.split("->")
                value = parse_value(value.strip())  # Преобразуем значение
                constants[name.strip()] = value
                ET.SubElement(xml_root, "constant", name=name.strip()).text = str(value)

            # Обработка выражений в постфиксной форме
            elif line.startswith("^["):
                expression = line[2:-1]  # Убираем ^[ и ]
                result = evaluate_postfix_expression(expression.strip())
                ET.SubElement(xml_root, "expression_result").text = str(result)

            # Обработка обычных значений
            else:
                value = parse_value(line)
                ET.SubElement(xml_root, "value").text = str(value)

        except ValueError as e:
            print(f"Error parsing line: {line}. Error: {e}")

        i += 1

    return xml_root


# Запись XML в файл
def write_xml_to_file(xml_root, output_file):
    tree = ET.ElementTree(xml_root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


# Основная функция
def main(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = f.read()

    xml_root = parse_configuration(input_data)
    write_xml_to_file(xml_root, output_file)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
    else:
        main(sys.argv[1], sys.argv[2])
