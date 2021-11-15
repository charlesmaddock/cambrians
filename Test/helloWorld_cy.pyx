cpdef int test(int x):
	cdef int count = 0
	cdef int i
	for i in range(x):
		count += i
		print(count)
	print('Cython done!')
	return count
