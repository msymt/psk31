import wave
import math
import numpy as np

def main():
	fname='./psk31.wav'  # should be specify the filename.
	smp= 8000           # Sampling Rate
	FQ= smp/1000.0      # Signal Frequency
	wind= 40            # window
	baud_rate = 31.25   # psk31 baud rate
	waveFile = wave.open(fname, 'r')

	q=[];i=[];result = []
	for j in range(waveFile.getnframes()):
		buf = waveFile.readframes(1)
		# 符号なし→符号あり
		q.append((buf[0]-128)*np.sin(np.pi*2.0/FQ*j))	#実部
		i.append((buf[0]-128)*np.cos(np.pi*2.0/FQ*j))	#虚部
		print(int(sum(q)>0),int(sum(i)>0),sep=",")
		result
		if j>wind:
			q.pop(0);i.pop(0)
	waveFile.close()


if __name__ == "__main__":
	main()
