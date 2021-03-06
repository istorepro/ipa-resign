# coding=utf-8 

import zipfile
import shutil
import sys, os
import platform
import json
import commands

####################
# 是否windows
def isWindows():
    return 'Windows' in platform.system()

####################
# zip压缩
def zip_dir(dirname,zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
         
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)
    zf.close()
    return

####################
# zip解压
def unzip(src,des): 
    if isipa(src):
        status, output = commands.getstatusoutput("unzip " + src + " -d " + des)
    elif isapk(src):
        zfile = zipfile.ZipFile(src,'r')
        for filename in zfile.namelist() :
            zfile.extract(filename,des)
    return

####################
# 高亮输出
SYS_ENCODE = sys.getfilesystemencoding()
def print_red(msg):
    msg = 'error: ' + msg
    printlog(msg)
    msg = msg.decode('utf-8').encode(SYS_ENCODE)
    if isWindows():
        print msg
    else:
        print '\033[0;31m', msg, '\033[0m'
    return

####################
def print_green(msg):
    printlog(msg)
    msg = msg.decode('utf-8').encode(SYS_ENCODE)
    if isWindows():
        print msg
    else:
        print '\033[0;32m', msg, '\033[0m'
    return

####################
# 输出log
def printlog(msg):
    LOG_FILE = os.path.join(os.getcwd(), 'resign.log')
    msg = msg + '\n'
    fp = open(LOG_FILE, 'a')
    fp.write(msg)
    fp.close

####################
# 是否apk
def isapk(filename):
    return 'apk' in filename.split('.')[-1]

####################
# 是否ipa
def isipa(filename):
    return 'ipa' in filename.split('.')[-1]

####################
# 是否APP
def isapp(filename):
    return 'app' in filename.split('.')[-1]

####################
# 重命名
def newname(prefex, oldname):
    index=oldname.rindex('.')
    oldpath = os.path.split(oldname)[0]
    filename = prefex + oldname[index:] 
    return  os.path.join(oldpath, filename)

####################
# 查找config文件
def findconfig(dirname):
    for root, dirs, files in os.walk(dirname):
        for name in files:
            if 'config.json' == name:
                return os.path.join(root, name)
    
    print_red('安装包'+ dirname + '中' +'检索config.json文件失败')
    sys.exit(0)

####################
# 删除文件夹
def removeDir(dirname):
    shutil.rmtree(dirname, True)
    # if isWindows():
    #     os.system("rd /s /q " + dirname)
    # else:
    #     os.system("rm -rf " + dirname)

####################
# 清理作案现场
def restoreENV(UNPACK_DIR):
    print_green('清理临时文件...')
    removeDir(UNPACK_DIR)

####################
# 向json文件中写入指定字段
def writeJson(filename, parname, value):
    if os.path.isfile(filename):
        fp = open(filename, 'r')
        filestr = fp.read()
        fp.close

        dictstr = json.loads(filestr)
        dictstr[parname] = value
        filestr = json.dumps(dictstr, ensure_ascii=False)

        fp = open(filename, 'w')
        fp.write(filestr)
        fp.close()
        return 
    else:
        print_red('文件' + filename + '不存在!')

####################
# 签名apk
def signapk(packname, APK_KEY, APK_PASS, APK_ALIAS, PACK_NEW):
    execstr = "jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore " + APK_KEY + " -storepass " + APK_PASS + " " + PACK_NEW + " " + APK_ALIAS
    status = os.system(execstr)
    if status == 0:
        print_green('签名成功！')
        print_green(packname)
    else:
        print_red('签名失败！')
        print_red('删除失败的签名包...')
        sys.remove(packname)

####################
# 签名ipa
def signipa(packname, IPA_CER, IPA_ENT, IPA_APP):
    execstr = "/usr/bin/codesign -f -s \"" + IPA_CER + "\" --entitlements " + IPA_ENT + " " + IPA_APP
    os.system(execstr)
    print_green(execstr)
    print_green('签名完成！')
    execstr = "/usr/bin/codesign --verify " + IPA_APP
    print_green(execstr)
    print_green('验证签名完成！')

####################
# 获取父目录
def getpardir(path):
    newpath = os.path.abspath(path)
    index = newpath.rindex('/')
    return newpath[:index]

####################
# main
####################
def main():
    # 运行环境默认编码ascii，当写入中文到文件时会因无法编码而出错
    reload(sys)
    sys.setdefaultencoding('utf-8')

    ####################
    # 参数解析
    if len(sys.argv) < 2:
        print_red('参数错误')
        print_green('eg. python resign.py 2333 d:/redbird.apk')
        sys.exit(1)

    ROOT_PATH = os.path.abspath(sys.path[0])

    # 代理商id
    AGENT_ID = sys.argv[1]

    # 母包 - 包含默认值
    PACK_ORIGIN = os.path.join(getpardir(ROOT_PATH), 'download/zhixin.ipa')
    print_green(sys.path[0])

    if len(sys.argv) > 2:
        PACK_ORIGIN = sys.argv[2]

    # 签名包名
    PACK_NEW = newname(AGENT_ID, PACK_ORIGIN)

    ####################
    # 签名参数

    # apk签名
    APK_KEY = os.path.join(ROOT_PATH, 'customer-hn787878-20160315.keystore')
    APK_ALIAS = 'customer'
    APK_PASS = 'hn787878'

    # ipa签名
    IPA_PROV = os.path.join(ROOT_PATH, 'embedded.mobileprovision')
    IPA_CER = 'iPhone Distribution: Beijing TianRuiDiAn Network Technology Co,Ltd.'
    IPA_ENT = os.path.join(ROOT_PATH, 'Entitlements.plist')
    IPA_APP = 'MixProject-mobile.app'

    ####################
    # 日志
    index=PACK_NEW.rindex('.')
    LOG_FILE = PACK_NEW[:index] + '.log'

    ####################
    # 检索母包
    if not os.path.exists(PACK_ORIGIN):
        print_red(PACK_ORIGIN + '母包文件检索失败！')
        sys.exit(1)

    ####################
    # 解压目录
    UNPACK_DIR = PACK_NEW[:PACK_NEW.rindex('.')]
    print_green('解包中...')
    print_green(PACK_ORIGIN)

    if os.path.exists(UNPACK_DIR):
        removeDir(UNPACK_DIR)

    unzip(PACK_ORIGIN, UNPACK_DIR)

    print_green('成功解压到: ')
    print_green(UNPACK_DIR)

    ####################
    # 检查签名
    print_green('检查签名...')

    if isapk(PACK_ORIGIN):
        if not os.path.exists(APK_KEY):
            print_red('签名文件检索失败:')
            print_red(APK_KEY)
            sys.exit(0)
        else:
            print_green('找到签名文件：')
            print_green(APK_KEY)

    elif isipa(PACK_ORIGIN):
        # ipa签名只能在mac上执行
        if isWindows():
            print_red('ipa包重签名只能在mac上进行')
            sys.exit(0)

        if not os.path.exists(IPA_PROV):
            print_red('签名文件检索失败:')
            print_red(IPA_PROV)
            sys.exit(0)
        else:
            print_green('找到签名文件：')
            print_green(IPA_PROV)

        if not os.path.exists(IPA_ENT):
            print_red('签名文件检索失败:')
            print_red(IPA_ENT)
            sys.exit(0)
        else:
            print_green('找到签名文件：')
            print_green(IPA_ENT)

        for root, dirs, files in os.walk(UNPACK_DIR):
            for dirname in dirs:
                if isapp(dirname):
                    print_green('找到APP文件:')
                    IPA_APP = os.path.join(root, dirname)
                    print_green(IPA_APP)
        
        if not os.path.exists(IPA_APP):
            print_red('检索APP文件失败！')
            print_red(IPA_APP)
            sys.exit(0)

    ####################
    # 查找配置文件
    print_green('定位config.json文件...')
    CONFIG_FILE = findconfig(UNPACK_DIR)
    print_green('找到配置文件: ')
    print_green(CONFIG_FILE)

    ####################
    # 写入代理商字段
    print_green('写入代理商字段...')
    writeJson(CONFIG_FILE, 'agent', AGENT_ID)

    ####################
    # 删除旧签名
    print_green('删除签名...')

    # 安卓apk
    if isapk(PACK_ORIGIN):
        for root, dirs, files in os.walk(UNPACK_DIR):
            for dirname in dirs:
                if dirname=='META-INF':
                    fulldir = os.path.join(root, dirname)
                    print_green(fulldir)
                    removeDir(fulldir)
                    print_green('签名删除成功！')
    
    # iOS ipa
    elif isipa(PACK_ORIGIN):
        for root, dirs, files in os.walk(UNPACK_DIR):
            for dirname in dirs:
                if dirname == '_CodeSignature':
                    fulldir = os.path.join(root, dirname)
                    print_green(fulldir)
                    removeDir(fulldir)
                    print_green('签名删除成功！')

            for filename in files:
                if filename == 'embedded.mobileprovision':
                    filename = os.path.join(root, filename)
                    print_green('替换PROV文件：')
                    print_green(filename)
                    os.system("cp " + IPA_PROV + " " + filename)
                    print_green('替换PROV成功！')

    ####################
    # 安卓重签名
    if isapk(PACK_ORIGIN):
        # 压缩
        print_green('重新打包中...')
        zip_dir(UNPACK_DIR, PACK_NEW)
        print_green(PACK_NEW)
        # 签名
        print_green('重新签名中...')
        signapk(PACK_NEW, APK_KEY, APK_PASS, APK_ALIAS, PACK_NEW)

    ####################
    # iOS重签名
    elif isipa(PACK_ORIGIN):
        # 签名
        print_green('重新签名中...')
        signipa(PACK_NEW, IPA_CER, IPA_ENT, IPA_APP)

        # 压缩
        print_green('重新打包中...')
        print_green(UNPACK_DIR)

        # 更改执行路径
        tmpdir = os.getcwd()
        os.chdir(UNPACK_DIR)

        # zipdir
        zip_dir(UNPACK_DIR, PACK_NEW)

        # 恢复执行路径
        os.chdir(tmpdir)

        print_green('打包成功：')
        print_green(PACK_NEW)

    # 清理作案现场
    restoreENV(UNPACK_DIR)

if __name__ == '__main__':
    main()

