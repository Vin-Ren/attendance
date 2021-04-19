import time


class animation:
    def __init__(self, frames:list):
        self.frames = frames
        self.frameindex = -1
        self.framesize = len(self.frames)

    def __str__(self):
        self.frameindex+=1 if self.frameindex < self.framesize-1 else -(self.framesize-1)
        return self.frames[self.frameindex]


def pause(pause_msg: str = "Press enter to continue.",
		  wait_cycle: int = 0,
		  cycle_len: float = 0.5,
		  wait_msg: list = ["Please wait %s seconds."], NoInput=False):
    if wait_cycle != 0:
        max_wmsg_len=len(max(wait_msg, key=len)) + len(f"{round(wait_cycle*cycle_len, 2)}")
        wait_anima = animation(wait_msg)
        for currtime in range(wait_cycle, 0, -1):
            print(f"\r{str(wait_anima) % (round(currtime*cycle_len, 2)):<{max_wmsg_len}}", end="")
            time.sleep(cycle_len)
    rv = input(pause_msg) if not NoInput else None
    return rv


if __name__ == '__main__':
    import time
    frames = ['frame1', 'frame2', 'frame3', 'frame4', 'frame5']
    anima = animation(frames)
    for i in range(15):
        print(anima)
        time.sleep(0.3)