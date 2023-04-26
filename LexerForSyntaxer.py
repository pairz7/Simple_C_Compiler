"""
 C语言词法分析器
 客制化版本 用于语法分析
 Implemented By Python
 Written By pair7z
"""
import sys
import re
import os
from enum import Enum


"""
定义Token表
"""
# 保留字
Reserved = ['int', 'long', 'short', 'float', 'double', 'char', 'bool', 'unsigned', 'signed', 'const', 'void', 'volatile',
            'enum', 'struct', 'union', 'if', 'else', 'goto', 'switch', 'case', 'do', 'while', 'for', 'continue',
            'break', 'return', 'default', 'typedef', 'auto', 'register', 'extern', 'static', 'sizeof', 'include']

# 数据类型保留字
TypeReserved = ['int', 'long', 'short', 'float', 'double', 'char', 'bool']

# 运算符
Operator = ['+', '-', '*', '/', '<', '<=', '>', '>=', '=', '==', '!=', '^', '%', '>>', '<<', '&', '&&', '|', '||',
            '!', '~', '++', '--', '+=', '-=']
# 分界符
Delimiter = [';', ':', '[', ']', '(', ')', '{', '}', '<', '>', ',', '.', '#', '"', '\'']


# type = 保留字/运算符/标识符/整型常量/浮点型常量/布尔型常量/分界符/字符串型常量/字符型常量
class TOKEN_TYPE(Enum):
    Reserved = 1
    Operator = 2
    Delimiter = 3
    IntConstant = 4
    FloatConstant = 5
    BoolConstant = 6
    StringConstant = 7
    CharConstant = 8
    Identifier = 9
    IntReserved = 10
    FloatReserved = 11
    CharReserved = 12


class lex():
    def __init__(self, token, type):
        self.token = token
        self.type = type

    def __str__(self):
        s = ''
        return "%s %s"%(self.token.ljust(20),self.type)
"""
    词法分析器
    run方法 输入代码文本 返回词法分析结果表
"""


class Lexer():
    def __init__(self):
        self.src_raw = ''  # 初始源代码
        self.src_preprocessed = ''  # 经过预处理后得到的代码串
        self.tokens = []  # 经过分词得到的token列表
        self.lex_result = []  # 词法分析结果

    """
        将tokens列表转化为词法分析结果 lex_result
        词法分析结果 (token, type)
        @param tokens token列表
        @return lex_result : list 结果列表(token, type)
    """

    def get_lex_result(self, tokens):
        lex_result = []
        for token in tokens:
            lex_result.append(lex(token,self.get_token_type(token)))
        return lex_result


    def get_specific_reserved_type(self, token):
        return token

    """
        通过token判断其类型
        获得token类型 type = 保留字/运算符/标识符/整型常量/实型常量/布尔型常量/字符型常量/字符串型常量/分界符
        @param token 
        @return type
    """

    def get_token_type(self, token):
        if self.is_reserved(token):
            return self.get_specific_reserved_type(token)
        if self.is_operator(token):
            return token
        if self.is_delimiter(token):
            return token
        if self.is_int_constant(token):
            return 'intn'
        if self.is_float_constant(token):
            return 'floatn'
        if self.is_bool_constant(token):
            return 'booln'
        if self.is_identifier(token):
            return 'id'
        if self.is_string_constant(token):
            return 'stringn'
        if self.is_char_constant(token):
            return 'charn'
        # 如果上面的都没识别出来 抛出异常 报错
        assert False,"错误: 无法识别%s的含义" % token

    """
        对预处理后的源代码进行分词获得token列表
        @param src_preprocessed 预处理后的代码 要求：去除注释 and 去除\n\t
        @return tokens : list 分词后的token列表
        双指针分词 以空格或分界符或运算符为分词位置
        特殊处理:
            1.字符(串)常量
            2.分隔符<和<= << /   >和>= >> 伪分隔符问题
            3.浮点数 .d\的伪分隔符问题 比如 .0  0. 0.0 
            4.
    """

    def split_token(self, src_preprocessed):
        src = src_preprocessed
        length = len(src)
        i = j = 0  # 双指针 i j 一前一后用来分词 src[i, j)为分词结果
        tokens = []
        while i < length:
            need_split = True  # 分词标志 用来区分当前区域是否需要分词
            handle_str = False  # 处理字符串标志 表示正在处理字符串
            if src[i] == '"' or src[i] == '\'':
                handle_str = True
                j += 1
            while j < length:
                if handle_str:
                    # 如果正在处理字符串或字符
                    # 那么如果遇到"或'就停止 右界++
                    # 如果没遇到的话 跳过其他判断 j++ 继续执行 直到遇到" '
                    if src[j] == '"' or src[j] == '\'':
                        j += 1
                        break
                    j += 1
                    continue
                if self.is_space(src[j]):
                    # 如果遇到空格 分两种情况
                    # 1.若i!=j 则以空格位置为右界 (空格要作为右界参与上一个分词)
                    # 2.若i =j 设置need_split为False 跳过分词 右界自增(空格不作为token)
                    if i == j:
                        need_split = False
                        j += 1
                    break
                if self.is_operator(src[j]):
                    #   如果是操作符 分开
                    # .如果遇到操作符 分两种情况
                    #   1.若i!=j 则以操作符位置为右界 (操作符要作为右界参与上一个分词)
                    #   2.若i =j 则以操作符位置加k为右界 (操作符自身为被分词的对象) k要判断该操作符1位长还是2位长
                    if i == j:
                        # print("debug:" + src[j:j + 2])
                        if j + 1 < length and self.is_operator(src[j:j + 2].strip()):
                            j += 2
                        else:
                            j += 1
                    break

                if self.is_delimiter(src[j]):
                    # 1.考虑.存在伪分隔符问题 判断.是否作为浮点数中的.出现
                    # 2.如果遇到分隔符 分两种情况
                    #   1.若i!=j 则以分隔符位置为右界 (分隔符要作为右界参与上一个分词)
                    #   2.若i =j 则以分隔符位置加1为右界 (分隔符自身为被分词的对象)
                    if src[j] == '.':
                        if (j + 1 < length and self.is_digital(src[j + 1])) \
                                or (j - 1 >= 0 and self.is_digital(src[j - 1])):
                            j += 1
                            continue
                    # 是分隔符
                    if i == j:
                        j += 1
                    break
                j += 1
            if need_split:
                if i!=j:
                    tokens.append(src[i:j].strip())
               # print(src[i:j].strip())
            i = j  # 取出一个词后 i从上一次右界出发
        return tokens

    """
        获得去除注释并去除换行符\n\t的源代码(假设代码无语法错误)
        注释识别两种：a. // -> \n结束   and  b.  /*----*/结束
        @param src_raw 源代码
        @return str 处理后的代码字符串
    """

    def get_preprocessed(self, src_raw):
        src_without_comment = ''
        raw_len = len(src_raw)  # 原文本的长度
        del_a = False  # 标志是否正在删除//类注释
        del_b = False  # 标志是否正在删除/* */类注释
        for i, ch in enumerate(src_raw):
            if del_a:
                # 正在删除 // 类注释 寻找结束标记\n
                if ch == '\n':
                    # 遇到\n 结束
                    del_a = False
                continue
            if del_b:
                # 正在删除 /* 类注释 寻找结束标记*/
                if i > 0:
                    if ch == '/' and src_raw[i - 1] == '*':
                        # 遇到*/结束
                        del_b = False
                continue
            # 没有正在进行删除注释 则寻找注释起始标记/* 或//
            if i < raw_len - 1 and ch == '/':
                if src_raw[i + 1] == '/':
                    # 匹配 //型注释
                    del_a = True
                    continue
                elif src_raw[i + 1] == '*':
                    # 匹配/*型注释
                    del_b = True
                    continue
            # 没有找到注释标记
            src_without_comment += ch
        return src_without_comment.replace('\n', '').replace('\t', '').replace('\r','')

    """
        判断是否是保留字
        @param token 欲判断的字符串
        @return True/False
    """

    def is_reserved(self, token: str):
        return token.strip() in Reserved

    """
        判断是否是操作符
        @param token 欲判断的字符串
        @return True/False
    """

    def is_operator(self, token: str):
        return token.strip() in Operator

    """
        判断是否是分隔符
        @param char 欲判断的字符
        @return True/False
    """

    def is_delimiter(self, char: str):
        return char.strip() in Delimiter

    """
        判断是否是空格
        @param char 欲判断的字符
        @return True/False
    """

    def is_space(self, char):
        return char == ' '

    """
        判断是否是数字
        @param char 欲判断的字符
        @return True/False
    """

    def is_digital(self, char):
        return len(char) == 1 and char >= '0' and char <= '9'

    """
        判断是否是整型常量
        @param token 欲判断的字符串
        @return True/False
    """

    def is_int_constant(self, token):
        state = 0
        if token == '':
            return False
        for i,ch in enumerate(token):
            if state == 0:
                if ch=='0':
                    state = 1
                elif '9' >= ch >= '1':
                    state = 2
                else:
                    return False
            elif state == 1:
                return False
            elif state == 2:
                if '9' >= ch >= '0':
                    state = 2
                else:
                    return False
        if state == 2 or state==1:
            return True
        else:
            return False

    """
        判断是否是浮点型常量
        @param token 欲判断的字符串
        @return True/False
    """

    def is_float_constant(self, token):
        state = 0
        if token == '':
            return False
        for i, ch in enumerate(token):
            if state==0:
                if ch == '.':
                    state = 1
                elif '9' >= ch >= '0':
                    state = 0
                else:
                    return False
            elif state==1:
                if '9' >= ch >= '0':
                    state = 1
                else:
                    return False
        if state == 1:
            return True
        else:
            return False
    """
        判断是否是布尔型常量
        @param token 欲判断的字符串
        @return True/False
    """

    def is_bool_constant(self, token):
        return token == 'true' or token == 'false'


    """
        判断是否是字符串型常量
        @param token 欲判断的字符串
        @return True/False
    """
    def is_string_constant(self, token):
        length = len(token)
        if length<2:
            return False
        token = token.strip()
        return token[0] == '"' and token[-1] == '"'

    """
        判断是否是字符型常量
        @param token 欲判断的字符串
        @return True/False
    """
    def is_char_constant(self, token):
        length = len(token)
        if length!=3 and length!=4:
            return False
        token = token.strip()
        if length == 4:
            if token[1]!= '\\':
                return False
        return token[0] == '\'' and token[-1] == '\''

    """
        判断是否是标识符
        @param token 欲判断的字符串
        @return True/False
    """

    def is_identifier(self, token):
        state = 0
        if token == '':
            return False
        for i, ch in enumerate(token):
            if state == 0:
                if ( 'z' >= ch >= 'a') \
                    or ( 'Z'>= ch >= 'A')\
                    or ( ch == '_'):
                    state = 1
                else:
                    return False
            elif state == 1:
                if ( 'z' >= ch >= 'a') \
                    or ( 'Z'>= ch >= 'A')\
                    or ('9'>=ch>='0')\
                        or (ch == '_'):
                    state = 1
                else:
                    return False
        if state == 1:
            return True
        else:
            return False


    def run(self, raw):
        self.src_raw = raw
        self.src_preprocessed = self.get_preprocessed(self.src_raw)
        self.tokens = self.split_token(self.src_preprocessed)
        self.lex_result = self.get_lex_result(self.tokens)
        return self.lex_result


"""
    通过脚本方式调用
    命令格式:
        python Lexer.py src_file_name
            src_file_name: 源代码文件名
"""


def call_bash():
    # 命令参数的数量
    args_num = 1 + 1
    arguments = sys.argv
    assert len(arguments) == args_num, '缺少必要的指令参数'
    src_file_name = arguments[1]
    assert re.search('\.(c|C)$', src_file_name), '源文件%s不是.c类型' % (src_file_name)
    assert os.path.exists(src_file_name), '源文件%s不存在' % (src_file_name)
    src_raw = ''
    with open(src_file_name, 'r', encoding='utf-8') as f:
        src_raw = f.read()
    lexer = Lexer()
    for i,item in enumerate(lexer.run(src_raw)):
        print(str(i).ljust(4),item)


if __name__ == "__main__":
    call_bash()