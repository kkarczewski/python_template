#! /usr/bin/env python3.4
#! -*- coding: utf-8 -*-
'''
Created on 27 lip 2015

@author: kamil.karczewski
'''

# #############################################################################
# standard phyton modules
# #############################################################################
import os
import sys
import string
import argparse
import subprocess

# #############################################################################
# constants, global variables
# #############################################################################
NAME = __file__
TEMP_PATH = SCRIPT_DIR+'/cache/'
SPLIT_DIR = os.path.dirname(os.path.realpath(NAME))
SCRIPT_DIR = SPLIT_DIR + '/.' + os.path.basename(NAME)
LIB_DIR = SCRIPT_DIR + '/cache/lib/'
TMP_DIR = SPLIT_DIR + '/tmp/'
sys.path.insert(0, LIB_DIR)

# List of lib to install
import_list = [
   ('sqlalchemy', '1.0.8', 'SQLAlchemy-1.0.8.egg-info'),
   ('paramiko', '1.15.2', 'paramiko-1.15.2.dist-info'),
   ('colorama', '0.3.3', 'colorama-0.3.3.egg-info'),
   ('pymysql', '0.6.7', 'PyMySQL-0.6.7.dist-info')]
for line in import_list:
   try:
      if os.path.isdir(LIB_DIR+line[2]):
         pass
         #print('Found installed '+line[0]+line[1]+' in '+line[2])
      else:
         try:
            import pip
         except:
            print("Use sudo apt-get install python3-pip")
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
# Read from file line by line
def read_file(file_name):
   try:
      with open(file_name, 'r') as file:
         lines = [line.rstrip('\n') for line in file]
   except (IOError, OSError):
      print >> sys.stderr, "Can't open file."
      sys.exit(1)
   return lines

# Read from file line by line excluding comments
def read_file_no_comments(file_name):
   try:
      with open(file_name, 'r') as file:
         templines = [line.rstrip('\n') for line in file]
         lines=([])
         for line in templines:
            if not line.startswith('#'):
               lines.append(line)
   except (IOError, OSError):
      print >> sys.stderr, "Can't open file."
      sys.exit(1)
   return lines

# Write to file line by line.
def write_file(path_to_conf,file_name,data):
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

# Green coloring if everything in ok
def print_ok(output):
   print(colorama.Fore.GREEN+output,colorama.Fore.RESET)

# Red coloring for errors
def print_err(error):
   print(colorama.Fore.RED,+error,colorama.Fore.RESET)

# Yellow coloring for warnings
def print_war(warning):
   print(colorama.Fore.YELLOW+warning,colorama.Fore.RESET)

# Paramiko example
def logonssh(server,loginssh,cmd):
   import getpass # in case of usege - move on the top of the file to the list of libs in use
   try:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(server,port=22,username=loginssh,password=getpass.getpass('SSH Password: '))
      stdin,stdout,stderr = ssh.exec_command(cmd)
      output = stdout.readlines()
      error = stderr.readlines()
      if error:
         for line in error:
            print(line)
      else:
         for line in output:
            print(line)
      ssh.close()
   except Exception as e:
      print(e)

# CSV write example
def csv_write(file_name, limit, data):
   import csv ## in case of usege - move on the top of the file to the list of libs in use
   with open(file_name, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=limit)
      for line in data:
         writer.writerow(line)
      #writer.writerow(['example','date','for','csv'])
      #writer.writerow(['example']*4)
# CSV read example
def csv_read(file_name, temp):
   import csv ## in case of usege - move on the top of the file to the list of libs in use
   with open(file_name, 'r', newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=temp)
      return reader
      #for row in reader:
      #   print(row)

# SQLAlchemy simple example
def simple_query(query, params):
    engine = sqlalchemy.create_engine(engine_text)
    # engine = create_engine(dialect+driver://username:password@host:port/database)
    connection = engine.connect()
    if params is None:
        result = connection.execute(query)
    else:
        result = connection.execute(query, param1=params, param2=params, param3=params)
    # for row in result:
    #     print(row)
    connection.close()
    return result

# #############################################################################
# operations
# #############################################################################

def opt_position(context, value_0):
   pass

def opt_named(context, value_0, value_1, value_2):
   pass

def opt_db_engine(args):
   import getpass # in case of usege - move on the top of the file to the list of libs in use
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
   if 'localhost' in engine_text:
      engine_text+='?unix_socket=/var/run/mysqld/mysqld.sock'
def test():
   # Testowe wydruki
   lines = ['ls -l','mkdir test','ls -la','touch plik']
   lines = readfile('sza.txt')
   ERROR_FLAG,done_cmd,out = os_call(*lines,progress_char='*',verbose=2)
   logonssh('dev.justnet.pl','kamil','ls -la')
   csv_write('eggs.csv',' ')
   csv_read('eggs.csv',' ')
   opt_db_engine(args) # przenieść do if:elif: w miejscu w którym używamy bazy
   query0 = text("SELECT COUNT(id) FROM history WHERE content NOT LIKE '%<object source=\"Client\">%' AND src LIKE 'DATASOURCE' AND table_name LIKE 'Client%'")
   count = simple_query(query0, None)
   for one in count:
      for two in one:
         print('Ilość rekordów: ', two)

def opt_help():
   parser.print_help()
   msg = 'Printed help'
   msg = (base64.b64encode(('Printed help').encode(OUTPUT_ENCODING))).decode(OUTPUT_ENCODING)
   return msg

# #############################################################################
# main app 
# #############################################################################

def main():
   # Reading arguments
   #Uncomment in case of usage db connection.
   #try:
   #   #Bug with sqlalchemy. Workaround After first installation it has to be imported twice.
   #   #Don't know why, still under investigation.
   #   from sqlalchemy.sql import text
   #except Exception as e:
   #   print_err('No sqlalchemy installation')
   #   print_err(e)
   parser = argparse.ArgumentParser(
      prog='template.py',
      description='Description script',
      epilog='Epilog script',
      add_help=True, 
      argument_default=argparse.SUPPRESS,
      formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument('--user','-U',
      default='jsql',
      help = 'Database user name/login..')
   parser.add_argument('--password','-P',
      default = 'qazxcdews',
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
      default = 'psm_sza_current',
      help = 'Database schema name.')
   parser.add_argument('arg-position',
      nargs='?',
      help='label under which the data will be saved')
   parser.add_argument('--arg-named','-a',
      action='store_true',
      help='show list with data')
   subparsers = parser.add_subparsers()
   parser_subone = subparsers.add_parser('sub-arg',help='Decription subone')
   parser_subone.add_argument('sub-arg',
      nargs='?',
      help='Description subone')
   argv = sys.argv[1:]
   args = parser.parse_args(argv)
   try:
      if not len(sys.argv) > 1 or 'help' in args:
         opt_help()
      elif 'test' in args:
         opt_test()
      #elif 'arg_position' in args:
      #   opt_position(ctx, args.arg_position)
      #elif 'arg_named' in args:
      #   opt_some(ctx, args.arg_named, 'none', -1)
      #elif 'sub-arg' in args:
      #   opt_some(ctx,args.sub-arg,'none',-1)      
      else:
         opt_help()
   except Exception as e:
      cmd = str()
      for one_arg in sys.argv:
         cmd+=one_arg+' '
      list_cmd=list()
      list_cmd.append(cmd)
      err_msg = str(e)
      my_logger('T',list_cmd,err_msg)
      print(e)
   

if __name__ == '__main__':
   main()

