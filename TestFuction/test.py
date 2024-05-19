# Python 代码示例：查询汉字“我”在GB2312中的编码
char = '代'
encoded_char = char.encode('gb2312')
print('GB2312编码为:', encoded_char.hex().upper())
