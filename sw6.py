# --coding=utf8--
"""
Class Switch

This version add get_arp()
"""
import paramiko
import time
import re
import traceback
from logger import logger


class ChannelError(IOError):
    pass


class MacRecord(object):
    def __init__(self, ip, mac, vlan, interface):
        self.ip=ip
        self.mac=mac
        self.vlan=vlan
        self.interface=interface


class Switch(object):
    """
    交换机的通用类
    """

    def __init__(self, ip, port, username, password, enpass, model="5250", layer=3):
        self.ip=ip
        self.port=port
        self.username=username
        self.password=password
        self.enpass=enpass
        self.ssh=False
        self.channels=[]
        self.model=model
        self.debug=False
        self.layer = layer # OSI模型的层数，指代2层交换机或者3层交换机
        logger.info("object created for ip : %s" % (self.ip))

    def __iter__(self):
        return self

    def connect(self):
        """
        connect to device via ssh, and return ssh client object
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.ip, self.port, self.username, self.password, look_for_keys=False, allow_agent=False)
            return True
        except Exception, e:
            logger.error("IP: %s, Connect Error %s: " % (self.ip, e))
            # traceback.print_exc()
            raise

    def newChannel(self):
        self.channels.append(self.ssh.invoke_shell())

    def setDebug(self, dbg="True"):
        self.debug = dbg
        if self.debug:
                logger.debug("debug on")
        else:
                logger.debug("debug off")
        return self.debug

    def read(self, chid=0):
        txt = ""
        if self.debug:
                print "[DEBUG]read"
        tCheck = 0
        while not self.channels[chid].recv_ready():
                time.sleep(0.3)
                if tCheck >= 10:
                    print "send time out"
                    return ""
        txt += self.channels[chid].recv(1024*64)
        if self.debug:
                print "[DEBUG]read : ", repr(txt)
        return txt

    def write(self, str='\n', chid=0, debug=False):
        if self.debug:
                print "[DEBUG]write"
        tCheck = 0
        while not self.channels[chid].send_ready():
                time.sleep(0.2)
                tCheck += 1
                if tCheck >= 10:
                    print "send time out"
                    return 0
        self.channels[chid].send(str)
        return len(str)

    def close(self):
        self.ssh.close()
        print self.ip, " Closed."

    def run(self, cmd="\n"):
        rslt = ""
        if not self.ssh or len(self.channels) == 0 or self.channels[0].closed:
            raise ChannelError  # 未建立Channel
        self.write(cmd+"\n")
        rslt += self.read()
        #  此处为了解决more的问题，解决办法是输入空格，但是还是有\b退格进入
        while not rslt.rstrip().endswith('#'):
                # print '.',
                self.write(" ")
                rslt += self.read()

        logger.info("Finished Run Cmd %s" % cmd)

        return rslt

    def enable(self):
        if not len(self.channels) or self.channels[0].closed:
            try:
                self.connect()
            except Exception, e:
                logger.error("IP : %s, Terminal Enable CMD Error: %s" % (self.ip, e))
                return False
        logger.info("%s Connected..." % self.ip)
        if len(self.channels) > 0 and self.channels[0].closed:
            del self.channels[0]
        if len(self.channels) == 0:
            self.newChannel()
        else:
            return True
        logger.info("[%s]Channel built..." % self.ip)
        self.channels[0].resize_pty(width=180,
                                    height=1024,
                                    width_pixels=0,
                                    height_pixels=0)
        logger.info("[%s]:%s" % (self.ip, self.read()))
        self.write("en\n")
        logger.info("[%s]:%s" % (self.ip, self.read()))
        self.write(self.enpass+'\n')
        r = self.read()
        logger.info("[%s]:%s" % (self.ip, r.strip()))
        return (True if r.strip().endswith("#") else False)

    def get_mac(self):
        pass

    def get_arp(self):
        pass

    def get_datetime(self):
        pass
class SW59(Switch):
    def get_mac(self):
        #  样式如下
        #  "MAC_Address    vid  vpn        port  per stc toS wtn srF dsF Frm     Time"
        #  "6c92.bf0f.ca60  3761    0      gei_1/22 0   0   0   0   0   0   0     0:00:51:48"

        if not len(self.channels) or self.channels[0].closed:
            logger.error("IP : %s, No Channel to Use !" % self.ip)
            return []
        logger.info("Getting mac on sw %s"%self.ip)
        raw_mac = self.run("show mac")
        re_mac_59 = re.compile('(\w{4}\.\w{4}\.\w{4})\s+(\d{1,4})\s+\d+\s+(\S+)')
        mac_match = re_mac_59.findall(raw_mac)
        #logger.info(raw_mac)
        #logger.info(mac_match)
        logger.info("Finished getting mac on sw %s"%self.ip)
        return [[self.ip, row[0], row[1], row[2]] for row in mac_match]

    def get_arp(self):
        if not len(self.channels) or self.channels[0].closed:
            logger.error("IP : %s, No Channel to Use !" % self.ip)
            return []
        raw_arp= self.run("show arp")
        arp_list=[]
        logger.info("Getting arp on sw %s"%self.ip)

        for line in raw_arp.split("\r\n"):
            list_line=line.split()
            if re.match(r'\d+\.\d+\.\d+\.\d+', list_line[0]):
                arp_list.append([self.ip, list_line[0], list_line[2], list_line[3], list_line[4], list_line[6]])

        logger.info("Finished Getting arp on sw %s"%self.ip)

        return arp_list

    def get_datetime(self):
        if not len(self.channels) or self.channels[0].closed:
            logger.error("IP : %s, No Channel to Use !" % self.ip)
            return []
    	return self.run("show clock")
class SW52(Switch):
    def get_mac(self):
        #样式如下
        #"MAC-Address  Vlan-Id   Port    Per Stc ToP ToS Sav SrF DsF Frm      Time"
        #"4c09.b4f9.c33d  1000   trunk-1    0   0   0   0  -    0   0   0    00:00:06:00"
        if not len(self.channels) or self.channels[0].closed:
            logger.error("IP : %s, No Channel to Use !" % self.ip)
            return []
        logger.info("Getting mac on sw %s"%self.ip)
        raw_mac = self.run("show mac")
        re_mac_52 = re.compile('(\w{4}\.\w{4}\.\w{4})\s+(\d{, 4})\s+(\S+)')
        mac_match=re_mac_52.findall(raw_mac)
        logger.info("Finished getting mac on sw %s"%self.ip)
        return [[self.ip, row[0], row[1], row[2]] for row in mac_match]

    def get_arp(self):
        return []

    def get_datetime(self):
        if not len(self.channels) or self.channels[0].closed:
            logger.error("IP : %s, No Channel to Use !" % self.ip)
            return []
        return self.run("show date-time")


class SW89(Switch):
    def get_mac(self):
        # "MAC_ADDRESS     VID   PORT                 PER  ST  TS  SF  DF  FRM  TIME"
        # "6c92.bf0f.ca89  3510  smartgroup12         0    0   0   0   0   0    00:00:01:01"
        if not len(self.channels) or self.channels[0].closed:
            logger.error("IP : %s, No Channel to Use !" % self.ip)
            return []
        logger.info("get mac on sw %s"%self.ip)
        raw_mac = self.run("show mac table")
        re_mac_89 = re.compile('(\w{4}\.\w{4}\.\w{4})\s+(\d{, 4})\s+(\S+)')
        mac_match=re_mac_89.findall(raw_mac)
        return [[self.ip, row[0], row[1], row[2]] for row in mac_match]

    def get_arp(self):
        # "IP                       Hardware                    Exter  Inter  Sub
        # Address         Age      Address        Interface    VlanID VlanID Interface"
        # 172.18.11.2     00:08:22 000b.abf0.b8be vlan997      997    N/A    gei-0/6/0/20
        # 10.40.0.13      03:13:24 286e.d488.c640 supervlan399 3761   N/A    smartgroup2
        #                                          2
        # 这个解析还是比较麻烦的，由于有换行，调整vty size也没有办法
        # 还有一个是more的存在，将退格符也带入了，所以先替换退格符和more
        if not len(self.channels) or self.channels[0].closed:
            logger.error("IP : %s, No Channel to Use !" % self.ip)
            return []
        raw_arp= self.run("show arp")
        raw_arp=raw_arp.replace('\b', '')
        raw_arp=raw_arp.replace(" --More--         ", "")
        arp_list=[]

        logger.info("get arp on sw %s"%self.ip)
        logger.info("Getting arp on sw %s"%self.ip)

        for line in raw_arp.split("\r\n"):
            list_line=line.split()
            if re.match(r'\d+\.\d+\.\d+\.\d+', list_line[0]):  #匹配记录
                arp_list.append([self.ip, list_line[0], list_line[2], list_line[3], list_line[4], list_line[6]])
            elif list_line[0].isdigit():   #如果是纯数字，则拼接到前一行interface的后面
                arp_list[-1][3] = arp_list[-1][3]+list_line[0]

        logger.info("Finished Getting arp on sw %s"%self.ip)
        return arp_list

    def get_datetime(self):

        if not len(self.channels) or self.channels[0].closed:
            logger.error("IP : %s, No Channel to Use !" % self.ip)
            return []
        return self.run("show clock detail")
