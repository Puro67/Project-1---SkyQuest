#P1
name = "NhatThanh"
student_id = "MUH115170"
date_returned = "14.10.2026"

import matplotlib.pyplot as plt
import labx as mx

x = np.arange(-10, 10, 0.001)
y = mx.lab_1_problem_1(x, student_id)

plt.figure(figsize=(10, 5))
plt.plot(x, y)
plt.title(f"Function f(x) for student {student_id}")
plt.xlabel("x")
plt.ylabel("f(x)")
plt.grid(True)
plt.show()

#P2
plt.figure(figsize=(7, 5))
plt.plot(x, y)
plt.xlim(-7.5, -6.5)
plt.ylim(0, 2)
plt.axhline(y=1, color='r', linestyle='--')
plt.xlabel("x")
plt.ylabel("f(x)")
plt.title("Point 1 - Zoomed view")
plt.grid(True)
plt.show()

plt.figure(figsize=(7, 5))
plt.plot(x, y)
plt.xlim(0, 1)
plt.ylim(0, 2)
plt.axhline(y=1, color='r', linestyle='--')
plt.xlabel("x")
plt.ylabel("f(x)")
plt.title("Point 2 - Zoomed view")
plt.grid(True)
plt.show()