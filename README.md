# Python实现的简易版C语言编译器
目录结构  
|---main.py  **暂时没用**  
|---README.md  
|---test.c   **测试代码**  
|---Lexer.py  **词法分析器**  
|---Lexer.py  **改造版词法分析器 用于和语法分析配合**  
|---Syntaxer.py  **语法分析器**  
|---config  
|------simple_c_grammar.xml **语法分析配置 包括文法等配置**  

##词法分析器  
###使用方法
命令格式： python ./Component/Lexer.py 源代码文件  
例如：
>python ./Component/Lexer.py ./test.c
