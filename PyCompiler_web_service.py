"""
    PyCompiler
    Web服务接口
"""
import sys
from Lexer import Lexer
from Syntaxer import Syntaxer
from flask import Flask, request, make_response,jsonify
from gevent.pywsgi import WSGIServer
app = Flask(__name__)
lexer = Lexer()


@app.route('/getLex', methods = ['POST'])
def get_lex():
    try:
        req = request
        raw = req.data
        src = raw.decode('utf-8')
        src = src[1:len(src)-1]
        src = src.replace('\\t','\t')
        src = src.replace('\\"','\"')
        # src = src.replace('\\n', '\n')
        src = src.replace('\\n', '\n')
        src = src.replace('\\\n', '\\n')
        src = src.replace('\\\\', '\\')
        print(src)
        lex_result = lexer.run(src)
        results = []
        results.append("%s %s"%("Token".ljust(20),"Type"))
        for result in lex_result:
            result = str(result)
            # result.replace('\n','\\n')
            results.append(str(result))
        data = {'lex_result':results, 'code':1, 'msg':'词法分析成功!'}
        return jsonify(data)
    except Exception as e:
        data = {'code':0, 'msg':'词法分析失败, 可能存在语法错误', 'lex_result':str(e)}
        return jsonify(data)

@app.route('/getSyntaxMatch', methods = ['POST'])
def get_syntax_match():
    try:
        syntaxer = Syntaxer()
        req = request
        raw = req.data
        src = raw.decode('utf-8')
        src = src[1:len(src)-1]
        src = src.replace('\\t','\t')
        src = src.replace('\\"','\"')
        # src = src.replace('\\n', '\n')
        src = src.replace('\\n', '\n')
        src = src.replace('\\\n', '\\n')
        src = src.replace('\\\\', '\\')
        print(src)
        is_match = syntaxer.run(src)
        if is_match:
            result_info = '语法通过'
        else:
            result_info = '语法存在错误'
        data = {'result': result_info, 'code':1, 'msg':'语法分析成功!'}
        return jsonify(data)
    except Exception as e:
        data = {'code':0, 'msg':'语法分析失败, 可能存在语法错误', 'result':str(e)}
        return jsonify(data)
    

@app.after_request
def func_res(resp):
    res = make_response(resp)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res


if __name__ == "__main__":
    app.run('',10086,debug=True)
    # Serve the app with gevent
    print("Web Service running in http://localhost:10086/")
    http_server = WSGIServer(('0.0.0.0',10086), app)
    http_server.serve_forever()
