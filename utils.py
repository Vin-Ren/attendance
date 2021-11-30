import time


class Animation:
	def __init__(self, frames:list):
		self.frames = frames
		self.frameindex = -1
		self.framesize = len(self.frames)

	def __str__(self):
		self.frameindex+=1 if self.frameindex < self.framesize-1 else -(self.framesize-1)
		return self.frames[self.frameindex]


def Pause(message: str = "Press enter to continue.",
			 waitMultiplier: int = 0,
			 waitTime: float = 0.5,
			 waitMessages: list[str] = ['Please wait %s seconds.'],
			 waitOnly = False):
	if waitMultiplier > 0:
		maxlen = lambda list: max(list, key=len)
		msgLenFmtr = len(maxlen(waitMessages)) + len(f"{round(waitMultiplier * waitTime, 2)}")
		animas = Animation(waitMessages)
		for t in range(waitMultiplier, 0, -1):
			FmtedTime = round(t * waitTime, 2)
			frame = str(animas)
			if "%s" in frame:
				print(f"\r{frame % FmtedTime:<{msgLenFmtr}}", end="")
			else:
				print(f"\r{frame:<{msgLenFmtr}}", end="")
			time.sleep(waitTime)
	UserInput = input(message) if not waitOnly else None
	return UserInput


if __name__ == '__main__':
	import time
	frames = ['frame1', 'frame2', 'frame3', 'frame4', 'frame5']
	anima = Animation(frames)
	for i in range(15):
		print(anima)
		time.sleep(0.3)