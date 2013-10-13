import os, sys, string, subprocess, distutils.util, check_install, site, glob

user_home = os.environ["HOME"]
print "<<Welcome to metAMOS install>>"

#check for python version
if (sys.version_info[0] < 2) or (sys.version_info[0] == 2 and sys.version_info[1] < 6):
  print "Python version is %s. metAMOS requires at least 2.6"%(sys.version)
  sys.exit(1)

#add access to utils.py, for utils dir
METAMOS_ROOT  = os.getcwd().strip()
INITIAL_SRC   = "%s%ssrc"%(METAMOS_ROOT, os.sep)
sys.path.append(INITIAL_SRC)
import utils
import workflow
sys.path.append(utils.INITIAL_UTILS)

shellv = os.environ["SHELL"]

#add site dir
site.addsitedir(utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"+os.sep+"python")
site.addsitedir(utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"+os.sep+"python")

if "PYTHONPATH" not in os.environ:
   os.environ["PYTHONPATH"] = ""
os.environ["PYTHONPATH"]+=utils.INITIAL_UTILS+os.sep+"python"+os.pathsep
os.environ["PYTHONPATH"] += utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"+os.pathsep
os.environ["PYTHONPATH"] += utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"+os.sep+"python"+os.pathsep
os.environ["PYTHONPATH"] += utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"+os.pathsep
os.environ["PYTHONPATH"] += utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"+os.sep+"python"+os.pathsep
sys.path.append(utils.INITIAL_UTILS+os.sep+"python")
sys.path.append(utils.INITIAL_UTILS+os.sep+"python" + os.sep+"lib"+ os.sep+"python")
sys.path.append(utils.INITIAL_UTILS+os.sep+"python" + os.sep+"lib64"+ os.sep+"python")

if 'bash' in shellv or utils.cmdExists('export'):
   os.system("export PYTHONPATH=%s:$PYTHONPATH"%(utils.INITIAL_UTILS+os.sep+"python"))
   os.system("export PYTHONPATH=%s:$PYTHONPATH"%(utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"+os.sep+"python"))
   os.system("export PYTHONPATH=%s:$PYTHONPATH"%(utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"+os.sep+"python"))
elif utils.cmdExists('setenv'):
   os.system("setenv PYTHONPATH %s:$PYTHONPATH"%(utils.INITIAL_UTILS+os.sep+"python"))
   os.system("setenv PYTHONPATH %s:$PYTHONPATH"%(utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"+os.sep+"python"))
   os.system("setenv PYTHONPATH %s:$PYTHONPATH"%(utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"+os.sep+"python"))
else:
   print "Cannot set PYTHONPATH variable, unknown shell %s\n"%(shellv)

if not os.path.exists("%s"%utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"):
    os.system("mkdir %s"%utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib")
if not os.path.exists("%s"%utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"):
    os.system("mkdir %s"%utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64")
if not os.path.exists("%s"%utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"+os.sep+"python"):
    os.system("mkdir %s"%utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"+os.sep+"python")
if not os.path.exists("%s"%utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"+os.sep+"python"):
    os.system("mkdir %s"%utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"+os.sep+"python")

ALLOW_FAST=True
HAVE_RT=False
HAVE_QUIET_HEAD=False

OSTYPE="Linux"
OSVERSION="1"
MACHINETYPE="x86_64"
kronaTools = "KronaTools-2.2"

#identify machine type
p = subprocess.Popen("echo `uname`", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(checkStdout, checkStderr) = p.communicate()
if checkStderr != "":
   print "Warning: Cannot determine OS, defaulting to %s"%(OSTYPE)
else:
    OSTYPE = checkStdout.strip()

p = subprocess.Popen("echo `uname -r`", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(checkStdout, checkStderr) = p.communicate()
if checkStderr != "":
   print "Warning: Cannot determine OS version, defaulting to %s"%(OSVERSION)
else:
   OSVERSION = checkStdout.strip()

p = subprocess.Popen("echo `uname -m`", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(checkStdout, checkStderr) = p.communicate()
if checkStderr != "":
   print "Warning: Cannot determine system type, defaulting to %s"%(MACHINETYPE)
else:
   MACHINETYPE = checkStdout.strip()

if OSTYPE == "Darwin":
   p = subprocess.Popen("echo `gcc --version`", shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   (checkStdout, checkStderr) = p.communicate()
   if "Apple" not in checkStdout:
      ALLOW_FAST=False

libPaths = [ "/usr/lib", "/usr/lib64", "/usr/local/lib/", "/usr/local/lib64/", "/opt/local/lib/", "/opt/local/lib64/"] 
for libPath in libPaths:
   if os.path.exists(libPath + os.sep + "librt.a") or os.path.exists(libPath + os.sep + "librt.so"):
      HAVE_RT=True
      break

p = utils.getCommandOutput("head --help |grep \"\\-q\" |wc -l", False)
if int(p) >= 1:
   HAVE_QUIET_HEAD=True

# get list of supported workflows
enabledWorkflows = set()
packagesToInstall = set()
knownPackages = set()
workflows = workflow.getAllWorkflows("%s/Utilities/workflows"%(METAMOS_ROOT))
for flow in workflows:
   knownPackages.update(workflows[flow].programList)

manual = False
fail = False

if (len(sys.argv) > 1):
  # should support tool list as well added
  for i in range(1, len(sys.argv)):
      arg = sys.argv[i]
      if arg.lower() in workflows.keys():
         packagesToInstall.update(workflows[arg.lower()].programList)
         enabledWorkflows.update(workflows[arg.lower()].getDerivedName())
      elif arg.lower() == "full":
         for flow in workflows:
             packagesToInstall.update(workflows[flow].programList)
             enabledWorkflows.update(workflows[flow].getDerivedName())
         print "Installing all available workflows"
      elif arg.lower() == "manual":
        manual = True
        for flow in workflows:
           enabledWorkflows.update(workflows[flow].getDerivedName())
      elif arg.lower() in knownPackages:
         packagesToInstall.add(arg.lower())
         for flow in workflows:
            if arg.lower() in workflows[flow].programList:
               enabledWorkflows.update(workflows[flow].getDerivedName())
               break
      else:
         if arg != "help":
            print "Unknown program or workflow %s specified."%(arg)
         fail = True
else:
    availableWf = workflow.getSupportedWorkflows("%s/Utilities/workflows"%(METAMOS_ROOT), False)
    for wf in availableWf:
       enabledWorkflows.update(wf.getDerivedName())
       packagesToInstall.update(wf.programList)

    print "Installing %s metAMOS workflow"%(",".join(enabledWorkflows))

if fail or help in sys.argv:
   print "Available workflows: %s"%(" ".join(workflows.keys()))
   print "Available packages: %s"%("\n\t".join(knownPackages))
   exit(1)
    
if manual:
    packagesToInstall = set()

for workflowName in enabledWorkflows:
    print "Selected to install workflowName: %s."%(workflowName.upper())

print "Will automatically install:"
for p in packagesToInstall:
    print "\t%s"%(p.title())

if not os.path.exists("./Utilities/config/usage.ok") and not os.path.exists("./Utilities/config/usage.no"):
    print "MetAMOS would like to record anonymous usage statistics, is this ok ? "
    dl = raw_input("Enter Y/N: ")
    if dl == 'y' or dl == 'Y':
        os.system("echo ok > ./Utilities/config/usage.ok")
    else:
        os.system("echo no > ./Utilities/config/usage.no")

# first the needed python packages
# make sure we have setuptools available
if 1:
   fail = 0
   try:
       import setuptools
   except ImportError:
       fail = 1
   if "setuptools" in packagesToInstall:
       dl = 'y'
   elif fail:
       print "setuptools not found, required for install, download now?"
       dl = raw_input("Enter Y/N: ")
   if fail and (dl == 'y' or dl == "Y"):
       os.system("curl -L https://bitbucket.org/pypa/setuptools/raw/0.7.4/ez_setup.py -o ez_setup.py")
       os.system("python ez_setup.py --user")
       
if 1:
   fail = 0
   try:
       import psutil
   except ImportError:
       fail = 1
   if "psutil" in packagesToInstall:
       dl = 'y'
   elif fail:
       print "psutil not found, required for memory usage estimation, download now?"
       dl = raw_input("Enter Y/N: ")
   if fail and (dl == 'y' or dl == "Y"):
       os.system("curl -L http://psutil.googlecode.com/files/psutil-0.6.1.tar.gz -o ./psutil.tar.gz")
       os.system("tar -C ./Utilities/python -xvf psutil.tar.gz")
       os.system("mv ./Utilities/python/psutil-0.6.1 ./Utilities/python/psutil")
       os.chdir("./Utilities/python/psutil")
       os.system("python setup.py install --home=%spython"%(utils.INITIAL_UTILS+os.sep))
       os.chdir("%s"%(METAMOS_ROOT))
       os.system("rm -rf psutil.tar.gz")
if 1:
   fail = 0
   try:
       import cython
   except ImportError:
       fail = 1
   if "cython" in packagesToInstall:
       dl = 'y'
   elif fail:
       print "cython modules not found, necessary for c-compiling python code, download now?"
       dl = raw_input("Enter Y/N: ")
   if fail and (dl == 'y' or dl == "Y"):
       os.system("curl -L https://github.com/cython/cython/archive/master.zip -o ./cython.zip")
       os.system("unzip ./cython.zip")
       os.system("mv ./cython-master ./Utilities/python/cython")
       os.chdir("./Utilities/python/cython")
       os.system("python setup.py install --home=%spython"%(utils.INITIAL_UTILS+os.sep))
       os.chdir(METAMOS_ROOT)
       os.system("rm -rf cython.zip")

if 1:
   fail = 0
   try:
       import pysam
   except ImportError:
       fail = 1

   if "pysam" in packagesToInstall:
       dl = 'y'
   elif fail:
       print "pysam python modules not found, necessary for bowtie2 alignments, download now?"
       dl = raw_input("Enter Y/N: ")

   if fail and (dl == 'y' or dl == "Y"):
       os.system("curl -L http://pysam.googlecode.com/files/pysam-0.6.tar.gz -o ./pysam.tar.gz")
       os.system("tar -C ./Utilities/python -xvf pysam.tar.gz")
       os.system("mv ./Utilities/python/pysam-0.6 ./Utilities/python/pysam")
       doInstall = True
       #for root install
       #os.system("sudo python ./Utilities/python/pysam/setup.py install")
       os.chdir("./Utilities/python/pysam")
       if OSTYPE == "Darwin":
          if utils.getFromPath("llvm-gcc-4.2", "LLVM GCC"):
             os.system("export CC=llvm-gcc-4.2")
             os.system("export CXX=llvm-g++-4.2")
          else:
             print "Warning: Cannot install pysam on your system. Please install LLVM compiler first."
             doInstall=False
       if doInstall:
          os.system("python setup.py build_ext --inplace")
          os.system("python setup.py build")
          os.system("python setup.py install --home=%spython"%(utils.INITIAL_UTILS+os.sep))
       os.chdir(METAMOS_ROOT)
       os.system("rm -rf pysam.tar.gz")

#WARNING: matplotlib causes install issues for multiple users
   fail = 0
   try:
       import numpy
   except ImportError:
       fail = 1

   if "numpy" in packagesToInstall:
       dl = 'y'
   elif fail:
       print "numpy python modules not found, necessary for html report, download now?"
       dl = raw_input("Enter Y/N: ")
   if fail and (dl == 'y' or dl == "Y"):
       os.system("curl -L http://downloads.sourceforge.net/project/numpy/NumPy/1.7.1/numpy-1.7.1.tar.gz -o ./numpy.tar.gz")
       os.system("tar -C ./Utilities/python -xvf numpy.tar.gz")
       os.system("mv ./Utilities/python/numpy-1.7.1 ./Utilities/python/numpy")
       os.chdir("./Utilities/python/numpy")
       os.system("python setup.py install --home=%spython"%(utils.INITIAL_UTILS+os.sep))
       os.chdir(METAMOS_ROOT)
       os.system("rm -rf numpy.tar.gz")

if 1:
   fail = 0
   try:
       import matplotlib
       if (matplotlib.__version__ < "1.1.0"):
          fail = 1
   except ImportError:
       fail = 1

   if "matplotlib" in packagesToInstall:
       dl = 'y'
   elif fail:
       print "Matplot lib version %s is incompatible with metAMOS. Need version 1.1.0+, download now?"%(matplotlib.__version__) 
       dl = raw_input("Enter Y/N: ")
   if fail and (dl == 'y' or dl == "Y"):
       os.system("curl -L http://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.1.0/matplotlib-1.1.0.tar.gz -o ./matplotlib.tar.gz")
       os.system("tar -C ./Utilities/python -xvf matplotlib.tar.gz")
       os.system("mv ./Utilities/python/matplotlib-1.1.0 ./Utilities/python/matplotlib")
       os.chdir("./Utilities/python/matplotlib")
       os.system("python setup.py install --home=%spython"%(utils.INITIAL_UTILS+os.sep))
       os.chdir(METAMOS_ROOT)
       os.system("rm -rf matplotlib.tar.gz")

# now software
if not os.path.exists("./AMOS") or 0:
   if "amos" in packagesToInstall:
       dl = 'y'
   else:
       print "AMOS binaries not found, needed for all steps, download now?"
       dl = raw_input("Enter Y/N: ")
       
   if dl == 'y' or dl == 'Y':
        os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/amos-3.2-BETA-%s-%s.binaries.tar.gz -o ./amos-binaries.tar.gz"%(OSTYPE, MACHINETYPE))
        os.system("tar -xvf amos-binaries.tar.gz")
        os.system("rm -rf amos-binaries.tar.gz")

if not os.path.exists("./Utilities/cpp%s%s-%s%skraken"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
    if "kraken" in packagesToInstall:
       dl = 'y'
    else:
       print "Kraken not found, optional for Annotate step, download now?"
       dl = raw_input("Enter Y/N: ")
    if dl == 'y' or dl == 'Y':
        archive = "kraken.tar.gz"
        os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/%s -o %s" %(archive, archive))
        os.system("rm -rf ./Utilities/cpp%s%s-%s%skraken"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
        os.system("tar -xvzf %s"%(archive))
        os.system("mv kraken-0.9.1b ./Utilities/cpp/%s%s-%s%skraken"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
        os.chdir("./Utilities/cpp/%s%s-%s%skraken"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
        os.system("./install_kraken.sh `pwd`/bin")
        os.chdir("%s"%(METAMOS_ROOT))
        os.system("rm %s"%archive)

if not os.path.exists("./Utilities/DB/kraken"):
    if "kraken" in packagesToInstall:
       dl = 'y'
    else:
       print "Kraken DB not found, required for Kraken, download now?"
       dl = raw_input("Enter Y/N: ")
    if dl == 'y' or dl == 'Y':
       settings = utils.Settings(1, 1, "", "")
       settings.OSTYPE = OSTYPE
       mem = utils.getAvailableMemory(settings)
       if (mem < 100):
          print "Insufficient memory to build full Kraken database. Requires at least 100GB of memory, using mini DB"
          archive = "minikraken.tgz"
          os.system("curl -L http://ccb.jhu.edu/software/kraken/dl/%s -o %s"%(archive, archive))
          os.system("tar xvzf %s"%(archive))
          os.system("mv minikraken_* ./Utilities/DB/kraken")
          os.system("rm %s"%(archive))
       else:
          os.chdir("./Utilities/cpp/%s%s-%s%skraken"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
          os.system("./bin/kraken-build --standard --threads %d --db %s/Utilities/DB/kraken"%(multiprocessing.cpu_count() - 1, METAMOS_ROOT)) 
          os.chdir("%s"%(METAMOS_ROOT))

if not os.path.exists("./LAP"):
    if "lap" in packagesToInstall:
       dl = 'y'
    else:
       print "LAP tool not found, needed for multiple assembly pipeline, download now?"
       dl = raw_input("Enter Y/N: ")
    if dl == 'y' or dl == 'Y':
        os.system("curl -L http://www.cbcb.umd.edu/~cmhill/files/lap_release_1.1.zip -o lap_release_1.1.zip")
        os.system("unzip lap_release_1.1.zip")
        os.system("mv ./lap_release_1.1 ./LAP")
        os.system("rm -rf lap_release_1.1.zip")

if not os.path.exists("KronaTools") or 0:
    if "kronatools" in packagesToInstall:
       dl = 'y'
    else:
       print "KronaTools not found, needed for Postprocess, download now?"
       dl = raw_input("Enter Y/N: ")
    if dl == 'y' or dl == 'Y':
        # TODO: KronaTools should be on the FTP site for robustness to URL changes
        os.system("curl -L 'ftp://ftp.cbcb.umd.edu/pub/data/metamos/" + kronaTools + ".tar' -o %s.tar"%(kronaTools))
        os.system("tar -xvf %s.tar"%(kronaTools))
        os.system("rm -rf %s.tar"%(kronaTools))
        os.system("mv %s KronaTools"%(kronaTools))
        os.system("cd KronaTools && ./install.pl --prefix=.")

if not os.path.exists("KronaTools/taxonomy/taxonomy.tab") or 0:
    if "kronatools" in packagesToInstall:
       dl = 'y'
    else:
       print "KronaTools taxonomy data not found, needed for Postprocess, download now (will take around 20 minutes)?"
       dl = raw_input("Enter Y/N: ")
    if dl == 'y' or dl == 'Y':
        os.system("cd KronaTools && ./updateTaxonomy.sh")
        os.chdir("%s"%(METAMOS_ROOT))
        os.system("cat KronaTools/taxonomy/taxonomy.tab |awk -F \"\\t\" '{print $1\"\\\t\"$NF}' > ./Utilities/DB/tax_key.tab")

if not os.path.exists("./FastQC"):
    if "fastqc" in packagesToInstall:
        dl = 'y'
    else:
       print "FastQC not found, optional for Preprocess, download now?"
       dl = raw_input("Enter Y/N: ")
    if dl == 'y' or dl == 'Y':
        archive = "fastqc_v0.10.0.zip"
        os.system("curl -L http://www.bioinformatics.babraham.ac.uk/projects/fastqc/%s -o %s" % (archive,archive))
        os.system("unzip %s" % archive)
        os.system("rm %s" % archive)
        os.system("chmod u+x FastQC/fastqc")
        
if not os.path.exists("./Utilities/DB/uniprot_sprot.fasta"):
    if "uniprot" in packagesToInstall:
       dl = 'y'
    else:
       print "Uniprot/Swissprot DB not found, optional for Functional Annotation, download now?"
       dl = raw_input("Enter Y/N: ")
    if dl == 'y' or dl == 'Y':
        archive = "uniprot.tar.gz"
        os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/%s -o %s" %(archive, archive))
        os.system("tar -C ./Utilities/DB/ -xvf %s" % archive)
        os.system("rm %s"%archive)
        
# now workflow specific tools
if "optional" in enabledWorkflows or manual:
    if not os.path.exists("./Utilities/cpp/%s-%s/metaphylerClassify"%(OSTYPE, MACHINETYPE)) or not os.path.exists("./Utilities/perl/metaphyler/markers/markers.protein") or not os.path.exists("./Utilities/perl/metaphyler/markers/markers.dna"):
        if "metaphyler" in packagesToInstall:
           dl = 'y'
        else:
           print "Metaphyler (latest version) not found, optional for Annotate, download now?"
           dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
            os.system("curl -L http://metaphyler.cbcb.umd.edu/MetaPhylerV1.25.tar.gz -o metaphyler.tar.gz")
            os.system("tar -C ./Utilities/perl/ -xvf metaphyler.tar.gz")
            os.system("mv ./Utilities/perl/MetaPhylerV1.25 ./Utilities/perl/metaphyler")
            os.system("mv ./Utilities/perl/metaphyler/installMetaphyler.pl ./Utilities/perl/metaphyler/installMetaphylerFORMATDB.pl");
            os.system("cat ./Utilities/perl/metaphyler/installMetaphylerFORMATDB.pl  |sed 's/formatdb/\.\/Utilities\/cpp\/%s-%s\/formatdb/g' > ./Utilities/perl/metaphyler/installMetaphyler.pl"%(OSTYPE, MACHINETYPE));
            os.system("perl ./Utilities/perl/metaphyler/installMetaphyler.pl")
            os.system("cp ./Utilities/perl/metaphyler/metaphylerClassify ./Utilities/cpp/%s-%s/metaphylerClassify"%(OSTYPE, MACHINETYPE))

    if not os.path.exists("./Utilities/models") or not os.path.exists("./Utilities/DB/blast_data"):
        if "fcp" in packagesToInstall:
           dl = 'y'
        else:
           print "Genome models not found, optional for FCP/NB, download now?"
           dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
            archive = "fcp_models.tar.gz"
            os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/%s -o %s" %(archive, archive))
            os.system("rm -rf ./Utilities/DB/blast_data")
            os.system("rm -rf ./Utilities/models")
            os.system("tar -C ./Utilities/ -xvf %s" % archive)
            os.system("rm %s"%archive)

    if not os.path.exists("./phylosift") or not os.path.exists("./phylosift/legacy/version.pm") or not os.path.exists("./phylosift/lib/Params"):
       if "phylosift" in packagesToInstall:
          dl = 'y'
       else:
          print "PhyloSift binaries not found, optional for Annotate step, download now?"
          dl = raw_input("Enter Y/N: ")
       if dl == 'y' or dl == 'Y':
          if not os.path.exists("./phylosift"):
             #phylosift OSX binaries included inside Linux X86_64 tarball..
             os.system("curl -L http://edhar.genomecenter.ucdavis.edu/~koadman/phylosift/devel/phylosift_20130829.tar.bz2 -o ./phylosift.tar.bz2")
             os.system("tar -xvjf phylosift.tar.bz2")
             os.system("rm -rf phylosift.tar.bz2")
             os.system("mv phylosift_20130829 phylosift")

          if not os.path.exists("./phylosift/legacy/version.pm"):
             #phylosift needs version but doesn't include it
             os.system("curl -L http://www.cpan.org/authors/id/J/JP/JPEACOCK/version-0.9903.tar.gz -o version.tar.gz")
             os.system("tar xvzf version.tar.gz")
             os.chdir("./version-0.9903/")
             os.system("perl Makefile.PL")
             os.system("make")
             os.system("cp -r blib/lib/* ../phylosift/lib")
             os.chdir(METAMOS_ROOT)
             os.system("rm -rf version.tar.gz")
             os.system("rm -rf version-0.9903")
          if not os.path.exists("./phylosift/lib/Params"):
             os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/params-validate.tar.gz -o ./params-validate.tar.gz")
             os.system("tar xvzf params-validate.tar.gz")
             os.system("rm -rf params-validate.tar.gz")
    
    # check the number of files the DB currently is and see if we have the expected number
    dbResult = utils.getCommandOutput("perl ./Utilities/perl/update_blastdb.pl refseq_protein --numpartitions", False)
    if dbResult == "":
       print "Error: could not connect to NCBI, will not be installing refseq protein DB"
    else:
       (dbName, numPartitions) = dbResult.split("\t", 1) 
       print "Checking whether %s is complete. Expecting %d partitions.\n"%(dbName, int(numPartitions))
       numPartitions = int(numPartitions) - 1
    
       if not os.path.exists("./Utilities/DB/refseq_protein.pal") or not os.path.exists("./Utilities/DB/refseq_protein.%02d.psq"%(int(numPartitions))) or not os.path.exists("./Utilities/DB/allprots.faa"):
           if "phmmer" in packagesToInstall:
               dl = 'y'
           else:
              print "refseq protein DB not found or incomplete, needed for Annotate step, download now?"
              dl = raw_input("Enter Y/N: ")
           if dl == 'y' or dl == 'Y':
               print "Download and install refseq protein DB.."
               os.system("perl ./Utilities/perl/update_blastdb.pl refseq_protein")
               os.system("mv refseq_protein.*.tar.gz ./Utilities/DB/")
           
               fileList = glob.glob("./Utilities/DB/refseq_protein.*.tar.gz") 
               for file in fileList:
                  os.system("tar -C ./Utilities/DB/ -xvf %s"%(file))
               print "    running fastacmd (might take a few min)..."
               os.system(".%sUtilities%scpp%s%s-%s%sfastacmd -d ./Utilities/DB/refseq_protein -p T -a T -D 1 -o ./Utilities/DB/allprots.faa"%(os.sep, os.sep, os.sep, OSTYPE, MACHINETYPE, os.sep))

# sra toolkit
if not os.path.exists("./Utilities/cpp%s%s-%s%ssra"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
    sra = utils.getFromPath("srapath", "SRA PATH", False)
    if sra == "":
       if "sra" in packagesToInstall:
          dl = 'y'
       else:
          print "SRA binaries not found, optional for initPipeline step, download now?"
          dl = raw_input("Enter Y/N: ")
       if dl == 'y' or dl == 'Y':
           if OSTYPE == 'Linux' and MACHINETYPE == "x86_64":
              os.system("curl -L http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.3.3-3/sratoolkit.2.3.3-3-centos_linux64.tar.gz -o sra.tar.gz")
           elif  OSTYPE == "Darwin" and MACHINETYPE == "x86_64":
               os.system("curl -L http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/2.3.3-3/sratoolkit.2.3.3-3-mac64.tar.gz -o sra.tar.gz")
           os.system("tar xvzf sra.tar.gz")
           os.system("mv sratoolkit.2.3.3-3-* ./Utilities/cpp%s%s-%s%ssra"%(os.sep, OSTYPE, MACHINETYPE, os.sep)) 
           os.system("rm -rf sra.tar.gz")

if "isolate" in enabledWorkflows or manual:
    if not os.path.exists("./CA") or 0:
      if "ca" in packagesToInstall:
         dl = 'y'
      else:
         print "Celera Assembler binaries not found, optional for Assemble step, download now?"
         dl = raw_input("Enter Y/N: ")
      if dl == 'y' or dl == 'Y':
          if OSTYPE == 'Linux' and MACHINETYPE == "x86_64":
             #hard coded, will fail if moved
             os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/wgs-7.0-PacBio-Linux-amd64.tar.bz2 -o wgs-7.0-PacBio-Linux-amd64.tar.bz2")
             os.system("bunzip2 wgs-7.0-PacBio-Linux-amd64.tar.bz2")
             os.system("tar xvf wgs-7.0-PacBio-Linux-amd64.tar")
             os.system("rm -rf wgs-7.0-PacBio-Linux-amd64.tar")
          else:
             os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/wgs-7.0.tar.bz2 -o wgs-7.0.tar.bz2")
             os.system("bunzip2 wgs-7.0.tar.bz2")
             os.system("tar xvf wgs-7.0.tar")
             os.system("rm -rf wgs-7.0.tar")
             # patch CA to support PacBio sequences and non-apple compilers on OSX
             if not ALLOW_FAST:
                os.system("cd wgs-7.0/kmer/ && cp configure.sh configure.original")
                os.system("cd wgs-7.0/kmer/ && cat configure.original |sed s/\-fast//g > configure.sh")
             os.system("cd wgs-7.0/src/ && cp AS_global.h AS_global.original")
             os.system("cd wgs-7.0/src/ && cat AS_global.original | sed 's/AS_READ_MAX_NORMAL_LEN_BITS.*11/AS_READ_MAX_NORMAL_LEN_BITS      15/g' > AS_global.h")
             os.system("cd wgs-7.0/kmer && ./configure.sh && gmake install")
             os.system("cd wgs-7.0/src && gmake")
          os.system("mv wgs-7.0 CA")

    if not os.path.exists("./Utilities/cpp%s%s-%s%sRay"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       if "ray" in packagesToInstall:
          dl = 'y'
       else:
          print "Ray binaries not found, optional for Assemble step, download now?"
          dl = raw_input("Enter Y/N: ")
       if dl == 'y' or dl == 'Y':
          # check for mpi which is required
          command="mpicxx"
          mpi=utils.getFromPath(command, "MPI", False)
          if not os.path.exists("%s%s%s"%(mpi, os.sep, command)):
             command="openmpicxx"
             mpi=utils.getFromPath(command, "MPI", False)
             if not os.path.exists("%s%s%s"%(mpi, os.sep, command)):
                mpi = command = ""
                print "Error: cannot find MPI, required to build Ray. Please add it to your path."
          if command != "":
             os.system("curl -L http://downloads.sourceforge.net/project/denovoassembler/Ray-v2.2.0.tar.bz2 -o Ray-v2.2.0.tar.bz2")
             os.system("tar xvjf Ray-v2.2.0.tar.bz2")
             os.system("mv Ray-v2.2.0 ./Utilities/cpp/%s%s-%s%sRay"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.chdir("./Utilities/cpp/%s%s-%s%sRay"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("make PREFIX=bin MPICXX=%s%s%s MAXKMERLENGTH=128 MPI_IO=y DEBUG=n ASSERT=n EXTRA=\" -march=native\""%(mpi, os.sep, command))
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("rm -rf Ray-v2.2.0.tar.bz2")

    if not os.path.exists("./Utilities/cpp%s%s-%s%skmergenie"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
        kmerGenie = utils.getFromPath("kmergenie", "Kmer Genie", False)
        if kmerGenie == "":
           if "kmergenie" in packagesToInstall:
              dl = 'y'
           else:
              print "Kmer Genie was not found, optional for Assemble step, download now?"
              dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
           os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/kmergenie-1.5692.tar.gz -o kmer.tar.gz")
           os.system("tar xvzf kmer.tar.gz")
           os.system("mv kmergenie-1.5692 ./Utilities/cpp%s%s-%s%skmergenie"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
           os.chdir("./Utilities/cpp%s%s-%s%skmergenie"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
           os.system("make k=300")
           os.chdir("%s"%(METAMOS_ROOT))
           os.system("rm -rf kmer.tar.gz")

    if not os.path.exists("./Utilities/cpp%s%s-%s%sprokka"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       prokaBin = utils.getFromPath("prokka", "Prokka", False)
       dl = 'n'
       if prokaBin == "":
          if "prokka" in packagesToInstall:
             dl = 'y'
          else:
             print "Prokka binaries not found, optional for Assemble step, download now?"
             dl = raw_input("Enter Y/N: ")
       if dl == 'y' or dl == 'Y':
          signalp = utils.getFromPath("signalp", "SignalP", False)
          if signalp == "":
             print "Warning: SignalP is not installed and is required for Prokka's gram option. Please download it and add it to your path."
          os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/prokka-1.7.tar.gz -o prokka-1.7.tar.gz")
          os.system("tar xvzf prokka-1.7.tar.gz")
          os.system("mv prokka-1.7 ./Utilities/cpp%s%s-%s%sprokka"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
          os.system("rm prokka-1.7.tar.gz")

          bioperl = utils.getCommandOutput("perl -MBio::Seq -e 0 && echo $?", True)
          perltime = utils.getCommandOutput("perl -MTime::Piece -e 0 && echo $?", True)
          xmlsimple = utils.getCommandOutput("perl -MXML::Simple -e 0 && echo $?", True)

          # always install bioperl, otherwise parts may be missing or it may be the wrong version
          # phylosift comes with BioPerl, use it
          os.system("curl -L http://edhar.genomecenter.ucdavis.edu/~koadman/phylosift/devel/phylosift_20130829.tar.bz2 -o ./phylosift.tar.bz2")
          os.system("tar -xvjf phylosift.tar.bz2")
          os.system("rm -rf phylosift.tar.bz2")
          os.system("mv phylosift_20130829/lib ./Utilities/cpp%s%s-%s%sprokka"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
          os.system("rm -rf phylosift_20130829")

          if perltime == "":
             os.system("curl -L http://search.cpan.org/CPAN/authors/id/M/MS/MSERGEANT/Time-Piece-1.08.tar.gz -o time.tar.gz")
             os.system("tar -xvzf time.tar.gz")
             os.chdir("Time-Piece-1.08")
             os.system("perl Makefile.PL PREFIX=`pwd`/build")
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             pathToCopy = utils.getCommandOutput("find Time-Piece-1.08/build -type d -name \"Time\" |grep -v auto", False)
             pathToCopy = os.path.dirname(pathToCopy)
             os.system("mkdir -p ./Utilities/cpp%s%s-%s%sprokka/lib"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             # copy one at a time in case of conflicts
             for file in os.listdir("%s%s"%(pathToCopy, os.sep)):
                toCopy = file
                file = "%s%s%s"%(pathToCopy, os.sep, toCopy)
                if os.path.exists("./Utilities/cpp%s%s-%s%sprokka/lib/%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, toCopy)):
                   os.system("mv %s/* ./Utilities/cpp%s%s-%s%sprokka/lib/%s/"%(file, os.sep, OSTYPE, MACHINETYPE, os.sep, toCopy))
                else:
                   os.system("mv %s ./Utilities/cpp%s%s-%s%sprokka/lib/"%(file, os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("rm -rf time.tar.gz")
             os.system("rm -rf Time-Piece-1.08") 

          if xmlsimple == "":
             os.system("curl -L http://search.cpan.org/CPAN/authors/id/G/GR/GRANTM/XML-Simple-1.08.tar.gz -o xml.tar.gz")
             os.system("tar -xvzf xml.tar.gz")
             os.chdir("XML-Simple-1.08")
             os.system("perl Makefile.PL PREFIX=`pwd`/build")
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             pathToCopy = utils.getCommandOutput("find XML-Simple-1.08/build -type d -name \"XML\" |grep -v auto", False)
             pathToCopy = os.path.dirname(pathToCopy)
             os.system("mkdir -p ./Utilities/cpp%s%s-%s%sprokka/lib"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             for file in os.listdir("%s%s"%(pathToCopy, os.sep)):
                toCopy = file
                file = "%s%s%s"%(pathToCopy, os.sep, toCopy)
                if os.path.exists("./Utilities/cpp%s%s-%s%sprokka/lib/%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, toCopy)):
                   os.system("mv %s/* ./Utilities/cpp%s%s-%s%sprokka/lib/%s/"%(file, os.sep, OSTYPE, MACHINETYPE, os.sep, toCopy))
                else:
                   os.system("mv %s ./Utilities/cpp%s%s-%s%sprokka/lib/"%(file, os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("rm -rf xml.tar.gz")
             os.system("rm -rf XML-Simple-1.08")

          if os.path.exists("./Utilities/cpp%s%s-%s%sprokka/lib"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
             os.chdir("./Utilities/cpp%s%s-%s%sprokka/bin"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("cp prokka prokka.original")
             os.system("cat prokka.original |awk '{if (match($0, \"use strict\")) { print \"use lib \\\"%s/Utilities/cpp%s%s-%s%sprokka/lib\\\";\"; print $0; } else { print $0}}' > prokka"%(METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.chdir("%s"%(METAMOS_ROOT))
          # for some reason prokka adds its binaries to the end of path, not beginning so if your path has the wrong version of a program, it will crash. Update
          os.chdir("./Utilities/cpp%s%s-%s%sprokka/bin"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
          os.system("cp prokka prokka.original")
          os.system("cat prokka.original |awk '{if (match($0, \"ENV{PATH}\")) { print \"$ENV{PATH} = $BINDIR . \\\":\\\" . $ENV{PATH};\"; } else { print $0}}' > prokka")
          os.chdir("%s"%(METAMOS_ROOT))

          aragorn = utils.getFromPath("aragorn", "aragorn", False)
          aragornVersion = ""
          if aragorn != "":
             aragornVersion = utils.getCommandOutput("%s/aragorn -h 2>&1 | grep -i '^ARAGORN v' |sed s/v//g |awk '{printf(\"%%2.2f\n\", $2)}'", True)
             if float(aragornVersion) < 1.2:
                aragorn = ""
          if aragorn == "":
             print "Aragorn missing, will install"
             os.system("curl -L http://130.235.46.10/ARAGORN/Downloads/aragorn1.2.36.tgz -o aragorn.tar.gz")
             os.system("tar xvzf aragorn.tar.gz")
             os.chdir("aragorn1.2.36")
             os.system("gcc -O3 -ffast-math -finline-functions -o aragorn aragorn1.2.36.c")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("mv aragorn1.2.36/aragorn ./Utilities/cpp%s%s-%s%sprokka/binaries%s%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower()))
             os.system("rm -rf aragorn1.2.36")
             os.system("rm aragorn.tar.gz")
          infernal = utils.getFromPath("cmscan", "Infernal", False)
          if infernal == "" and not os.path.exists("./Utilities/cpp%s%s-%s%sprokka/binaries/%s/infernal"%(os.sep, OSTYPE, MACHINETYPE, os.sep, OSTYPE.lower())):
             print "Infernal missing, will install"
             if OSTYPE == "Darwin":
                os.system("curl -L http://selab.janelia.org/software/infernal/infernal-1.1rc4-macosx-intel.tar.gz -o infernal.tar.gz")
             else:
                os.system("curl -L http://selab.janelia.org/software/infernal/infernal-1.1rc4-linux-intel-gcc.tar.gz -o infernal.tar.gz")
             os.system("tar xvzf infernal.tar.gz")
             os.system("mv infernal*/binaries/* ./Utilities/cpp%s%s-%s%sprokka/binaries%s%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower()))
             os.system("rm -rf infernal*")
          barrnap = utils.getFromPath("barrnap", "barrnap", False)
          if barrnap == "" and not os.path.exists("./Utilities/cpp%s%s-%s%sprokka/binaries/%s/barrnap"%(os.sep, OSTYPE, MACHINETYPE, os.sep, OSTYPE.lower())):
             print "Barrnap missing, will install"
             os.system("curl -L http://www.vicbioinformatics.com/barrnap-0.1.tar.gz -o barrnap.tar.gz")
             os.system("tar xvzf barrnap.tar.gz")
             os.system("mv barrnap-0.1/barrnap ./Utilities/cpp%s%s-%s%sprokka/binaries%s%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower()))
             os.system("mv barrnap-0.1/db ./Utilities/cpp%s%s-%s%sprokka/binaries%s%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower()))
             os.system("rm -rf barrnap-0.1")
             os.system("rm barrnap.tar.gz")

          hmmscan = utils.getFromPath("hmmscan", "HMMER3", False)
          hmmscanVersion = ""
          if hmmscan != "":
             hmmscanVersion = utils.getCommandOutput("%s/hmmscan -h | grep '^# HMMER' |awk '{printf(\"%%2.2f\\n\", $3)}'"%(hmmscan), True)
             print "Found HMM SCAN %s %s"%(hmmscan, hmmscanVersion)
             if float(hmmscanVersion) < 3.1:
                hmmscan = ""
          if hmmscan == "" and not os.path.exists("./Utilities/cpp%s%s-%s%sprokka/binaries/%s/hmmscan"%(os.sep, OSTYPE, MACHINETYPE, os.sep, OSTYPE.lower())):
             print "HMMER3 is missing, will install"
             if OSTYPE == "Darwin":
                os.system("curl -L ftp://selab.janelia.org/pub/software/hmmer3/3.1b1/hmmer-3.1b1-macosx-intel.tar.gz -o hmmer.tar.gz")
             elif OSTYPE == "Linux" and MACHINETYPE == "x86_64":
                os.system("curl -L ftp://selab.janelia.org/pub/software/hmmer3/3.1b1/hmmer-3.1b1-linux-intel-x86_64.tar.gz -o hmmer.tar.gz")
             elif OSTYPE == "Linux":
                os.system("curl -L ftp://selab.janelia.org/pub/software/hmmer3/3.1b1/hmmer-3.1b1-linux-intel-ia32.tar.gz -o hmmer.tar.gz") 
             os.system("tar xvzf hmmer.tar.gz")
             os.system("mv hmmer*/binaries/* ./Utilities/cpp%s%s-%s%sprokka/binaries%s%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower()))
             os.system("rm -rf hmmer*")

          gnuparallel = utils.getFromPath("parallel", "GNU Parallel", False)
          if gnuparallel == "" and not os.path.exists("./Utilities/cpp%s%s-%s%sprokka/binaries/%s/parallel"%(os.sep, OSTYPE, MACHINETYPE, os.sep, OSTYPE.lower())):
             print "GNU Parallel is missing, will install"
             os.system("curl -L http://ftp.gnu.org/gnu/parallel/parallel-20100424.tar.bz2 -o parallel.tar.gz")
             os.system("tar xvjf parallel.tar.gz")
             os.chdir("parallel-20100424")
             os.system("./configure --prefix=`pwd`")
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("mv parallel-20100424/parallel ./Utilities/cpp%s%s-%s%sprokka/binaries%s%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower()))
             os.system("rm -rf parallel-20100424")
             os.system("rm parallel.tar.gz")
          
          blastp = utils.getFromPath("blastp", "BLAST+", False)
          if blastp == "" and not os.path.exists("./Utilities/cpp%s%s-%s%sprokka/binaries/%s/blastp"%(os.sep, OSTYPE, MACHINETYPE, os.sep, OSTYPE.lower())):
             os.system("ln %s/Utilities/cpp%s%s-%s%sblastp %s/Utilities/cpp%s%s-%s%sprokka/binaries%s%s%sblastp"%(METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep, METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower(), os.sep))

          prodigal = utils.getFromPath("prodigal", "PRODIGAL", False)
          if prodigal != "":
             prodigalVersion = utils.getCommandOutput("%s/prodigal -v 2>&1 | grep -i '^Prodigal V' |sed s/V//g |awk '{printf(\"%%2.2f\n\", $2)}'"%(prodigal), True)
             print "Found prodigal %s %s"%(prodigal, prodigalVersion)
             if float(prodigalVersion) < 2.6:
                prodigal = ""

          if prodigal == "":
             os.system("curl -L https://prodigal.googlecode.com/files/prodigal.v2_60.tar.gz -o prodigal.tar.gz")
             os.system("tar xvzf prodigal.tar.gz")
             os.system("rm -rf prodigal.tar.gz")
             os.system("curl -L https://prodigal.googlecode.com/files/prodigal_v2.60.bugfix1.tar.gz -o prodigal.tar.gz")
             os.system("tar xvzf prodigal.tar.gz")
             os.system("mv prodigal_v2.60.bugfix1/* prodigal.v2_60/")
             os.chdir("prodigal.v2_60")
             os.system("make")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("mv prodigal.v2_60/prodigal ./Utilities/cpp%s%s-%s%sprokka/binaries%s%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower()))
             os.system("rm -rf prodigal.tar.gz")
             os.system("rm -rf prodigal.v2_60") 
             os.system("rm -rf prodigal_v2.60.bugfix1")

          tbl2asn = utils.getFromPath("tbl2asn", "NCBI Tbl2Asn", False)
          if tbl2asn == "" and not os.path.exists("./Utilities/cpp%s%s-%s%sprokka/binaries/%s/tbl2asn"%(os.sep, OSTYPE, MACHINETYPE, os.sep, OSTYPE.lower())):
             print "NCBI Tbl2Asn is missing, will install"
             if OSTYPE == "Darwin":
                os.system("curl -L ftp://ftp.ncbi.nih.gov/toolbox/ncbi_tools/converters/by_program/tbl2asn/mac.tbl2asn.gz -o tbl2asn.gz")
             elif OSTYPE == "Linux" and MACHINETYPE == "x86_64":
                os.system("curl -L ftp://ftp.ncbi.nih.gov/toolbox/ncbi_tools/converters/by_program/tbl2asn/linux64.tbl2asn.gz -o tbl2asn.gz")
             elif OSTYPE == "Linux":
                os.system("curl -L ftp://ftp.ncbi.nih.gov/toolbox/ncbi_tools/converters/by_program/tbl2asn/linux.tbl2asn.gz -o tbl2asn.gz")
             os.system("gunzip tbl2asn.gz")
             os.system("chmod ug+x tbl2asn")
             os.system("mv tbl2asn ./Utilities/cpp%s%s-%s%sprokka/binaries%s%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep, OSTYPE.lower()))
             os.system("rm tbl2asn.gz")

    if not os.path.exists("./Utilities/cpp%s%s-%s%ssoap2"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       if "soap2" in packagesToInstall:
          if "soap2" in packagesToInstall:
             dl = 'y'
          else:
             print "SOAPdenovo2 binaries not found, optional for Assemble step, download now?"
             dl = raw_input("Enter Y/N: ")
          if dl == 'y' or dl == 'Y':
             if OSTYPE == "Darwin":
                os.system("curl -L http://sourceforge.net/projects/soapdenovo2/files/SOAPdenovo2/bin/r223/SOAPdenovo2-bin-MACOS-generic-r223.tgz -o soap2.tar.gz")
             else:
                os.system("curl -L http://sourceforge.net/projects/soapdenovo2/files/SOAPdenovo2/bin/r223/SOAPdenovo2-bin-LINUX-generic-r223.tgz -o soap2.tar.gz")
             os.system("curl -L http://sourceforge.net/projects/soapdenovo2/files/GapCloser/src/r6/GapCloser-src-v1.12-r6.tgz -o gapcloser.tar.gz")
             os.system("tar xvzf gapcloser.tar.gz")
             os.chdir("v1.12-r6")
             os.system("make")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("mkdir -p ./Utilities/cpp%s%s-%s%ssoap2/bin"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("mv soap2.tar.gz ./Utilities/cpp%s%s-%s%ssoap2/bin"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.chdir("./Utilities/cpp%s%s-%s%ssoap2/bin"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("tar xvzf soap2.tar.gz")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("mv v1.12-r6/Release/* ./Utilities/cpp%s%s-%s%ssoap2/bin"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("rm -rf soap2.tar.gz")
             os.system("rm -rf v1.12-r6")
             os.system("rm -rf gapcloser.tar.gz")

    if not os.path.exists("./Utilities/cpp%s%s-%s%sMaSuRCA"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       masurca = utils.getFromPath("runSRCA.pl", "MaSuRCA", False)
       if masurca == "" and OSTYPE != "Darwin":
          if "masurca" in packagesToInstall:
             dl = 'y'
          else:
             print "MaSuRCA binaries not found, optional for Assemble step, download now?"
             dl = raw_input("Enter Y/N: ")
          if dl == 'y' or dl == 'Y':
             gccVersion = utils.getCommandOutput("gcc --version|grep gcc|awk '{print $NF}' |awk -F \".\" '{print $1\".\"$2}'", False)
             if float(gccVersion) < 4.4:
                print "Error: MaSuRCA requires gcc at least version 4.4, found version %s. Please update and try again"%(gccVersion)
             else:
                os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/MaSuRCA-2.0.3.1.tar.gz -o msrca.tar.gz")
                os.system("tar xvzf msrca.tar.gz")
                os.system("mv ./MaSuRCA-2.0.3.1 ./Utilities/cpp%s%s-%s%sMaSuRCA"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
                os.chdir("./Utilities/cpp%s%s-%s%sMaSuRCA"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
                os.system("cp install.sh install.orig")
                os.system("cat install.orig |sed s/\-\-prefix/\-\-disable\-shared\ \-\-prefix/g > install.sh")
                # patch CA
                if not ALLOW_FAST:
                   os.system("cd CA/kmer/ && cp configure.sh configure.original")
                   os.system("cd CA/kmer/ && cat configure.original |sed s/\-fast//g > configure.sh")
                if not HAVE_RT:
                   os.system("cd SuperReads-0.3.2/ && cp Makefile.am Makefile.am.original")
                   os.system("cd SuperReads-0.3.2/ && cat Makefile.am.original |sed s/\-lrt//g > Makefile.am")
                   os.system("cd SuperReads-0.3.2/ && cp Makefile.in Makefile.in.original")
                   os.system("cd SuperReads-0.3.2/ && cat Makefile.in.original |sed s/\-lrt//g > Makefile.in")
                if not HAVE_QUIET_HEAD:
                   os.system("cd SuperReads-0.3.2/src && cp runSRCA.pl runSRCA.original")
                   os.system("cd SuperReads-0.3.2/src && cat runSRCA.original |sed s/head\ \-q/head/g > runSRCA.pl")
                os.system("bash install.sh")
                os.chdir("%s"%(METAMOS_ROOT))
                os.system("rm -rf ./MaSuRCA-2.0.3.1")
                os.system("rm msrca.tar.gz")

    if not os.path.exists("./Utilities/cpp%s%s-%s%smira"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       mira = utils.getFromPath("mira", "MIRA", False)
       if mira == "":
          if "mira" in packagesToInstall:
             dl = 'y'
          else:
             print "MIRA binaries not found, optional for Assemble step, download now?"
             dl = raw_input("Enter Y/N: ")
          if dl == 'y' or dl == 'Y':
             if OSTYPE == "Darwin":
	        os.system("curl -L http://sourceforge.net/projects/mira-assembler/files/MIRA/stable/mira_4.0rc2_darwin12.5.0_x86_64_static.tar.bz2 -o mira.tar.bz2")
             else:
                os.system("curl -L http://sourceforge.net/projects/mira-assembler/files/MIRA/stable/mira_4.0rc2_linux-gnu_x86_64_static.tar.bz2 -o mira.tar.bz2")
             os.system("tar xvjf mira.tar.bz2")
             os.system("rm -f mira.tar.bz2")
             os.system("mv `ls -d mira*` ./Utilities/cpp%s%s-%s%smira"%(os.sep, OSTYPE, MACHINETYPE, os.sep))

    if not os.path.exists("./Utilities/cpp%s%s-%s%sidba"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       idba = utils.getFromPath("idba", "IDBA-UD", False)
       if idba == "":
          if "idba" in packagesToInstall:
             dl = 'y'
          else:
             print "IDBA-UD binaries not found, optional for Assemble step, download now?"
             dl = raw_input("Enter Y/N: ")
          if dl == 'y' or dl == 'Y':
             os.system("curl -L http://hku-idba.googlecode.com/files/idba-1.1.1.tar.gz -o idba.tar.gz")
             os.system("tar xvzf idba.tar.gz")
             os.system("mv idba-1.1.1 ./Utilities/cpp%s%s-%s%sidba"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.chdir("./Utilities/cpp%s%s-%s%sidba"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("mv src/sequence/short_sequence.h src/sequence/short_sequence.orig")
             os.system("cat src/sequence/short_sequence.orig |awk '{if (match($0, \"kMaxShortSequence = 128\")) print \"static const uint32_t kMaxShortSequence = 32768;\"; else print $0}' > src/sequence/short_sequence.h")
             os.system("./configure")
             os.system("make")
             os.chdir("%s"%(METAMOS_ROOT))

    if not os.path.exists("./Utilities/cpp%s%s-%s%sabyss"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       abyss = utils.getFromPath("ABYSS", "ABySS", False)
       if abyss == "":
          if "abyss" in packagesToInstall:
             dl = 'y'
          else:
             print "ABySS binaries not found, optional for Assemble step, download now?"
             dl = raw_input("Enter Y/N: ")
          if dl == 'y' or dl == 'Y':
             os.system("curl -L https://sparsehash.googlecode.com/files/sparsehash-2.0.2.tar.gz -o sparse.tar.gz")
             os.system("tar xvzf sparse.tar.gz")
             os.chdir("sparsehash-2.0.2")
             os.system("./configure --prefix=`pwd`")
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("curl -L http://sourceforge.net/projects/boost/files/boost/1.49.0/boost_1_49_0.tar.gz -o boost.tar.gz")
             os.system("tar xvzf boost.tar.gz")
             os.system("curl -L http://www.bcgsc.ca/platform/bioinfo/software/abyss/releases/1.3.6/abyss-1.3.6.tar.gz -o abyss.tar.gz")
             os.system("tar xvzf abyss.tar.gz")
             os.chdir("abyss-1.3.6")
             os.system("ln -s %s/boost_1_49_0/boost boost"%(METAMOS_ROOT))
             os.environ["CFLAGS"] = "-I%s/sparsehash-2.0.2/include"%(METAMOS_ROOT)
             os.environ["CPPFLAGS"] = "-I%s/sparsehash-2.0.2/include"%(METAMOS_ROOT)
             os.environ["CXXFLAGS"] = "-I%s/sparsehash-2.0.2/include"%(METAMOS_ROOT)
             os.system("./configure --enable-maxk=96 --prefix=`pwd`/build")
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("mkdir ./Utilities/cpp%s%s-%s%sabyss"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("mv abyss-1.3.6/build/* ./Utilities/cpp%s%s-%s%sabyss/"%(os.sep, OSTYPE, MACHINETYPE, os.sep))

             # update abysss to use installed mpi
             command="mpirun"
             mpi=utils.getFromPath(command, "MPI", False)
             if not os.path.exists("%s%s%s"%(mpi, os.sep, command)):
                command="openmpirun"
                mpi=utils.getFromPath(command, "MPI", False)
                if not os.path.exists("%s%s%s"%(mpi, os.sep, command)):
                   mpi = command = ""
             os.chdir("./Utilities/cpp%s%s-%s%sabyss/bin/"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("cp abyss-pe abyss-pe-orig")
             if mpi != "" and os.path.exists("./Utilities/cpp%s%s-%s%sabyss/bin/ABYSS-P"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
                os.system("cat abyss-pe-orig |sed s/which\ mpirun/which\ %s/g > abyss-pe"%(command))
             else:
                print "Error: cannot find MPI in your path. Disabling ABySS threading."
                os.system("cat abyss-pe-orig |awk -v found=0 -v skipping=0 '{if (match($0, \"ifdef np\")) {skipping=1; } if (skipping && match($1, \"ABYSS\")) {print $0; skipping=1; found=1} if (found && match($1, \"endif\")) {skipping=0;found = 0;} else if (skipping == 0) { print $0; } }' > abyss-pe")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("rm -rf sparsehash-2.0.2")
             os.system("rm -rf sparse.tar.gz")
             os.system("rm -rf abyss-1.3.6")
             os.system("rm -rf abyss.tar.gz")
             os.system("rm -rf boost_1_49_0")
             os.system("rm -rf boost.tar.gz")

    if not os.path.exists("./Utilities/cpp%s%s-%s%ssga"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       sga = utils.getFromPath("sga", "SGA", False)
       if sga == "":
          if "sga" in packagesToInstall:
             dl = 'y'
          else:
             print "SGA binaries not found, optional for Assemble step, download now?"
             dl = raw_input("Enter Y/N: ")
          if dl == 'y' or dl == 'Y':
             os.system("curl -L https://sparsehash.googlecode.com/files/sparsehash-2.0.2.tar.gz -o sparse.tar.gz")
             os.system("tar xvzf sparse.tar.gz")
             os.chdir("sparsehash-2.0.2")
             os.system("./configure --prefix=`pwd`")
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("curl -L https://github.com/pezmaster31/bamtools/archive/master.zip -o bamtools.tar.gz")
             os.system("unzip bamtools.tar.gz")
             os.system("curl -L http://sourceforge.net/projects/bio-bwa/files/bwa-0.7.5a.tar.bz2 -o bwa.tar.bz2")
             os.system("tar xvjf bwa.tar.bz2")
             os.chdir("bwa-0.7.5a")
             os.system("make")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("curl -L https://github.com/jts/sga/archive/master.zip -o sga.tar.gz")
             os.system("unzip sga.tar.gz")
             os.system("mv sga-master ./Utilities/cpp%s%s-%s%ssga"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("mv bamtools-master ./Utilities/cpp%s%s-%s%ssga/bamtools"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("mv sparsehash-2.0.2 ./Utilities/cpp%s%s-%s%ssga/sparsehash"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.chdir("./Utilities/cpp%s%s-%s%ssga/bamtools"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("mkdir build")
             os.chdir("build")
             os.system("cmake ..")
             os.system("make")
             os.chdir("%s"%(METAMOS_ROOT))
             os.chdir("./Utilities/cpp%s%s-%s%ssga/src"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("sh ./autogen.sh")
             os.system("./configure --with-sparsehash=`pwd`/../sparsehash --with-bamtools=`pwd`/../bamtools --prefix=`pwd`/../")
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             os.system("mv bwa-0.7.5a/bwa ./Utilities/cpp%s%s-%s%ssga/bin/"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("ln %s/Utilities/cpp%s%s-%s%ssamtools %s/Utilities/cpp%s%s-%s%ssga/bin%ssamtools"%(METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep, METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep, os.sep))
             os.system("rm -rf sparsehash-2.0.2")
             os.system("rm -rf sparse.tar.gz")
             os.system("rm -rf bamtools-master")
             os.system("rm -rf bamtools.tar.gz")
             os.system("rm -rf sga-master")
             os.system("rm -rf sga.tar.gz")
             os.system("rm -rf bwa.tar.gz")
             os.system("rm -rf bwa-0.7.5.a")

    if not os.path.exists("./quast"):
        if "quast" in packagesToInstall:
           dl = 'y'
        else:
           print "QUAST tool not found, optional for Validate step, download now?"
           dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
            os.system("curl -L http://downloads.sourceforge.net/project/quast/quast-2.2.tar.gz -o quast.tar.gz")
            os.system("tar xvzf quast.tar.gz")
            os.system("mv ./quast-2.2 ./quast")
            os.system("rm -rf quast.tar.gz")

            # since quast requires a reference, also download refseq
            ftpSite = "ftp://ftp.ncbi.nih.gov/genomes/Bacteria"
            file = "all.fna.tar.gz"
            print "Downloading refseq genomes (%s)..."%(file)
            print "\tThis file is large and may take time to download"
            os.system("curl -L %s/%s -o genomes.tar.gz"%(ftpSite, file))
            os.system("mkdir -p ./Utilities/DB/refseq/temp")
            os.system("mv genomes.tar.gz ./Utilities/DB/refseq/temp")
            os.chdir("./Utilities/DB/refseq/temp")
            os.system("tar xvzf genomes.tar.gz")
            os.chdir("..")
            print "Current directory is %s"%(os.getcwd())
            for file in os.listdir("%s/temp"%(os.getcwd())):
               file = "%s%stemp%s%s"%(os.getcwd(), os.sep, os.sep, file)
               if os.path.isdir(file):
                  prefix = os.path.splitext(os.path.basename(file))[0]
                  os.system("cat %s/*.fna > %s.fna"%(file, prefix))
            os.system("rm -rf temp")
            os.chdir("%s"%(METAMOS_ROOT))
   
    if not os.path.exists("./Utilities/cpp%s%s-%s%sfreebayes"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
        if "freebayes" in packagesToInstall:
           dl = 'y'
        else:
           print "FreeBayes tool not found, optional for Validate step, download now?"
           dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
           os.system("git clone --recursive git://github.com/ekg/freebayes.git freebayes")
           os.system("mv ./freebayes ./Utilities/cpp/%s%s-%s%sfreebayes"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
           os.chdir("./Utilities/cpp/%s%s-%s%sfreebayes"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
           os.system("make")
           os.chdir("%s"%(METAMOS_ROOT))

    if not os.path.exists("./Utilities/cpp%s%s-%s%scgal"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
        if "cgal" in packagesToInstall:
           dl = 'y'
        else:
           print "CGAL tool not found, optional for Validate step, download now?"
           dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
            os.system("curl -L http://bio.math.berkeley.edu/cgal/cgal-0.9.6-beta.tar -o cgal.tar")
            os.system("tar xvf cgal.tar")
            os.system("mv cgal-0.9.6-beta ./Utilities/cpp/%s%s-%s%scgal"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
            os.chdir("./Utilities/cpp/%s%s-%s%scgal"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
            os.system("make")
            os.chdir("%s"%(METAMOS_ROOT))
            os.system("rm -rf cgal.tar")

    if not os.path.exists("./Utilities/cpp%s%s-%s%sREAPR"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
       if "reapr" in packagesToInstall:
          dl = 'y'
       else:
           print "REAPR tool not found, optional for Validate step, download now?"
           dl = raw_input("Enter Y/N: ")
       if dl == 'y' or dl == 'Y':
          os.system("curl -L ftp://ftp.sanger.ac.uk/pub4/resources/software/reapr/Reapr_1.0.16.tar.gz -o reapr.tar.gz")
          os.system("tar xvzf reapr.tar.gz")
          os.system("mv Reapr_1.0.16 ./Utilities/cpp/%s%s-%s%sREAPR"%(os.sep, OSTYPE, MACHINETYPE, os.sep))

          filespec = utils.getCommandOutput("perl -MFile::Spec::Link -e 0 && echo $?", True)
          if filespec == "":
             os.system("curl -L http://search.cpan.org/CPAN/authors/id/R/RM/RMBARKER/File-Copy-Link-0.113.tar.gz -o file.tar.gz")
             os.system("tar xvzf file.tar.gz")
             os.chdir("File-Copy-Link-0.113")
             os.system("perl Makefile.PL PREFIX=`pwd`/build")
             os.system("make install")
             os.chdir("%s"%(METAMOS_ROOT))
             pathToCopy = utils.getCommandOutput("find File-Copy-Link-0.113/build -type d -name \"File\" |grep -v auto", False)
             pathToCopy = os.path.dirname(pathToCopy)
             os.system("mkdir -p ./Utilities/cpp%s%s-%s%sREAPR/lib"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             # copy one at a time in case of conflicts
             for file in os.listdir("%s%s"%(pathToCopy, os.sep)):
                toCopy = file
                file = "%s%s%s"%(pathToCopy, os.sep, toCopy)
                if os.path.exists("./Utilities/cpp%s%s-%s%sREAPR/lib/%s"%(os.sep, OSTYPE, MACHINETYPE, os.sep, toCopy)):
                   os.system("mv %s/* ./Utilities/cpp%s%s-%s%sREAPR/lib/%s/"%(file, os.sep, OSTYPE, MACHINETYPE, os.sep, toCopy))
                else:
                   os.system("mv %s ./Utilities/cpp%s%s-%s%sREAPR/lib/"%(file, os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("rm -rf file.tar.gz")
             os.system("rm -rf File-Copy-Link-0.113")
             os.environ["PERL5LIB"]+="%s/Utilities/cpp%s%s-%s%sREAPR/lib/"%(METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep)
          os.chdir("./Utilities/cpp/%s%s-%s%sREAPR"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
          os.system("sh install.sh")
          os.chdir("%s"%(METAMOS_ROOT))

          if os.path.exists("./Utilities/cpp%s%s-%s%sREAPR/lib"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
             os.chdir("./Utilities/cpp%s%s-%s%sREAPR/"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.system("cp reapr reapr.original")
             os.system("cat reapr.original |awk '{if (match($0, \"use strict\")) { print \"use lib \\\"%s/Utilities/cpp%s%s-%s%sREAPR/lib\\\";\"; print $0; } else { print $0}}' > reapr"%(METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep))
             os.chdir("%s"%(METAMOS_ROOT))

          # REAPR has a bug where fasta headers with commas are not properly fixed, patch the bug
          os.chdir("./Utilities/cpp%s%s-%s%sREAPR/src"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
          os.system("cp task_facheck.pl task_facheck.pl.original")
          os.system("cat task_facheck.pl.original |awk -v comma=\"'\"  '{if (match($0, \"new_id =~\")) { print \"$new_id =~ s/[;|:,\"comma\"\\+\\-\\s\\(\\)\\{\\}\\[\\]]/_/g;\"; } else { print $0}}' > task_facheck.pl")
          os.chdir("%s"%(METAMOS_ROOT))
          os.system("rm -rf reapr.tar.gz")
    
    if not os.path.exists("./Utilities/cpp%s%s-%s%sFRCbam"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
        if "frcbam" in packagesToInstall:
           dl = 'y'
        else:
           print "FRCbam tool not found, optional for Validate step, download now?"
           dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
            os.system("curl -L https://github.com/vezzi/FRC_align/archive/master.zip -o frcbam.zip")
            os.system("unzip frcbam.zip")
            os.system("mv FRC_align-master ./Utilities/cpp/%s%s-%s%sFRCbam"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
            os.chdir("./Utilities/cpp/%s%s-%s%sFRCbam/src/samtools"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
            os.system("make")
            os.chdir("%s/Utilities/cpp/%s%s-%s%sFRCbam"%(METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep))
            boostFlags = ""
            if os.path.exists("/opt/local/lib/libboost_system-mt.a"):
               os.environ["LDFLAGS"]="-L/opt/local/lib -lboost_system-mt"
            elif os.path.exists("/opt/local/lib/libboost_system.a"):
               os.environ["LDFLAGS"]="-L/opt/local/lib -lboost_system"
            elif os.path.exists("/usr/lib/libboost_system-mt.a"):
               os.environ["LDFLAGS"]="-L/usr/lib -lboost_system-mt"
            elif os.path.exists("/usr/lib/libboost_system.a"):
               os.environ["LDFLAGS"]="-L/usr/lib -lboost_system"
            else:
               # install boost ourselves
               os.system("curl -L http://sourceforge.net/projects/boost/files/boost/1.49.0/boost_1_49_0.tar.gz -o boost.tar.gz")
               os.system("tar xvzf boost.tar.gz")
               os.chdir("boost_1_49_0")
               os.system("sh bootstrap.sh")
               os.system("./b2 install --prefix=`pwd`/build threading=multi")
               ldflags = "-L%s/build/lib -lboost_system"%(os.getcwd())
               if os.path.exists("%s/build/lib/libboost_system-mt.a"%(os.getcwd())):
                  ldflags = "-L%s/build/lib -lboost_system-mt"%(os.getcwd())
               os.environ["LDFLAGS"]=ldflags
               os.environ["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"] + os.pathsep + "%s/build/lib"%(os.getcwd())
               boostFlags = "--with-boost=%s/build/ --disable-shared --enable-static-boost --enable-static-FRC"%(os.getcwd())
               os.chdir("..")
               os.system("rm -rf boost.tar.gz")
    
            os.system("./configure --prefix=%s/Utilities/cpp/%s%s-%s%sFRCbam/ %s"%(METAMOS_ROOT, os.sep, OSTYPE, MACHINETYPE, os.sep, boostFlags))
            os.system("make install")
            if boostFlags != "":
               os.system("cp boost_1_49_0/build/lib/* ./bin")

            os.chdir("%s"%(METAMOS_ROOT))
            os.system("rm -rf frcbam.zip")

    if not os.path.exists("./Utilities/cpp/%s%s-%s%sALE"%(os.sep, OSTYPE, MACHINETYPE, os.sep)):
        if "ale" in packagesToInstall:
           dl = 'y'
        else:
           print "ALE tool not found, optional for Validate step, download now?"
           dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
           os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/ale.tar.gz -o ale.tar.gz")
           os.system("tar xvzf ale.tar.gz")
           os.system("mv ALE ./Utilities/cpp/%s%s-%s%sALE"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
           os.chdir("./Utilities/cpp/%s%s-%s%sALE/src"%(os.sep, OSTYPE, MACHINETYPE, os.sep))
           os.system("make all") 
           os.chdir("%s"%(METAMOS_ROOT))
           os.system("rm -rf ale.tar.gz")

if "deprecated" in enabledWorkflows or manual:
    if not os.path.exists("./Utilities/glimmer-mg"):
        if "glimmer-mg" in packagesToInstall:
           dl = 'y'
        else:
           print "Glimmer-MG not found, optional for FindORFS step. Caution, this will take approx. 24 hours to complete, including Phymm download & install. download & install now?"
           dl = raw_input("Enter Y/N: ")
        if dl == 'y' or dl == 'Y':
            archive = "glimmer-mg-0.3.1.tar.gz"
            os.system("curl -L ftp://ftp.cbcb.umd.edu/pub/data/metamos/%s -o %s" %(archive, archive))
            os.system("tar -C ./Utilities/ -xvf %s" % archive)
            os.system("rm %s"%archive)
            os.system("python ./Utilities/glimmer-mg/install_glimmer.py")

# should check for success of installation
workflow.updateSupportedWorkflows(enabledWorkflows)

sys.path.append(METAMOS_ROOT + os.sep + "Utilities" + os.sep + "python")
from get_setuptools import use_setuptools
use_setuptools()

print "Run setup.py.."
os.system("python setup.py install_scripts --install-dir=`pwd` build_ext")
#print "Compile & optimize"
#distutils.util.byte_compile(['./runPipeline.py'],optimize=2,force=True)
#os.system("chmod a+wrx runPipeline.pyo")
os.system("mv runPipeline.py runPipeline")
os.system("mv initPipeline.py initPipeline")

#remove imports from pth file, if exists                                                                                                                                                          
nf = []
try:
    dir1 = utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib"+os.sep+"python"
    if not os.path.exists(dir1+os.sep+"easy-install.pth"):
        dir1 = utils.INITIAL_UTILS+os.sep+"python"+os.sep+"lib64"+os.sep+"python"

    nf = open(dir1+os.sep+"easy-install.pth",'r')
    ndata = []
    for line in nf.xreadlines():
        if "import" in line:
            continue
        ndata.append(line)
    nf.close()
    nfo = open(dir1+os.sep+"easy-install.pth",'w')
    for line in ndata:
        nfo.write(line)
    nfo.close()
except IOError:
    pass

validate_install = 0
if validate_install:
    rt = check_install.validate_dir(METAMOS_ROOT,'required_file_list.txt')
    if rt == -1:
        print "MetAMOS not properly installed, please reinstall or contact development team for assistance"
        sys.exit(1)
    
