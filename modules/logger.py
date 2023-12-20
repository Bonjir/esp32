import utime

LOG_FILE = 'log.txt'

# def init():
#     global flog
#     flog = open(LOG_FILE, "a+")
#     info("Log Start.")

def print_only(inf):
    y, m, d, h, mn, s, _, _ = utime.localtime()
    infostr = "{y:04}-{m:02}-{d:02} {h:02}:{mn:02}:{s:02}\tPRINT\t: {inf}\n".format(y=y, m=m, d=d, h=h, mn=mn, s=s, inf=inf)
    print(infostr.strip())

def info(inf):
    flog = open(LOG_FILE, "a+")
    y, m, d, h, mn, s, _, _ = utime.localtime()
    infostr = "{y:04}-{m:02}-{d:02} {h:02}:{mn:02}:{s:02}\tINFO\t: {inf}\n".format(y=y, m=m, d=d, h=h, mn=mn, s=s, inf=inf)
    flog.write(infostr)
    print(infostr.strip())
    flog.close()
    
def error(err):
    flog = open(LOG_FILE, "a+")
    y, m, d, h, mn, s, _, _ = utime.localtime()
    errstr = "{y:04}-{m:02}-{d:02} {h:02}:{mn:02}:{s:02}\tERROR\t: {err}\n".format(y=y, m=m, d=d, h=h, mn=mn, s=s, err=err)
    flog.write(errstr)
    print(errstr.strip())
    flog.close()
    
def critical(err):
    flog = open(LOG_FILE, "a+")
    y, m, d, h, mn, s, _, _ = utime.localtime()
    cristr = "{y:04}-{m:02}-{d:02} {h:02}:{mn:02}:{s:02}\tCRITICAL\t: {err}\n".format(y=y, m=m, d=d, h=h, mn=mn, s=s, err=err)
    flog.write(cristr)
    print(cristr.strip())
    flog.close()
    
