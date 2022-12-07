from flask import Flask, session, request, jsonify, abort
from flask.templating import render_template
from flask_cors import CORS
import hashlib, os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/isUpload", methods=['GET', 'POST'])
def isUpload():
    print("isupload")
    if request.method == 'POST':
        md5Val = request.form.get('md5')  # 获取文件的唯一标识符
        chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
        filename = '%s%s' % (md5Val, chunk)  # 构造该分片的唯一标识符
        print(request.form)
        upload_file = request.files['file']
        upload_file.save('./chunk/%s' % filename)  # 保存分片到本地
    return 'isUpload'


@app.route('/file/isExist', methods=['POST'])
def isExist():
    print("isexist")
    target_filename = request.form.get('filename')
    md5Val = request.form.get('md5')
    chunk = 0  # 分片序号
    print(target_filename)
    print(chunk)
    result = {}
    isFileExist = 'notExist'
    if os.path.exists('./uploadfile/%s' % target_filename):
        isFileExist = 'isExist'
    else:
        isFileExist = 'notExist'

    while True:
        try:
            filename = './chunk/%s%d' % (md5Val, chunk)
            if os.path.exists(filename) and os.path.getsize(filename):
                chunk += 1
            else:
                break
        except IOError as msg:
            break
    result['isFileExist'] = isFileExist
    result['chunk'] = chunk
    return result


@app.route('/file/merge', methods=['POST'])
def upload_success():  # 按序读出分片内容，并写入新文件
    print("merge")
    md5Val = request.form.get('md5')  # 获取文件的唯一标识符
    target_filename = request.form.get('filename')  # 获取该分片在所有分片中的序号
    chunk = 0  # 分片序号
    with open('./uploadfile/%s' % target_filename, 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = './chunk/%s%d' % (md5Val, chunk)
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            except IOError as msg:
                break

            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间

    return '文件上传成功!'


if __name__ == '__main__':
    app.run(debug=True)
