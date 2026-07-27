import subprocess
import asyncio

_CONTAINER = "ugv_jetson_ros_humble"
_INIT = (
    "source /root/.bashrc && "
    "source /home/ws/ugv_ws/install/setup.bash"
)


class DockerROS2:
    """统一管理容器内 ROS2 命令执行"""

    @staticmethod
    def run(cmd: str, timeout: int = 10) -> subprocess.CompletedProcess:
        """同步执行，等待结果"""
        return subprocess.run(
            ["docker", "exec", _CONTAINER, "bash", "-i", "-c", f"{_INIT} && {cmd}"],
            capture_output=True, text=True, timeout=timeout
        )

    @staticmethod
    def run_bg(cmd: str) -> subprocess.Popen:
        """后台执行，不阻塞，返回进程句柄"""
        return subprocess.Popen(
            ["docker", "exec", _CONTAINER, "bash", "-i", "-c", f"{_INIT} && {cmd}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

    @staticmethod
    async def run_async(cmd: str, timeout: int = 10) -> str:
        """异步执行，返回输出"""
        proc = await asyncio.create_subprocess_exec(
            "docker", "exec", _CONTAINER, "bash", "-i", "-c", f"{_INIT} && {cmd}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return stdout.decode()

    @staticmethod
    def node_running(node_name: str) -> bool:
        """检查 ROS2 节点是否在运行"""
        result = DockerROS2.run("ros2 node list")
        return node_name in result.stdout

    @staticmethod
    def shell(cmd: str, timeout: int = 30) -> tuple[int, str]:
        """执行并返回 (returncode, output)，用于需要判断成功失败的场景"""
        result = DockerROS2.run(cmd, timeout=timeout)
        return result.returncode, result.stdout + result.stderr