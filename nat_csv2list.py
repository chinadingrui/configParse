# --encoding=utf8--
import re

def nat_csv_to_list(csv_filename):
    rslt=[]
    pt_dash=re.compile(r'((?P<port>\d+)-(?P=port))') #匹配"端口1-端口1"
    pt_dash_ip=re.compile(r'((?P<ip>\d+\.\d+\.\d+\.\d+)-(?P=ip))') #匹配"ip1-ip1"
    with open(csv_filename,'r') as f:
        for line in f:
            # print line.decode('gbk','ignore')
            if len(line):
                #print isinstance(line,unicode)
                line = line.replace('","','"^"') #因为在端口字段也有逗号分割，所以先将字段之间的逗号分割符改为^
                #line = line.decode('gbk','ignore').replace('","','"^"')
                line = line.replace('"','') #去掉双引号
                #line = line.replace("TCP(0)to",'')
                #line = line.replace("UDP(0)to",'')
                line = re.sub(pt_dash_ip,'\g<ip>',line) # 一定要把ip匹配的放在端口匹配的前面，否则有可能会把10.20.24.191-10.20.24.191识别成端口
                line = re.sub(pt_dash,'\g<port>',line)
                #print line
                #line = line.replace('^(','^').replace(")^",'^')

                lst = line.decode('gbk','ignore').replace('","','"^"').split('^') #前面的部重要，重点在split
                rslt.append(lst)
                # for field in lst:
                #     print '\t:',field
    del rslt[0] #del title
    return rslt

if __name__ == "__main__":
    a = nat_csv_to_list('dnat_2016_9_7_13_4_3.csv')
    for i in a:
        for t in i:
            print t
