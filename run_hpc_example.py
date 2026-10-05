import argparse
import time
from hpqc.hpc.client import QuantumClient

def main():
    parser = argparse.ArgumentParser(description="HPC-QC Example Client Runner")
    parser.add_argument("--server", default="localhost:50051", help="QC Server address (default: localhost:50051)")
    parser.add_argument("--shots", type=int, default=10000, help="Number of quantum execution shots (default: 10000)")
    args = parser.parse_args()

    # 1. Khởi tạo kết nối gRPC tới QC Server
    # Thay 'localhost:50051' bằng IP của máy QC nếu chạy khác máy (VD: '10.0.0.20:50051')
    print(f"Đang kết nối tới QC Server tại {args.server}...")
    qc = QuantumClient(args.server)
    
    try:
        # --- Ví dụ 1: Chạy Bell circuit cơ bản không truyền data ---
        print("\n--- Ví dụ 1: Bell Circuit cơ bản (|Phi+> state) ---")
        start_time = time.time()
        
        # Gửi request tới server
        result1 = qc.bell(shots=args.shots)
        
        elapsed_time = time.time() - start_time
        print(f"Thời gian thực thi: {elapsed_time:.4f}s")
        print("Backend thực thi:", result1["backend"])
        print("Kết quả (Counts):", result1["result"]["counts"])
        print("Trạng thái đo phổ biến nhất (Decoded):", result1["result"].get("decoded_output"))


        # --- Ví dụ 2: Chạy Bell circuit có truyền data để Encoding ---
        # Data này sẽ được BasisEncoder xử lý để lật bit trước khi chạy lõi Bell
        print("\n--- Ví dụ 2: Bell Circuit kèm Encoding Data [0, 1] (|Psi+> state) ---")
        
        # Dữ liệu cổ điển muốn encode, ví dụ 'data': [0, 1] 
        # Sẽ áp dụng cổng X lên qubit thứ 1
        input_data = {
            "data": [0, 1] 
        }
        
        start_time = time.time()
        
        # Gửi request tới server kèm data
        result2 = qc.bell(inputs=input_data, shots=args.shots)
        
        elapsed_time = time.time() - start_time
        print(f"Thời gian thực thi: {elapsed_time:.4f}s")
        print("Backend thực thi:", result2["backend"])
        print("Kết quả (Counts):", result2["result"]["counts"])
        print("Trạng thái đo phổ biến nhất (Decoded):", result2["result"].get("decoded_output"))
       
    finally:
        # 3. Đóng kết nối
        qc.close()
        print("\nĐã đóng kết nối gRPC.")

if __name__ == "__main__":
    main()
