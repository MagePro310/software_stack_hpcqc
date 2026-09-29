import time
from hpqc.hpc.client import QuantumClient

def main():
    # 1. Khởi tạo kết nối gRPC tới QC Server
    # Thay 'localhost:50051' bằng IP của máy QC nếu chạy khác máy (VD: '10.0.0.20:50051')
    print("Đang kết nối tới QC Server tại localhost:50051...")
    qc = QuantumClient("localhost:50051")
    
    try:
        # --- Ví dụ 1: Chạy Bell circuit cơ bản không truyền data ---
        print("\n--- Ví dụ 1: Bell Circuit cơ bản ---")
        start_time = time.time()
        
        # Gửi request tới server
        result1 = qc.bell(shots=10000000)
        
        elapsed_time = time.time() - start_time
        print(f"Thời gian thực thi: {elapsed_time:.4f}s")
        print("Backend thực thi:", result1["backend"])
        print("Kết quả (Counts):", result1["result"]["counts"])


        # --- Ví dụ 2: Chạy Bell circuit có truyền data để Encoding ---
        # Data này sẽ được BasisEncoder xử lý để lật bit trước khi chạy lõi Bell
        print("\n--- Ví dụ 2: Bell Circuit kèm Encoding Data ---")
        
        # Dữ liệu cổ điển muốn encode, ví dụ 'data': [1, 0] 
        # Sẽ áp dụng cổng X lên qubit thứ 0
        input_data = {
            "data": [1, 0] 
        }
        
        start_time = time.time()
        
        # Gửi request tới server kèm data
        result2 = qc.bell(inputs=input_data, shots=10000000)
        
        elapsed_time = time.time() - start_time
        print(f"Thời gian thực thi: {elapsed_time:.4f}s")
        print("Backend thực thi:", result2["backend"])
        print("Kết quả (Counts):", result2["result"]["counts"])
       
    finally:
        # 3. Đóng kết nối
        qc.close()
        print("\nĐã đóng kết nối gRPC.")

if __name__ == "__main__":
    main()
