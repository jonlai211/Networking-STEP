#!/bin/bash

echo "This is the Benchmark for CAN201 Networking Assessment."
echo "starting..."

BM_DIR=./Benchmark
test -d $BM_DIR || mkdir $BM_DIR

echo "1. Generating $1 random binary file(s)"
for ((i=1; i<=$1; i++))
do
	perl -ne 'print unpack("b*")' < /dev/urandom | head -c1M > ./$BM_DIR/file$i.bin
done

echo "2. Transferring "
for ((i=1; i<=$1; i++))
do
	python client.py --server_ip 127.0.0.1 --id 2034590 --f file.bin
done

echo "closing..."
