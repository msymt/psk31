import wave
import math
import numpy as np
import table
"""
wavから，2bitの位相変調されたデータを取り出す
	q, i: 受信側の位相差がある．
2bitから畳み込み符号で1bitに変換
（ビタビ復号によって復元）
1bitの列からvaricodeで対応する文字へ変換
"""

def main():
	fname='./psk31.wav'  # should be specify the filename.
	smp= 8000           # Sampling Rate
	FQ= smp/1000.0      # Signal Frequency
	wind= 40            # window
	baud_rate = 31.25   # psk31 baud rate
	bit_duration = int(smp/baud_rate) # sampling number / 1bit, 256
	bit_width = 0.5			# 50%
	waveFile = wave.open(fname, 'r')

	q=[];i=[];whole_smp = []
	for j in range(waveFile.getnframes()):
		buf = waveFile.readframes(1)
		singed_value = buf[0]-128	# 符号なし→符号あり
		element = np.pi*2.0/FQ*j	# sin/cosの中
		q.append(singed_value*np.sin(element))	#虚部
		i.append(singed_value*np.cos(element))	#実部
		time = j / smp
		# print(int(sum(q)>0),int(sum(i)>0),sep=",")
		whole_smp.append([int(sum(q)>0),int(sum(i)>0), time]) #強め合う→>0, 弱め合う-> <= 0
		# whole_smp.append([sum(q),sum(i), time])
		if j>wind:
			q.pop(0);i.pop(0)
	waveFile.close()

	# 256個ずつに分けたbit列を格納
	divide_one_bit = divide_one_bit_array(whole_smp, bit_duration)
	divide_one_bit = divide_one_bit[:-1] #末尾削除
	extracted_one_bit = []
	for item in divide_one_bit:
		extracted_one_bit.append(item[int(len(item) * bit_width)]) # 50%あたり
	# decoded_one_bit = decode_bit(extracted_one_bit)
	decoded_one_bit = decode_fec(extracted_one_bit)
	bit_chunks = decoded_value_to_bit_chunks(decoded_one_bit)
	chars = parse_varicode(bit_chunks)
	for char in chars:
		print(char, end='', flush=True)
	print('')

# サンプルを1bit毎に分けた結果を返す
def divide_one_bit_array(smp_buf, bit_duration):
	result = []
	start = 0 # break用
	for _ in smp_buf:
		bit_buf = smp_buf[start:start+bit_duration:1] # 256個ずつ
		result.append(bit_buf)
		start += bit_duration
		if start >= len(smp_buf): # 境界
			break
	return result

# def decode_bit(bit_stream):
# 	state = "00000"
# 	last_input = None
	# result = []
	# for item in bit_stream:
	# 	q_value = item[0]; i_value = item[1]
	# 	gray_code = decode_gray_code(q_value, i_value)
	# 	if last_input is None:
	# 		last_input = gray_code
	# 		result.append(last_input)
	# 		continue

	# 	diff = (gray_code - last_input) % 4 # 00 - 11

def decode_fec(bit_stream):
	last_input = None
	state = "00000" # init
	result = []
	for item in bit_stream:
		q = item[0];i = item[1]
		gray_code = decode_gray_code(q, i)
		if last_input is None:
			last_input = gray_code
			result.append(last_input)
			continue

		diff = (gray_code - last_input) % 4 # 00 ~ 11
		last_input = gray_code
		current_input = None
		if diff == convolutional_encode(state, 0):
			current_input = 0
		elif diff == convolutional_encode(state, 1):
			current_input = 1
		else:
			# current_input is None
			state = "00000"
			continue

		state = state[-4:] + str(current_input)
		result.append(current_input)
	return result

# グレイ符号による誤り訂正
def decode_gray_code(q, i):
	return table.GRAY_TABLE[q][i]

# def convolutional_encode_next(old_state, current):
# 	bit0 = convolutional_encode_g0(old_state, current)
# 	bit1 = convolutional_encode_g1(old_state, current)
# 	next_state = old_state[-4:]
# 	return [next_state, (bit0>>1)|bit1 ]


# def convolutional_encode_g0(old_state, current):
# 	state = old_state[-4:] + str(current)
# 	bit0 = (int(state[0]) + int (state[1]) + int(state[2]) + int(state[4])) % 2
# 	return bit0

# def convolutional_encode_g1(old_state, current):
# 	state = old_state[-4:] + str(current)
# 	bit1 = (int(state[0]) + int(state[3]) + int(state[4])) % 2
# 	return bit1

# def convolutional_encode(old_state, current):
#     state = old_state[-4:] + str(current)
#     bit1 = (int(state[4]) + int(state[2]) + int(state[1]) + int(state[0])) % 2
#     bit2 = (int(state[4]) + int(state[3]) + int(state[0])) % 2
#     return int(bit2) * 2 + int(bit1)

def convolutional_encode(old_state, current):
	state = old_state[-4:] + str(current)
	bit1 = int(state[0]) ^ int(state[2]) ^ int(state[3]) ^ int(state[4])
	bit2 = not int(state[0]) ^ int(state[1]) ^ int(state[4])
	return int(bit2) * 2 + int(bit1)

def decoded_value_to_bit_chunks(bit_values):
	chunk = ""
	result = []
	for current_value in bit_values:
		if (
			chunk != "" and chunk[-1] == "0" and current_value == 0 or
			chunk == "" and current_value == 0
		):
			if chunk != "":
				result.append(chunk.rstrip("0"))
				chunk = ""
		else:
			chunk += str(current_value)
	# if chunk != '':
	# 	 chunk.rstrip("0")
	# 	 result.append(chunk)
	return result


def parse_varicode(bit_chunks):
	result = []
	# print(bit_chunks)
	for chunk in bit_chunks:
		# 割り当てにない場合
		if chunk not in table.VARICODE_TABLE.keys():
			pass
		else:
			char = table.VARICODE_TABLE[chunk]
			result.append(char)
	return result

def divide_one_bit_smp(smp_buf):
	pass
	# for item in smp_buf:

if __name__ == "__main__":
	main()
