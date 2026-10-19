import subprocess
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
r="/usr/local/lib/python3.13/dist-packages/nvidia/cu13"
print(sh(f"ls {r}; ls {r}/lib | head -40; ls {r}/include | head -30; ls {r}/bin"))
print(sh(f"ls {r}/lib | grep -E 'cudart|cublas' "))
print(sh(f"ls /usr/local/lib/python3.13/dist-packages/nvidia/"))
