#!/bin/zsh

TIMEFMT=$'%*U\n%*S'

echo "This is the Benchmark for CAN201 Networking Assessment."
echo "starting..."

while getopts n:p:d:s: opt
do
	case "${opt}" in
		n)	n=${OPTARG};;		# the number of files.
		p)	ip=${OPTARG};;		# the ip address of server.
		d)	id=${OPTARG};;		# the student id.
		s)	size=${OPTARG};;	# the size of a file. (500K/10M/1G/...)
	esac
done

BM_DIR=./Benchmark
test -d $BM_DIR || mkdir $BM_DIR
cd $BM_DIR || exit

echo "1. Generating $n random binary file(s)"
for ((i=1; i<=$n; i++))
do
	perl -ne 'print unpack("b*")' < /dev/urandom | head -c$size > file$i.bin
	
	md5sum file$i.bin >> md5.txt
done

echo "2. Transferring $n random binary file(s)"
for ((i=1; i<=$n; i++))
do
	{ time python ../client.py --server_ip $ip --id $id --f ./file$i.bin; } >> result.txt 2>> time.txt
done

echo "closing..."
