import subprocess
import time

CONTAINER_INIT = "source /root/.bashrc && source /home/ws/ugv_ws/install/setup.bash"

def docker_exec(cmd: str) -> subprocess.Popen:
    return subprocess.Popen(
        ["docker", "exec", "ugv_jetson_ros_humble",
         "bash", "-i", "-c", f"{CONTAINER_INIT} && {cmd}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

def main():
    print("启动 SLAM 建图...")
    slam_proc = docker_exec("ros2 launch ugv_nav slam_nav.launch.py use_rviz:=false")

    print("等待 10 秒...")
    time.sleep(10)

    if slam_proc.poll() is not None:
        out = slam_proc.stdout.read().decode()
        print(f"SLAM 启动失败:\n{out}")
        return

    print("SLAM 启动成功，实时输出如下（Ctrl+C 停止）：")
    try:
        while True:
            line = slam_proc.stdout.readline()
            if line:
                print(line.decode().rstrip())
    except KeyboardInterrupt:
        print("\n停止 SLAM...")
        slam_proc.terminate()
        slam_proc.wait()
        print("已停止")

if __name__ == "__main__":
    main()