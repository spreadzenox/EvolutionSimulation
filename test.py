import numpy as np

input_size = 15
output_size = 6
n_layer = 4

input_test = np.random.rand(15)

weight = [np.random.randn(input_size, input_size) for i in range(n_layer)] + [
    np.random.randn(output_size, input_size)
]

for layer in weight:
    input_test = np.tanh(np.matmul(layer, input_test))
print(input_test)
