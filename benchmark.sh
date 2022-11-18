#!/bin/bash

echo "This is the Benchmark for CAN201 Networking Assessment."
echo "starting..."

while getopts n:ip:id: opt
do
	case "${opt}" in
		n)	n=${OPTARG};;
		p)	ip=${OPTARG};;
		d)	id=${OPTARG};;
	esac
done

BM_DIR=./Benchmark
test -d $BM_DIR || mkdir $BM_DIR
cd $BM_DIR

echo "1. Generating $n random binary file(s)"
for ((i=1; i<=$n; i++))
do
	perl -ne 'print unpack("b*")' < /dev/urandom | head -c1M > ./file$i.bin
done

echo "2. Transferring $n random binary file(s)"
for ((i=1; i<=$n; i++))
do
	time python ../client.py --server_ip ${ip} --id ${id} --f ./file$i.bin
done

echo "closing..."
