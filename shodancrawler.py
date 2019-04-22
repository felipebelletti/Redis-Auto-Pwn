import shodan, sys, subprocess

def crawler():
	try:
		api = shodan.Shodan('SUA API KEY DO SHODAN VEM AQUI')
		results = api.search(sys.argv[1])
		print('Results found: {}'.format(results['total']))
		with open("output.txt", "w") as f:
			for result in results['matches']:
				f.write(result['ip_str']+"\n")
				print result['ip_str']
	except shodan.APIError, e:
		print('Error: {}'.format(e))
		sys.exit(1)

if __name__=="__main__":
	crawler()
