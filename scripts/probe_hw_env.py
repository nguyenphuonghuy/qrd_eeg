#!/usr/bin/env python3
"""Truy hoi lai thong tin phan cung/phan mem cua node da chay do_latency.py,
phuc vu yeu cau minor review IJRCS (CPU model, so luong, BLAS/backend,
OS, phien ban PyTorch, precision)."""
import platform, subprocess, torch

print("hostname:", platform.node())
print("OS:", platform.platform())
print("Python:", platform.python_version())
print("PyTorch:", torch.__version__)
print("torch.get_num_threads():", torch.get_num_threads())
print("torch default dtype:", torch.get_default_dtype())
try:
    print("torch.__config__.parallel_info():")
    print(torch.__config__.parallel_info())
except Exception as e:
    print("parallel_info loi:", e)
try:
    print("torch.backends.mkl.is_available():", torch.backends.mkl.is_available())
except Exception as e:
    print(e)
try:
    print("torch.backends.openmp.is_available():", torch.backends.openmp.is_available())
except Exception as e:
    print(e)

print("\n--- lscpu ---")
try:
    print(subprocess.run(["lscpu"], capture_output=True, text=True, timeout=10).stdout)
except Exception as e:
    print("lscpu loi:", e)

print("--- nproc ---")
try:
    print(subprocess.run(["nproc"], capture_output=True, text=True, timeout=10).stdout)
except Exception as e:
    print(e)
