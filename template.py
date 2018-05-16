#! /usr/bin/env python3.4
#! -*- coding: utf-8 -*-
'''
Created on 27 lip 2015
@author: kamil.karczewski
'''

# #############################################################################
# standard phyton modules
# #############################################################################
import os            # standard os lib
import sys           # standard sys lib
import cvs           # standard cvs lib for cvs file I/O
import string        # standard string lib
import getpass       # standard gepass lib to hiding password
import argparse      # standard argparse lib to manage args from cmd
import subprocess    # standard subprocess lib to executing bash commend thru python

# #############################################################################
# constants, global variables
# #############################################################################
NAME = __file__
SPLIT_DIR = os.path.dirname(os.path.realpath(NAME))
SCRIPT_DIR = SPLIT_DIR + '/.' + os.path.basename(NAME)
LIB_DIR = SCRIPT_DIR + '/cache/lib/'
sys.path.insert(0, LIB_DIR)

# #############################################################################
# Third party phyton modules - list with procedure to install and import them
# #############################################################################
# After first installation check for rigth package name in LIB_DIR for third column
# Bug for third party libs - workaround - After first installation it need to rerun the script.
# Don't know why, still under investigation.
import_list = [
   ('sqlalchemy', '1.2.7', 'SQLAlchemy-1.2.7-py3.6.egg-info'),   # Database connector
   ('pymysql',    '0.8.1', 'PyMySQL-0.8.1.dist-info'),           # Database driver
   ('paramiko',   '2.4.1', 'paramiko-2.4.1.dist-info'),          # SSH connector
   ('lxml',       '4.2.1', 'lxml-4.2.1.dist-info'),              # XML toolkit
   ('colorama',   '0.3.3', 'colorama-0.3.3-py3.6.egg-info')      # Colloring output
]

for line in import_list:
   try:
      if os.path.isdir(LIB_DIR+line[2]):
         pass
         #print('Found installed '+line[0]+line[1]+' in '+line[2])
      else:
         try:
            import pip
         except:
            print("For debian - Use sudo apt-get install python3-pip")
            print("For centos/redhat - use  yum -y install python36u-pip")
            #TO DO - change script to use get-pip unless installing pip as root
            # Probably solution for problem with installing pip.
            # https://github.com/pypa/get-pip
            sys.exit(1)
         print('No lib '+line[0]+'-'+line[1])
         os.system("python"+sys.version[0:3]+" -m pip install '"+line[0]+'=='+line[1]+"' --target="+LIB_DIR+" -b "+TMP_DIR)
      module_obj = __import__(line[0])
      globals()[line[0]] = module_obj
   except ImportError as e:
      print(line[0]+' is not installed')

# #############################################################################
# functions
# #############################################################################

def read_file(file_name):
   '''
   Read from file line by line
   '''
   try:
      with open(file_name, 'r') as file:
         lines = [line.rstrip('\n') for line in file]
   except (IOError, OSError):
      print_err(str(sys.stderr) + "\nCan't open file.")
      sys.exit(1)
   return lines

def read_file_no_comments(file_name):
   '''
   Read from file line by line excluding comments
   '''
   try:
      with open(file_name, 'r') as file:
         templines = [line.rstrip('\n') for line in file]
         lines=([])
         for line in templines:
            if not line.startswith('#'):
               lines.append(line)
   except (IOError, OSError):
      print_err(str(sys.stderr) + "\nCan't open file.")
      sys.exit(1)
   return lines

def write_file(path_to_conf,file_name,data):
   '''
   Write to file line by line.
   '''
   if isinstance(data, str):
      data = data.split('\n')
   if os.path.exists(path_to_conf):
      try:
         with open(path_to_conf+file_name,'w') as fileout:
            for line in data:
               fileout.writelines(line+'\n')
      except(IOError,OSError):
         print_err("Can't write to file.")
         sys.exit(1)
   else:
      print_err("Can't write to file. There are no path that you specified")

def print_ok(output):
   '''
   Green coloring if everything in ok.
   '''
   print(colorama.Fore.GREEN+output,colorama.Fore.RESET)

def print_err(error):
   '''
   Red coloring for errors.
   '''
   print(colorama.Fore.RED,+error,colorama.Fore.RESET)

def print_war(warning):
   '''
   Yellow coloring for warnings.
   '''
   print(colorama.Fore.YELLOW+warning,colorama.Fore.RESET)

def csv_write(file_name, limit, data):
   '''
   CSV write example.
   '''
   if isinstance(data, str):
      data = data.split('\n')
   with open(file_name, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=limit)
      for line in data:
         writer.writerow(line)

def csv_read(file_name, temp):
   '''
   CSV read example.
   '''
   with open(file_name, 'r', newline='') as csvfile:
      readed = csv.reader(csvfile, delimiter=temp)
      return readed
      
def cmd_over_ssh(server,loginssh,cmd):
   '''
   Paramiko simple example.
   '''
   try:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(server,port=22,username=loginssh,password=getpass.getpass('SSH Password: '))
      stdin,stdout,stderr = ssh.exec_command(cmd)
      output = stdout.readlines()
      error = stderr.readlines()
      if error:
         for line in error:
            print_err(line)
      else:
         for line in output:
            print_ok(line)
      ssh.close()
   except Exception as e:
      print_err(e)
      
def simple_query(query, params):
   '''
   SQLAlchemy simple example.
   '''
   engine = sqlalchemy.create_engine(engine_text)
   # engine = create_engine(dialect+driver://username:password@host:port/database)
   connection = engine.connect()
   if params is None:
      result = connection.execute(query)
   else:
      result = connection.execute(query, param1=params, param2=params, param3=params)
   connection.close()
   return result

def execute_cmd(list_of_cmd):
   result = dict()
   if isinstance(list_of_cmd, str):
      list_of_cmd = [list_of_cmd]
   proc = subprocess.Popen(list_of_cmd,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=True)
   (stdout,stderr) = proc.communicate()

   if proc.returncode == 0 and stderr.decode('ascii') == '':
      result['stdout'] = stdout.decode('ascii').split('\n')
   else:
      result['exit_code'] = proc.returncode
      result['stderr'] = stderr.decode('ascii')
      result['command'] = list_of_cmd
   return result

def read_xml_file(path):
   '''
   XML file reader.
   '''
   try:
      tree = etree.parse(path)
      root = tree.getroot()
      return root
   except IOError as e:
      print('Problem with file or filepath.')
      print(e)

# #############################################################################
# operations
# #############################################################################

def opt_db_engine(args):
   global engine_text
   config = dict(user=args.user, host=args.host, port=args.port, password=args.password, schema=args.schema)
   if not 'schema' in args:
      sys.exit(print_err("Database schema is required."))
   else:
      config['schema'] = args.schema
   if args.password == None:
      config['password'] = getpass.getpass('Password to database: ')
   else:
      config['password'] = args.password
   temp = string.Template('mysql+pymysql://$user:$password@$host$port/$schema')
   engine_text = temp.safe_substitute(config)
   #OLD VERSION NEEDS SPECIFIED SOCKET TO CONNECT WITH LOCALHOST
   #if 'localhost' in engine_text:
   #   engine_text+='?unix_socket=/var/run/mysqld/mysqld.sock'

def opt_read_file(in_file):
   print(read_file(in_file))

def opt_read_ex_comment(in_file):
   print(read_file_no_comments(in_file))

def opt_write_file(out_file):
   data = 'aergqwergwer\nasdfaweqwzn\nline3\nline4\n#comment'
   write_file('./',out_file,data)
   data2 = ['fasdfasdf','asdfwergwe','line100','line10000']
   write_file('./','second_file',data2)

def opt_write_csv(file_name):
   data = [['asd','gfadfgd','fgarsdfgf'],['qae','qwr','wer'],['line3','1','2'],['line4','4','#comment']]
   csv_write(file_name,';',data)
   data2 = [['fasdfasdf'],['asdfwergwe'],['line100'],['line10000']]
   csv_write(file_name+'2',';',data2)

def opt_read_csv(file_name):
   print(csv_read(file_name, ';'))
   for one in csv_read(file_name,';'):
      print(one)

def opt_paramiko(args):
   cmd_over_ssh(args[0],args[1],args[2])

def opt_sqlalchemy(args):
   '''
   Test usage and printing output.
   '''
   opt_db_engine(args) #move to if:elif: for argparse in place where we use database
   query = sqlalchemy.text(args.sqlalchemy)
   response = simple_query(query, None)
   print(response)
   for row in response:
      print(row[1],row[0],row[2])

def opt_subprocess(cmd):
   response = execute_cmd([cmd])
   print(response)

def opt_read_xml(file_name):
   xml_file = read_xml_file(file_name)
   print(etree.tostring(root, pretty_print=True).decode('ascii'))
  
def opt_help():
   parser.print_help()
   msg = 'Printdded help'
   return msg

# #############################################################################
# main app function - reading arguments with argpars
# #############################################################################

def main():
   parser = argparse.ArgumentParser(
      prog='template.py',
      description='Description script',
      epilog='Epilog script',
      add_help=True, 
      argument_default=argparse.SUPPRESS,
      formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument('--user','-U',
      default='root',
      help = 'Database user name/login..')
   parser.add_argument('--password','-P',
      default = 'password',
      nargs='?',
      help = '''Database user password, no password as default,
if used without value you will be asked to
write password in prompt.''')
   parser.add_argument('--host','-H',
      default='localhost',
      help = 'Database url/ip address. Default localhost.')
   parser.add_argument('--port','-O',
      default='',
      help = 'Database port number.')
   parser.add_argument('--schema','-S',
      default = 'mysql',
      help = 'Database schema name.')  
   parser.add_argument('--read_file','-rf',
      help='Test reading all file content. Require file_path.')
   parser.add_argument('--read_ex_comment','-rec',
      help='Test reading file content, excluding commented lines. Require file_path')
   parser.add_argument('--write_file','-wf',
      help='Test writing to file. Require file_path.')
   parser.add_argument('--write_csv','-wc',
      help='Test writing to csv file. Require file_path.')
   parser.add_argument('--read_csv','-rc',
      help='Test reading to csv file. Require file_path.')
   parser.add_argument('--paramiko','-pa',
      nargs=3,
      help='Test executing bash command with paramiko. Required server user cmd')
   parser.add_argument('--sqlalchemy','-sql',
      help='Test connection to database. Creds are in different args. Here specify query.')
   parser.add_argument('--subprocess','-sub',
      help='Test executing bash command with subprocess. Required cmd.')
   parser.add_argument('--read_xml','-rx',
      help='Test read xml file. Required file_path.')

   argv = sys.argv[1:]
   args = parser.parse_args(argv)
   try:
      if not len(sys.argv) > 1 or 'help' in args:
         opt_help(parser)
      elif 'read_file' in args:
         opt_read_file(args.read_file)
      elif 'read_ex_comment' in args:
         opt_read_ex_comment(args.read_ex_comment)
      elif 'write_file' in args:
         opt_write_file(args.write_file)
      elif 'write_csv' in args:
         opt_write_csv(args.write_csv)
      elif 'read_csv' in args:
         opt_read_csv(args.read_csv)
      elif 'paramiko' in args:
         opt_paramiko(args.paramiko)
      elif 'sqlalchemy' in args:
         opt_sqlalchemy(args)
      elif 'subprocess' in args:
         opt_subprocess(args.subprocess)
      elif 'read_xml' in args:
         opt_read_xml(args.read_xml)
      else:
         opt_help(parser)
   except Exception as e:
      print_err(e)

if __name__ == '__main__':
   # required by lxml as it's 3rd party lib
   # and automatic import doesn't support import using 'from'
   # TO DO auto import supporting 'from lib import part'
   from lxml import etree 
   main()
