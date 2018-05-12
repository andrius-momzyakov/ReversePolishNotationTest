'''
Перевод арифм. выражения в польскую запись.
Условия:
- только бинарные операторы + - * /

Упрощения:
- только целые операнды

Примеры:
'6 - 7 - (4 + 5) / 3 - 8 * 2'
'6 - 7 - (4 + (  5-7 )) / 3 - 9 / (8 * 2 /3 )'

Запуск демонстрации:
====================

>python3 main.py

Использование в коде:
=====================

obj = PolishNotation(<выражение>)

print(obj.full_trasform())

'''

import re


class PolishNotation:
    '''
    преобразование арифм. выражения в польскую нотацию
    '''
    def __init__(self, expression: str):
        self.expr = expression
        self.b_stack = {}
        self.md_stack = {}

    def transform_one_lvl(self, opex, expr=None):
        '''
        преобразование цепочки из операций одного приоритета
        :param expr:
        :param opex: регулярка для операции: '[+-]' или '[*/]'
        :return:
        '''
        expression = expr if expr else self.expr
        # print(expression)
        # одно число
        if re.match(r'^\s*(\d+|<\d+>|<b\d+>)\s*$', expression):
            return ' ' + expression + ' '
        # первый операнд
        first_opd = re.match(r'^\s*(?P<f_opd>\d+|<\d+>|<b\d+>)\s*' + opex + '?\s*', expression)
        if not first_opd:
            return ''
        # print('first_opd', first_opd.group('f_opd'))
        first_opd = first_opd.group('f_opd')
        tail = expression.replace(first_opd, '', 1)

        result = ' ' + first_opd + ' '

        for member in re.findall(r'\s*({opex})\s*(\d+|<\d+>|<b\d+>)\s*'.format(opex=opex), tail):
            result += ' ' + member[1] + ' ' + member[0] + ' '

        result = result.replace(2 * ' ', ' ')
        return result

    def brackets_tokenize(self, expr=None, lvl=None):
        '''
        токенизация выражений в скобках
        :return:
        '''
        # print('brackets_tokenize')
        expression = expr if expr else self.expr
        # print(expression)
        result = expression

        if not re.findall(r'\(([^(^)]*?)\)', expression):
            return expression

        idx = 0

        while re.findall(r'\(\s*[^(^)]*?\s*\)', result):
            for b in re.findall(r'\(\s*[^(^)]*?\s*\)', result):
                b_cnts = re.search(r'\(\s*([^(^)]*?)\s*\)', b).groups()[0] # TODO: maybe goup(0) doesn't work
                                                                              # properly!!!
                self.b_stack[idx] = {'original': b_cnts, 'result': self.simple_transform(expr=b_cnts)}
                result = result.replace(b, '<b{}>'.format(idx))
                idx += 1

        return result

    def mul_div_tokenize(self, expr=None):
        '''
        токенизация  цепочек умн-делений без скобок в исходном выражении
        :param expr:
        :return:
        '''
        # print('mul_div_tokenize')
        expression = expr if expr else self.expr
        result = expression
        idx = 0
        # print(result)
        for md in re.findall(r'\s*(?:\d+|<b\d+>)\s*(?:[*/]\s*(?:\d+|<b\d+>)\s*)+', expression):
            self.md_stack[idx] = {'original': md, 'result': self.transform_one_lvl('[*/]', expr=md)}
            # print(idx, self.md_stack[idx])
            result = result.replace(md, '<{}>'.format(idx), 1)
            idx += 1
        # print(result)
        return result, self.md_stack

    def simple_transform(self, expr=None):
        '''
        преобразование выражения в форме цеочки сложений-вычитаний без скобок
        :param expr:
        :return:
        '''
        # print('simple_transform')
        expression = expr if expr else self.expr
        result = expression
        result_tokenized = self.mul_div_tokenize(expr=result)[0]
        result = self.transform_one_lvl('[+-]', expr=result_tokenized)
        # print(result)
        for key, expr in self.md_stack.items():
            subst_str = expr['result']
            result = result.replace('<{}>'.format(key), ' {} '.format(subst_str))
        result = result.replace(2 * ' ', ' ')
        return result

    def brackets_detokenize(self, expr=None):
        expression = expr if expr else self.expr
        for idx, elem in [(idx, self.b_stack[idx]) for idx in reversed(list(self.b_stack.keys()))]:
            # sources - для страховки от зацикливания
            sources = list(self.b_stack.keys())
            sources.remove(idx)
            while re.findall(r'<b\d+>', elem['result']) and sources:
                for idx in re.findall(r'<b(\d)+>', elem['result']):
                    iidx = int(idx)
                    elem['result'] = elem['result'].replace('<b{}>'.format(idx), ' {} '
                                                            .format(self.b_stack[iidx]['result']))
                    sources.remove(iidx)
        # print(expression)
        for idx in re.findall(r'<b(\d)+>', expression):
            iidx = int(idx)
            expression = expression.replace('<b{}>'.format(idx), self.b_stack[iidx]['result'])
        return expression

    def full_transform(self, expr=None):
        # expression = expr if expr else self.expr
        # result = expression
        # print('Исходное', self.expr)
        result = self.brackets_tokenize()
        # print(result)
        result = self.simple_transform(expr=result)
        # print(result)
        result = self.brackets_detokenize(expr=result)
        while re.search(r'\s\s', result):
            result = result.replace(2 * ' ', ' ')
        if result[0] == ' ': result = result[1:]
        if result[-1] == ' ': result = result[:-1]
        return result


if __name__ == '__main__':
    example1 = "6 - 7 - (4 + 5) / 3 - 8 * 2"
    example2 = '22 - 2 / 3 - 1 + 3 * 6 / 2'
    example3 = '6 - 7 - (4 + (  5-7 )) / 3 - 9 / (8 * 2 /3 )'

    trans = PolishNotation(example1)
    print('Исходное:', trans.expr)
    print("Результат:", trans.full_transform())

    trans = PolishNotation(example2)
    print('Исходное:', trans.expr)
    print("Результат:", trans.full_transform())

    trans = PolishNotation(example3)
    print('Исходное:', trans.expr)
    print("Результат:", trans.full_transform())

