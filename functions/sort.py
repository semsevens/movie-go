from __future__ import division	 #
import operator


#confirm the maximum key-value in the first place in list
def MakeMaxHeap(rows, key, E, S):	
	for i in range((E-S)//2 - 1, -1, -1):
		t = i + S
		m = 2*i + 1 + S
		n = 2*i + 2 + S
		if operator.lt(rows[t][key], rows[m][key]):
			# swap(rows[t], rows[m])
			temp = rows[t]
			rows[t] = rows[m]
			rows[m] = temp
		if operator.lt(n, E) and operator.lt(rows[t][key], rows[n][key]):
			# swap(rows[i], rows[n])
			temp = rows[t]
			rows[t] = rows[n]
			rows[n] = temp

#exchange key-value in the first place and the last place in the list	
def heapsort(rows, divs, key, E, S):   #E-endpoint  S-startpoint
	mark = E - 1
	for i in range(E - 1, S, -1):
		temp = rows[i]
		rows[i] = rows[S]
		rows[S] = temp
		#compare with the newest highest key-value
		#occur difference
		#mark the boundary's position for the next sort
		if rows[mark][key] != rows[i][key]:
			divs.append(mark)
		mark = i
		MakeMaxHeap(rows, key, i, S)

#heapsort in each bucket in one key-value
#update new buckets for the other key-value
def multipleKeySort(rows, keys):
	divs = []
	divs.append(0)
	divs.append(len(rows))
	for key in keys:
		divs.sort()
		for i in range(len(divs) - 1, 0, -1):
			MakeMaxHeap(rows, key, divs[i], divs[i - 1])
			heapsort(rows, divs, key, divs[i], divs[i - 1])
