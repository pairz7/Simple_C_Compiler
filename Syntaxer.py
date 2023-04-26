"""
 语法分析器
 Implemented By Python
 Written By pair7z
"""

import sys
import re
import os
from enum import Enum
from LexerForSyntaxer import Lexer

# 分析表输出宽度控制
PREDICT_WIDTH = 16
# 分析过程记录表 输出宽度控制
RECORD_WIDTHS = [6, 40, 140, 30, 10]
# 文法符号一位/多位
# True: E->E+T|-E+格式
# False:E->E + T|- E +格式
V_SINGLE = False


class Syntaxer():
    """
    语法分析器
    """

    def __init__(self, config_path='config/simple_c_grammar.xml'):
        self.lexer = Lexer()
        self.config_path = config_path
        self.vt = ['@', '#']  # 终结符
        self.vn = []  # 非终结符
        self.token_subs = {}  # token与文法符号替换表
        self.grammar = {}  # 文法
        self.first = {}  # first集
        self.follow = {}  # follow集
        self.select = {}  # select集
        self.start_v = None  # 文法开始符
        self.predict_table = self.LL1Table()  # 预测表
        self.record = self.Record()  # 分析记录表

        self.solving_vn = ''  # 记录正在求解的非终结符 防止陷入死循环

    class LL1Table():
        """
        LL1预测表
        """

        def __init__(self):
            self.x_axis = []
            self.y_axis = []
            self.table = []
            pass

        def init_table(self, vt: list, vn: list, select: dict):
            """
            构造预测表
            :param vt:
            :param vn:
            :return:
            """
            vt.remove('@')
            self.x_axis = vt
            self.y_axis = vn

            def get_i(_vn):
                return self.y_axis.index(_vn)

            def get_j(_vt):
                return self.x_axis.index(_vt)

            self.table = [[None for j in range(len(self.x_axis))] for i in range(len(self.y_axis))]
            for _vn, generate in select:
                for _vt in select[(_vn, generate)]:
                    self.table[get_i(_vn)][get_j(_vt)] = generate

        def width_adjust(self):
            """
            自适应得到打印表格宽度
            :return:
            """
            res = [0 for i in range(len(self.x_axis))]
            for i in range(len(self.y_axis)):
                for j in range(len(self.x_axis)):
                    if self.table[i][j]:
                        l = len(' '.join(self.table[i][j])) + 5
                    else:
                        l = 10
                    if  l > res[j]:
                        res[j] = l
            return res

        def print(self):
            """
            可视化输出当前分析表的内容
            :return:
            """
            WIDTHS = self.width_adjust()
            HEADER_WIDTH = max([len(str(item)) for item in self.y_axis])
            END_CHAR = '|'
            print(''.ljust(HEADER_WIDTH), end=END_CHAR)
            for i, x_head in enumerate(self.x_axis):
                print(str(x_head).ljust(WIDTHS[i]), end=END_CHAR)
            print()
            for i in range(len(self.y_axis)):
                print(self.y_axis[i].ljust(HEADER_WIDTH), end=END_CHAR)
                for j in range(len(self.x_axis)):
                    if self.table[i][j]:
                        if V_SINGLE:
                            print(self.table[i][j].ljust(WIDTHS[j]), end=END_CHAR)
                        else:
                            print(' '.join(self.table[i][j]).ljust(WIDTHS[j]), end=END_CHAR)
                    else:
                        print(''.ljust(WIDTHS[j]), end=END_CHAR)
                print()

        def __call__(self, vn, vt):
            return self.table[self.y_axis.index(vn)][self.x_axis.index(vt)]\


    class Record():
        """
        分析记录表
        """

        def __init__(self):
            self.record = [('步骤', '分析栈', '余留符号串', '产生式', '下一步动作')]
            self.analysis_str = ''  # 分析串

        def append(self, step, stack_list, remain_list, generate, next_step):
            if isinstance(remain_list, list) or isinstance(remain_list, tuple):
                self.record.append((step, ''.join(stack_list), ''.join(remain_list), generate, next_step))
            if isinstance(remain_list, str):
                self.record.append((step, ''.join(stack_list), remain_list, generate, next_step))

        def width_adaptive(self):
            """
            根据数据宽度自适应
            :return:
            """
            widths = [0, 0, 0, 0, 0]
            for row in self.record[1:]:
                for i, item in enumerate(row):
                    if len(str(item))>widths[i]:
                        widths[i] = len(str(item)) + 5
            return widths

        def print(self):
            WIDTHS = self.width_adaptive()
            for i, header in enumerate(self.record[0]):
                print(str(header).ljust(WIDTHS[i] - 2), end='')
            print()
            for row in self.record[1:]:
                for i, item in enumerate(row):
                    print(str(item).ljust(WIDTHS[i]), end='')
                print()

    def info_head(self):
        return '[Syntaxer]: '

    def info(self, msg):
        print(self.info_head() + msg)

    def read_conf(self):
        """
        从配置文件中读取基本信息
        由于re表达式不支持\n 所以需要先做一下代换
        :return:
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_raw = f.read()
            wrap_subs = '~'
            config_raw = config_raw.replace('\n', wrap_subs)
            vt_raw = re.findall(r'<vt>(.*?)</vt>', config_raw)[0]
            # vn_raw = re.findall(r'<vn>(.*?)</vn>', config_raw)[0]
            replace_raw = re.findall(r'<replace>(.*?)</replace>', config_raw)[0]
            grammar_raw = re.findall(r'<grammar>(.*?)</grammar>', config_raw)[0]
            vt_raw = vt_raw.strip(wrap_subs)
            # vn_raw = vn_raw.strip(wrap_subs)
            replace_raw = replace_raw.strip(wrap_subs).replace(wrap_subs, '\n')
            grammar_raw = grammar_raw.strip(wrap_subs).replace(wrap_subs, '\n')
            self.read_vt(vt_raw)
            # self.read_vn(vn_raw)
            self.read_token_subs(replace_raw)
            self.read_grammar(grammar_raw)

    def read_vt(self, s: str):
        """
        读取终结符
        :param s: 以空格为分隔
        :return:
        """
        self.vt = self.union(self.vt, s.split())

    def read_vn(self, s: str):
        """
        读取非终结符
        自动从文法符号中判断
        :param s: 以空格为分隔
        :return:
        """
        self.vn = self.union(self.vn, s.split())

    def read_token_subs(self, s: str):
        """
        读取token替换表
        :param s token替换表文本 以\n换行
        :return:
        """
        for line in s.split('\n'):
            k, v = line.split()
            self.token_subs[k] = v

    def read_grammar(self, s: str):
        """
        读取grammar文法 顺便读取vn
        :param s:
        :return:
        """
        start_v = None
        if V_SINGLE:
            for line in s.split('\n'):
                vn, generate = line.split('→')
                self.vn.append(vn)
                if start_v is None:
                    start_v = vn
                self.grammar[vn] = []
                for item in generate.split('|'):
                    self.grammar[vn].append(item)
        else:
            for line in s.split('\n'):
                vn, generate = line.split('→')
                self.vn.append(vn)
                if start_v is None:
                    start_v = vn
                self.grammar[vn] = []
                for item in generate.split('|'):
                    self.grammar[vn].append(tuple(item.split()))
        # 设置文法开始符
        self.start_v = start_v

    def run(self, code_raw):
        """
        语法分析主控程序
        :param code_raw: 代码段
        :return: bool 匹配不匹配
        """
        self.is_match = False
        self.read_conf()
        self.init_data()  # 初始化各种数据结构
        # 判断是否是LL1文法 不是的话报错
        if not self.is_LL1_grammar():
            raise Exception("配置的文法不满足LL(1)规则")
        print(self.info_head() + "文法满足LL(1)规则")
        # 构造LL1预测表
        self.predict_table.init_table(self.vt, self.vn, self.select)
        # 输出LL1预测表
        print(self.info_head() + "所构造LL(1)分析表为:")
        self.predict_table.print()
        analyzed_str = self.get_tokens(code_raw)  # 待分析的串
        self.driver(analyzed_str)  # 运行语法分析驱动程序
        self.info('分析过程表为:')
        self.record.print()
        return self.is_match

    def get_tokens(self, code_raw):
        res = []
        token_list = self.lexer.run(code_raw)
        for lex in token_list:
            type = lex.type
            if type in self.token_subs.keys():
                type = self.token_subs[type]
            res.append(type)
        res.append('#')
        return res

    def driver(self, analysis):
        """
        LL(1)分析驱动程序
        :param 待分析的串
        :return:
        """
        step = 0  # 记录步骤
        stack = Stack()  # 分析栈
        work = analysis  # 余留符号串
        scan_p = 0  # 扫描指针
        # 首先 # 开始符进栈
        stack.push(['#', self.start_v])
        while stack.top() != '#':
            top = stack.top()
            v = work[scan_p]  # 正在分析的符号
            if v not in self.vt:
                raise Exception("遇到未知的符号: %s"%v)
            if top in self.vn:
                # 如果栈顶是非终结符 进行规约
                # 查分析表 如果 [top, v] is None 报错 识别失败
                generate = self.predict_table(top, v)
                if generate is None:
                    self.info('匹配失败')
                    return
                if isinstance(generate, list) or isinstance(generate, tuple):
                    generate_str = ' '.join(generate)
                else:
                    generate_str = generate
                next_step = '弹出%s, %s进栈' % (top, generate_str[::-1])
                if (V_SINGLE and generate == '@') or (not V_SINGLE and generate == ('@',)):
                    next_step = '弹出%s' % top
                self.record.append(step, stack.list(), work[scan_p:], '%s→%s' % (top, generate_str), next_step)
                # 弹出top generate逆序进栈
                stack.pop()
                if (V_SINGLE and generate != '@') or (not V_SINGLE and generate != ('@',)):
                    if isinstance(generate, str):
                        stack.push(list(generate[::-1]))
                    elif isinstance(generate, tuple) or isinstance(generate, list):
                        stack.push(generate[::-1])
            else:
                # 是终结符 与扫描符号进行比较
                if top == v:
                    # 弹出v 指针后移
                    next_step = '弹出%s, 扫描指针后移一个符号' % top
                    self.record.append(step, stack.list(), work[scan_p:], '', next_step)
                    stack.pop()
                    scan_p += 1
                else:
                    self.info('匹配失败')
                    return
                pass
            step += 1
        if stack.top() == '#' == work[scan_p]:
            self.record.append(step, stack.list(), work[scan_p:], '', '匹配成功')
            self.info("匹配成功")
            self.is_match = True
        else:
            self.info("匹配失败")

    def is_LL1_grammar(self):
        """
        判断是否是LL1文法
        :return:
        """
        for vn in self.vn:
            lists = []
            for generate in self.grammar[vn]:
                key = (vn, generate)
                lists.append(self.select[key])
            # 各同一非终结符的select交集若不为空 则不是LL1文法
            if len(self.intersect_list(lists)) > 0:
                return False
        return True

    def init_data(self):
        """
        初始化各种集合
        :return:
        """
        # 求first集
        for vn in self.vn:
            self.first[vn] = self.get_first(self.grammar[vn])
        # 求follow集
        for vn in self.vn:
            self.solving_vn = vn
            self.follow[vn] = self.get_follow(vn)
        # 求select集
        for vn in self.vn:
            for generate in self.grammar[vn]:
                key = (vn, generate)  # 代表 vn->generate
                res = []
                # 如果@不属于first(generate) : first(generate)
                # 如果@属于first(generate) : first(a, skip_empty) u follow(vn)
                first = self.get_first([generate])
                if '@' in first:
                    first.remove('@')
                    res = self.union(res, first, self.follow[vn])
                else:
                    res = self.union(res, self.get_first([generate]))
                self.select[key] = res

    def get_first(self, generate_list, skip_empty=False):
        """
        求first
        :param generate_list: 生成式列表
        :param skip_empty 跳过空串
        :return: list
        """
        # 判断是否已经求过first集 有的话直接取用
        # 判断是终结符还是非终结符
        res = []
        # 如果是空串
        for generate in generate_list:
            if (V_SINGLE and generate == '@') or (not V_SINGLE and generate == ('@',)):
                if skip_empty:
                    continue
                else:
                    res = self.union(res, ['@'])
            for i, c in enumerate(generate):
                if c in self.vt:
                    res = self.union(res, [c])
                    break
                elif c in self.vn:
                    if c in self.first.keys():
                        c_first = self.first[c]
                    else:
                        _generate_list = self.grammar[c]
                        c_first = self.get_first(_generate_list)
                    if '@' in c_first and i + 1 < len(generate):
                        # 会推导出@
                        c_first.remove('@')
                        res = self.union(res, c_first)
                    else:
                        res = self.union(res, c_first)
                        break
        return res

    def get_follow(self, vn):
        """
        求vn的follow集
        :return:
        """
        if vn in self.follow.keys():
            # 之前已求得
            return self.follow[vn]
        res = []
        if vn == self.start_v:
            res.append('#')
        for _vn, generate_list in self.grammar.items():
            for generate in generate_list:
                for i, v in enumerate(generate):
                    if v == vn:
                        flag = False
                        for j in range(i+1, len(generate)):
                            # 判断后面的first中是否包括空串 如果包括空串的话 循环向下判断
                            after_first = self.get_first([generate[j:]])
                            if '@' in after_first:
                                # 如果后面的式子会出现空的情况
                                after_first.remove('@')
                                res = self.union(res, after_first)
                            else:
                                # 没有空的情况 直接退出循环
                                res = self.union(res, after_first)
                                flag = True
                                break
                        if flag:
                            # 在最后一个符号之前已经得到了结果
                            continue
                        if _vn != self.solving_vn and _vn != vn:
                            # 防止出现无限陷入递归
                            res = self.union(res, self.get_follow(_vn))
        return res

    def has_empty_generate(self, vn):
        """
        非终结符是否能推导出空串 @
        :param vn: 非终结符
        :return:
        """
        for generate in self.grammar[vn]:
            if (V_SINGLE and generate == '@') or (not V_SINGLE and generate == ('@',)):
                return True
        return False

    def union(self, a: list, *args):
        """
        合并两个列表 去除重复项 取并集
        :param a:
        :param b:
        :return: list
        """
        for b in args:
            for item in b:
                if item not in a:
                    a.append(item)
        return a

    def intersect(self, a: list, *args):
        """
        取多个列表的交集
        :param a:
        :param args:
        :return:
        """
        lists = []
        lists.append(a)
        for b in args:
            lists.append(b)
        return self.intersect_list(lists)

    def intersect_list(self, lists: list):
        """
        求交集
        :param lists:
        :return:
        """
        a = lists[0]
        ans = []
        if len(lists) == 1:
            return ans
        is_intersect = [True for i in range(len(a))]
        for b in lists[1:]:
            for i, item in enumerate(a):
                if item not in b:
                    is_intersect[i] = False
        for i in range(len(is_intersect)):
            if is_intersect[i]:
                ans.append(a[i])
        return ans


class Stack():
    """
    自写栈 通过封装list
    """

    def __init__(self):
        self.arr = []
        pass

    def size(self):
        return len(self.arr)

    def push(self, e):
        """
        如果e是元素列表 则按照顺序依次入栈
        :param e:
        :return:
        """
        if isinstance(e, tuple) or isinstance(e, list):
            for ele in e:
                self.arr.append(ele)
        else:
            self.arr.append(e)

    def is_empty(self):
        return self.size() == 0

    def pop(self):
        if self.is_empty():
            return None
        e = self.arr.pop()
        return e

    def top(self):
        """
        获得栈顶元素
        :return:
        """
        if self.is_empty():
            return None
        return self.arr[self.size() - 1]

    def __str__(self):
        return self.arr.__str__()

    def list(self):
        return self.arr


if __name__ == '__main__':
    with open('grammar_test.c', 'r', encoding='utf-8') as f:
        code_raw = f.read()
    syntaxer = Syntaxer(config_path='config/simple_c_grammar.xml')
    syntaxer.run(code_raw)
    pass
