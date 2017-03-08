#--coding=utf8--
from sw6 import Switch,SW52,SW59,SW89
from ConfigParser import ConfigParser
from multiprocessing import Pool
from logger import logger
from nat_csv2list import nat_csv_to_list
import pdb
import os

def getMac(sw):
    if not sw.enable():
        logger.error("IP : %s, SW not enabled while getting mac" % sw.ip)
        return []
    return sw.get_mac()

def getArp(sw):
    #pdb.set_trace()
    if not sw.enable():
        return []
    logger.info("Collecting Arp of %s",sw.ip)
    return sw.get_arp()

def filter_mac_vlan1000(macs):
    new_macs=[]
    for mac in macs:
        if mac[2] != '1000':
           new_macs.append(mac)
    return new_macs

class DataCenter(object):
    sws=[]
    macs=[]
    arps=[]
    nats=[]

    def __init__(self,config_file="pass.conf"):
        conf = ConfigParser()
        conf.read(config_file)
        #logger.info(u"Reading Config File...")
        for it in conf.sections():
            model = conf.get(it,"model")
            if model == "5250":
                self.sws.append(SW52(it,22,'admin',conf.get(it,"login_pass"),conf.get(it,"en_pass"),model,layer=conf.get(it,"layer")))
            elif model == "5928E":
                self.sws.append(SW59(it,22,'admin',conf.get(it,"login_pass"),conf.get(it,"en_pass"),model,layer=conf.get(it,"layer")))
            elif model == "8912E":
                self.sws.append(SW89(it,22,'admin',conf.get(it,"login_pass"),conf.get(it,"en_pass"),model,layer=conf.get(it,"layer")))



    def getMacTab(self):
        pool=Pool(len(self.sws))
        r=pool.map(getMac,self.sws)
        pool.close()
        pool.join()
        g_mac_table=[]
        for tab in r:
            g_mac_table+=tab
            #print tab
        g_mac_table = filter_mac_vlan1000(g_mac_table)
        self.macs=g_mac_table
        return True

    def getArpTab(self):
        pool=Pool(len(self.sws))
        r=pool.map(getArp,self.sws)
        pool.close()
        pool.join()
        #pdb.set_trace()
        g_arp_table=[]
        for tab in r:
            g_arp_table+=tab
            #print tab
        self.arps=g_arp_table
        return True

    def getNATTab(self,fullPath):
        # from csv import nat table ,convert to list nats
        try:
            print fullPath
            self.nats = nat_csv_to_list(fullPath)
        except:
            print "ERROR Reading NAT File"

        return True

    def getArpKW(self,kw):
        # 通过关键字查找arp表项中的内荣
        rslt=[]

        for arp in self.arps:
            for field in arp:
                if kw.lower() in field.lower():
                    rslt.append(arp)
                    break
        return rslt

    def getMacKW(self,kw):
        # 通过关键字查找mac表项中的内荣
        rslt=[]

        for mac in self.macs:
            for field in mac:
                if kw.lower() in field.lower():
                    rslt.append(mac)
                    break
        return rslt

    def getNATKW(self,kw):
        # 通过关键字查找mac表项中的内荣
        rslt=[]

        for nat in self.nats:
            for field in nat:
                if kw.lower() in field.lower():
                    rslt.append(nat)
                    break
        return rslt
    def getMacTabA(self):#for test
        self.macs = [
        ['192.168.100.253', '286e.d488.c675', '3766', 'gei_1/23'],
        ['192.168.100.253', '286e.d488.c673', '3766', 'gei_1/23'],
        ['192.168.100.253', '286e.d488.c671', '3766', 'gei_1/23'],
        ['192.168.100.253', '6c92.bf0f.caa8', '3761', 'gei_1/23'],
        ['192.168.100.253', '286e.d488.c679', '3766', 'gei_1/20'],
        ['192.168.100.253', '286e.d488.c66d', '3761', 'gei_1/23'],
        ['192.168.100.253', '286e.d488.c66e', '3761', 'gei_1/23'],
        ['192.168.100.253', '286e.d488.c66c', '3761', 'gei_1/20'],
        ['192.168.100.253', '286e.d488.c674', '3766', 'gei_1/23'],
        ['192.168.100.253', '286e.d488.c672', '3766', 'gei_1/20'],
        ['192.168.100.253', '286e.d488.c667', '3761', 'gei_1/23'],
        ['192.168.100.253', '286e.d488.c67b', '3766', 'gei_1/20'],
        ['192.168.100.253', '286e.d488.c676', '3766', 'gei_1/23']
        ]
        return True
    def getArpTabA(self):#for test
        self.arps = [
        ['192.168.100.1', '172.18.12.128', '0050.56ba.a529', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.127', '0050.568f.6409', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.124', '0050.568f.031b', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.130', '0050.568f.29e8', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.120', '0050.568f.0876', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.198', '0050.5697.11c1', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.70', '0050.568f.5cc1', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.139', '0050.56ba.612a', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.75', '0050.568f.6ddf', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.199', '0050.568f.0ad1', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.23', '0050.568f.0d30', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.12', '0050.568f.0e2c', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.205', '0050.568f.2f02', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.143', '0050.56ba.0c8c', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.73', '000c.29de.43a8', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.126', '0050.568f.0bd5', 'vlan996', '996', 'smartgroup22'],
        ['192.168.100.1', '172.18.12.13', '0050.568f.4d34', 'vlan996', '996', 'smartgroup22']
        ]
        return True

if __name__ == "__main__":
  dc=DataCenter()
  #print dc.sws
  dc.getMacTabA()
  dc.getArpTabA()
#  dc.getNATTab()
  print "*" * 80
  for mac in dc.macs:
    print mac
  for arp in dc.arps:
    print arp
