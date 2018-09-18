import os
import sys

def main():
	dir = sys.argv[1]
	filelist = os.listdir(dir)
	print(len(filelist))

if __name__=='__main__':
	main()
