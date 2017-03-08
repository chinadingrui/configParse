#--coding=utf8--
import logging    
import logging.config    
    
logging.config.fileConfig("logging.conf")    # 采用配置文件     
    
# create logger     
logger = logging.getLogger("WebSW")