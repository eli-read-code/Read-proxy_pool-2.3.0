import logging

# 1、创建一个logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

# 2、创建一个handler，用于写入日志文件
fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG) # 日志记录级别,最低 DEBUG+INFO+ERROR
# fh.setLevel(logging.INFO) # 日志记录级别,中 INFO+ERROR
# fh.setLevel(logging.ERROR) # 日志记录级别,最高 ERROR


# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 3、定义handler的输出格式（formatter）
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 4、给handler添加formatter
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 5、给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)

logger.info("info")
logger.debug("debug")
logger.error("error")