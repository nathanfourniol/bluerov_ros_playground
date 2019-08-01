#!/usr/bin/env python

import threading
import time

class RecordThread(threading.Thread):
    def __init__(self,filename, recordtime, classtorecord, argtorecord ):

        """
        filename : to store data
        recordtime :
        argtorecord : list of str with the name of attr to record
        """
        threading.Thread.__init__(self)
        self.recordTime = recordtime
        self.filename = filename
        self.argToRecord = argtorecord
        self.classToRecord = classtorecord

    def run(self):
        f = open(self.filename,'w')
        t0 = time.time()
        while time.time()-t0<self.recordTime :
            print(time.time()-t0)
            buf = "{}, ".format(time.time()-t0)
            for i in self.argToRecord:
                buf = buf + "{}, ".format(getattr(self.classToRecord, i))
            f.write(buf+"\n")
            time.sleep(0.1)
        f.close()


































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































