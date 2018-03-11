import numpy as np
import sys
import csv
import pandas as pd
import itertools
import time
#Global Variables
min_sup = 0.01
mod = 2


def generateHashTree(C, k):
	hashtree = {}
	temp = {}
	temp = hashtree
	list_counts = []
	for itemset in C:
		temp = hashtree
		for i in range(0, k-1):
			if itemset[i]%mod in temp:
				temp = temp[itemset[i]%mod]
			else:
				temp[itemset[i]%mod] = {}
				temp = temp[itemset[i]%mod]
		if itemset[k-1]%mod in temp:
			a = [itemset, 0]
			temp[itemset[k-1]%mod].append(a)
			list_counts.append(a)
		else:
			temp[itemset[k-1]%mod] = []
			a = [itemset, 0]
			temp[itemset[k-1]%mod].append(a)
			list_counts.append(a)
	return hashtree, list_counts


def isContained(itemset, Hashtree, k):
	#write the function here which checks if the k-itemset is present in the hashtree
	temp = Hashtree
	for i in range(0, k):
		if itemset[i]%mod in temp:
			temp = temp[itemset[i]%mod]
		else: 
			return False
	for search_item in temp:
		if(itemset == search_item[0]):
			if(search_item[1]>min_sup * num_transactions):
				return True
			else:
				return False
	return False


def gen_ksubsets(itemset, k):
	subsets = []
	for i in itemset:
		s = []
		for j in itemset:
			if(j==i):
				continue
			else:
				s.append(j)
		subsets.append(s)
	return subsets


def apriori_gen(F, k, Hashtree):
	if(k==1):
		C = []
		for i1 in range(0, len(F)):
			for i2 in range(i1+1, len(F)):
				Ck = []
				Ck.append(min(F[i1], F[i2]))
				Ck.append(max(F[i1], F[i2]))
				C.append(Ck)
		#Np pruning required in this case
		return C


	else:	
		C = []
		#insertion into C_k using self_joining
		for i1 in range(0, len(F)):
			for i2 in range(i1+1, len(F)):
				j=0
				while(j<k-1):
					if(F[i1][j]!=F[i2][j]):
						break
					j+=1
				if(j==k-1):
					Ck = []
					for j in range(0, k-1):
						Ck.append(F[i1][j])
					Ck.append(min(F[i1][k-1], F[i2][k-1]))
					Ck.append(max(F[i1][k-1], F[i2][k-1]))
					C.append(Ck)
		#Pruning step
		for itemset in C:
			for ksubset in gen_ksubsets(itemset, k+1):
				if(isContained(ksubset, Hashtree, k)==False):
					C.remove(itemset)
					break
		return C

def update_counts(transactions, hashtree, k):
	#generate all k subsets transactions and update counts
	for transaction in transactions:
		k_subset_list = list(itertools.combinations(transaction, k))
		temp = hashtree
		for ksubset in k_subset_list:
			temp = hashtree
			i=0
			while(i<k):
				if(ksubset[i]%mod in temp):
					temp = temp[ksubset[i]%mod]
				else:
					break
				i+=1
			if(i==k):
				for search_item in temp:
					if(list(ksubset)==search_item[0]):
						search_item[1]+=1
						
	



transactions = []
file_reader = open('retail.dat')
for line in file_reader:
	l = [int(x) for x in line.split()]
	transactions.append(l)
C = []
F = []
max_id = -1
global num_transactions
num_transactions = len(transactions)
for transaction in transactions:
	transaction.sort()
	for id in transaction:
		if(id>max_id):
			max_id = id
count = [0]*(max_id+1)
for transaction in transactions:
	for id in transaction:
		count[id]+=1
new_transactions=[]
for ls in transactions:
	l=[]
	for item in ls:
		if(count[item]>=min_sup*num_transactions):
			l.append(item)
	new_transactions.append(l)
transactions = new_transactions.copy()
new_transactions.clear()

start = time.clock()
F1=[] #Frequent 1-itemset
C1 = []
for i in range(0, len(count)):
	C1.append(i)
	if(count[i] >= min_sup* num_transactions):
		F1.append(i)
F.append(F1)
C.append(C1)
Freq_k = F1
k=2
oldHashTree = {}
print(*F1,sep='\n')
for i in range(0, mod):
	oldHashTree[i]=[]
for i in range(1, max_id+1):
	oldHashTree[i%mod].append([i, count[i]])


while(len(Freq_k)!=0):
	Candidate_gen = apriori_gen(Freq_k, k-1, oldHashTree)
	#print(Candidate_gen)
	if(len(Candidate_gen)==0):
		break
	newHashTree, list_counts = generateHashTree(Candidate_gen, k)
	update_counts(transactions, newHashTree, k)
	Freq_k = []
	for item in list_counts:
		if(item[1]>=min_sup*num_transactions):
			Freq_k.append(item[0])
	print(k)
	print(*Freq_k, sep='\n')
	F.append(Freq_k)
	k+=1
	oldHashTree = newHashTree.copy()
	newHashTree.clear()
end = time.clock() - start
print(end)

