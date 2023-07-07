import numpy as np
import pyaudio
import wave
import logmmse

def start_audio(time=3, Save_wave = "test.wav"):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 16000
    RECORD_SECONDS = time  # 需要录制的时间
    WAVE_OUTPUT_FILENAME = Save_wave  # 保存的文件名

    p = pyaudio.PyAudio()  # 初始化
    print("ON")

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)  # 创建录音文件
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)  # 开始录音
    print("OFF")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')  # 保存
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    f = wave.open(WAVE_OUTPUT_FILENAME, "r")
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    print("nchannels:", nchannels, "sampwidth:", sampwidth, "framerate:", framerate, "nframes:", nframes)
    data = f.readframes(nframes)
    f.close()
    data = np.fromstring(data, dtype=np.short)

    # 降噪
    data = logmmse.logmmse(data=data, sampling_rate=framerate)


    # 保存音频
    file_save = 'process.wav'
    nframes = len(data)
    f = wave.open(file_save, 'w')
    f.setparams((1, 2, framerate, nframes, 'NONE', 'NONE'))  # 声道，字节数，采样频率，*，*
    # print(data)
    f.writeframes(data)  # outData
    f.close()
    return WAVE_OUTPUT_FILENAME
# f = wave.open(path, "r")
#     params = f.getparams()
#     nchannels, sampwidth, framerate, nframes = params[:4]
#     print("nchannels:", nchannels, "sampwidth:", sampwidth, "framerate:", framerate, "nframes:", nframes)
#     data = f.readframes(nframes)
#     f.close()
#     data = np.fromstring(data, dtype=np.short)
#
#     # 降噪
#     data = logmmse.logmmse(data=data, sampling_rate=framerate)
#
#
#     # 保存音频
#     file_save = 'process.wav'
#     nframes = len(data)
#     f = wave.open(file_save, 'w')
#     f.setparams((1, 2, framerate, nframes, 'NONE', 'NONE'))  # 声道，字节数，采样频率，*，*
#     # print(data)
#     f.writeframes(data)  # outData
#     f.close()