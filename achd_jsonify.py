from achd_datetools import achd_today
from glob import iglob
import subprocess
from sys import argv
from time import sleep
from os import environ

print(achd_today)
base_dir = environ.get('ACHD_Base_Remix')
dir_out=list(iglob(base_dir+"achd_remix/"+achd_today+"/*.pdf"))


def jython_process_pdf(base_dir=base_dir,document='doc'):
    "send a document to be processed by jython"
    #subprocess.run([base_dir+"graalvm-ce-java11-19.3.1/bin/java","-jar",
    subprocess.run([base_dir+"graalvm-ce-1.0.0-rc10/bin/java","-jar",
    base_dir+"jython/jython.jar",
    "-Dpython.path="+base_dir+"pdfbox-app-2.0.13.jar",
    base_dir+"achd_remix/achd_test.py",document]) 

#if __name__ == '__main__':
    #if argv[1]:
    #    jython_process_pdf(base_dir=base_dir,document=argv[1])
    #else:
#    for document in dir_out:
#        jython_process_pdf(base_dir=base_dir,document=document)
#        print(document + " jsonifyied")
#        sleep(2)
