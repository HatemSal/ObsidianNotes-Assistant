import lightning as L
import subprocess

class FastAPIBackend(L.LightningWork):
    def __init__(self):
        super().__init__(
            cloud_compute=L.CloudCompute("cpu-small"),
            port=8000
        )

    def run(self):
       
        subprocess.run([
            "uvicorn",
            "src.backend.main:app",
            "--host", "0.0.0.0",
            "--port", str(self.port)
        ])


class RootFlow(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.backend = FastAPIBackend()

    def run(self):
        self.backend.run()

    def configure_layout(self):
        
        return [{"name": "FastAPI", "content": self.backend.url}]


app = L.LightningApp(RootFlow())
