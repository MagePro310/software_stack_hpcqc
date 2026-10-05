"""Demo kịch bản kiểm thử đa tiến trình / đa luồng (Concurrent HPC Clients).

Mô phỏng nhiều tác vụ HPC gửi đồng thời tới QC Server để kiểm chứng
hàng đợi FCFS (QuantumTaskQueue) điều phối và xử lý tuần tự an toàn.
"""

import argparse
import concurrent.futures
import time
from hpqc.hpc.client import QuantumClient

def submit_task(server_addr: str, client_id: int, input_data: list[int], shots: int):
    client = QuantumClient(server_addr)
    start = time.time()
    try:
        print(f"[Client {client_id}] Gửi task với input={input_data}, shots={shots}...")
        res = client.bell(inputs={"data": input_data}, shots=shots)
        duration = time.time() - start
        print(
            f"[Client {client_id}] Hoàn thành sau {duration:.3f}s | "
            f"Backend: {res['backend']} | Decoded: {res['result']['decoded_output']} | "
            f"Counts: {res['result']['counts']}"
        )
        return client_id, duration, res
    finally:
        client.close()

def main():
    parser = argparse.ArgumentParser(description="Demo HPC-QC Concurrent Task Queue")
    parser.add_argument("--server", default="localhost:50051", help="QC Server address (host:port)")
    args = parser.parse_args()

    print(f"=== Bắt đầu Demo kiểm thử đồng thời tới QC Server ({args.server}) ===")
    test_cases = [
        (1, [0, 0], 2000),
        (2, [0, 1], 2000),
        (3, [1, 0], 2000),
        (4, [1, 1], 2000),
    ]

    start_total = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(submit_task, args.server, cid, data, shots)
            for cid, data, shots in test_cases
        ]
        concurrent.futures.wait(futures)

    total_time = time.time() - start_total
    print(f"\n=== Tất cả {len(test_cases)} tasks đã hoàn thành trong {total_time:.3f}s ===")

if __name__ == "__main__":
    main()
