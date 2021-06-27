import

class Launcher:
    running: bool = False

    def __init__(self):
        self.running = True
        main()

    def stop(self): self.running = False

    def start(self): self.running = True

    def toggle_running(self): self.running = !self.running

    def main(self):
        while self.running:
            pass
