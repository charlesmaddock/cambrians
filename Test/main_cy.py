import timeit

cy = timeit.timeit('helloWorld_cy.test(5000)', setup = 'import helloWorld_cy', number = 1000)
py = timeit.timeit('helloWorld_py.test(5000)', setup = 'import helloWorld_py', number = 1000)

print(cy, py)
print('Cython is {}x faster than Python'.format(py/cy))