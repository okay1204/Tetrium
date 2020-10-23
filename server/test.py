import pickle

z =  pickle.dumps('hello')

print(z)


y = pickle.loads('hello')
print(y)