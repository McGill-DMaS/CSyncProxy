import matplotlib.pyplot as plt
values = [0.5003128760529482, 0.4976052948255113, 0.4949458483754514, 0.49016847172081823, 0.487581227436823,
          0.46878459687123936, 0.4408664259927797, 0.41211793020457277, 0.3845126353790615]
x = epsilon = [0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1]
y = values

plt.figure(figsize=(8, 6))
plt.plot(x, y)
plt.xlabel('Privacy budget $\epsilon$', fontsize=18)
plt.ylabel('Probability of successful anonymization', fontsize=18)
plt.grid(True)
plt.savefig('epsilon_values.png')
plt.show()
