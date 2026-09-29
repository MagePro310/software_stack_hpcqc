import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import RYGate
from qiskit.quantum_info import Statevector

# 1. Khởi tạo và chuẩn hóa dữ liệu
data = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=float)
norm = np.linalg.norm(data)
x = data / norm  # x là vector biên độ đã chuẩn hóa

print("Vector gốc cần đạt được:")
print(np.round(x, 4))
print("-" * 50)

# 2. Khởi tạo mạch lượng tử 3 qubit
qc = QuantumCircuit(3)

# ==========================================
# BƯỚC 1: Xoay Qubit 2 (Qubit cao nhất - MSB)
# Phân nhánh mảng làm 2 nửa: [0,1,2,3] và [4,5,6,7]
# ==========================================
prob_q2_1 = np.sum(x[4:8]**2) # Xác suất nhánh q2 = 1 (các phần tử 4->7)
angle_q2 = 2 * np.arcsin(np.sqrt(prob_q2_1))
qc.ry(angle_q2, 2)


# ==========================================
# BƯỚC 2: Xoay Qubit 1 (Điều khiển bởi Qubit 2)
# Phân nhánh tiếp thành các nhóm 2 phần tử
# ==========================================
# 2.1 Nhánh q2 = 0 (Điều khiển anti-control bằng cổng X)
prob_q2_0 = np.sum(x[0:4]**2)
prob_q1_1_given_q2_0 = np.sum(x[2:4]**2) / prob_q2_0
angle_q1_0 = 2 * np.arcsin(np.sqrt(prob_q1_1_given_q2_0))

qc.x(2)  # Đảo trạng thái q2 để làm anti-control (kích hoạt khi q2=0)
qc.cry(angle_q1_0, 2, 1)
qc.x(2)  # Trả lại trạng thái q2

# 2.2 Nhánh q2 = 1 (Điều khiển control bình thường)
prob_q1_1_given_q2_1 = np.sum(x[6:8]**2) / prob_q2_1
angle_q1_1 = 2 * np.arcsin(np.sqrt(prob_q1_1_given_q2_1))

qc.cry(angle_q1_1, 2, 1)


# ==========================================
# BƯỚC 3: Xoay Qubit 0 (Điều khiển bởi Qubit 2 và Qubit 1)
# Tính giá trị lá cuối cùng cho từng phần tử
# ==========================================
# 3.1 Nhánh 00 (q2=0, q1=0) -> Quyết định giữa x[0] và x[1]
prob_q1_q0_00 = x[0]**2 + x[1]**2
angle_q0_00 = 2 * np.arcsin(np.sqrt(x[1]**2 / prob_q1_q0_00))
qc.x([1, 2])
qc.append(RYGate(angle_q0_00).control(2), [2, 1, 0]) # CC-RY target=0, ctrl=2,1
qc.x([1, 2])

# 3.2 Nhánh 01 (q2=0, q1=1) -> Quyết định giữa x[2] và x[3]
prob_q1_q0_01 = x[2]**2 + x[3]**2
angle_q0_01 = 2 * np.arcsin(np.sqrt(x[3]**2 / prob_q1_q0_01))
qc.x(2) # Kích hoạt khi q2=0, q1=1
qc.append(RYGate(angle_q0_01).control(2), [2, 1, 0])
qc.x(2)

# 3.3 Nhánh 10 (q2=1, q1=0) -> Quyết định giữa x[4] và x[5]
prob_q1_q0_10 = x[4]**2 + x[5]**2
angle_q0_10 = 2 * np.arcsin(np.sqrt(x[5]**2 / prob_q1_q0_10))
qc.x(1) # Kích hoạt khi q2=1, q1=0
qc.append(RYGate(angle_q0_10).control(2), [2, 1, 0])
qc.x(1)

# 3.4 Nhánh 11 (q2=1, q1=1) -> Quyết định giữa x[6] và x[7]
prob_q1_q0_11 = x[6]**2 + x[7]**2
angle_q0_11 = 2 * np.arcsin(np.sqrt(x[7]**2 / prob_q1_q0_11))
qc.append(RYGate(angle_q0_11).control(2), [2, 1, 0]) # Kích hoạt khi q2=1, q1=1


# ==========================================
# KIỂM TRA ĐẦU RA
# ==========================================
print("Trạng thái từ việc ghép cổng lượng tử:")
state = Statevector(qc)
# Loại bỏ phần ảo (thường là 0j do ta chỉ dùng cổng R_y thực)
print(np.round(state.data.real, 4))

print("-" * 50)
print("Sơ đồ mạch (chỉ in văn bản):")
print(qc.draw('text'))
print(qc.depth())