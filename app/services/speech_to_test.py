import whisper
import pyautogui
import sounddevice as sd
import numpy as np
import queue
import time
import pygetwindow as gw
import warnings
import sys
import threading

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
model = whisper.load_model("base.en", device="cpu")

samplerate = 16000
blocksize = 4000
audio_queue = queue.Queue()
audio_buffer = np.zeros((0,))
stop_event = threading.Event()   # <-- thread-safe flag


def audio_callback(indata, frames, time_, status):
    audio_queue.put(indata.copy())


def write_code(text):
    try:
        vscode_window = None
        for w in gw.getWindowsWithTitle("Visual Studio Code"):
            if "Code" in w.title:
                vscode_window = w
                break

        if vscode_window:
            vscode_window.activate()
            time.sleep(0.3)
            pyautogui.typewrite(text, interval=0.02)
            pyautogui.press("enter")
            print("✅ Code typed in VS Code.")
        else:
            print("⚠️ VS Code window not found.")
    except Exception as e:
        print(f"❌ Error typing in VS Code: {e}")


def interpret_and_execute(command: str):
    command = command.lower().strip()
    if "stop" in command:
        print("🛑 Voice stop command received. Exiting...")
        stop_event.set()
        return

    elif "for loop" in command or "create a loop" in command:
        write_code("for i in range(5):\n    print(i)")
    elif "while loop" in command:
        write_code("i = 0\nwhile i < 5:\n    print(i)\n    i += 1")
    elif "print" in command:
        write_code('print("Hello, world!")')
    elif "function" in command:
        write_code("def my_function():\n    print('Function created')")
    elif "if statement" in command:
        write_code("if True:\n    print('Condition met')")
    elif "clear" in command:
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
    else:
        print("⚠️ Command not recognized.")


def main():
    print("🎙️ Listening for voice commands... (say 'stop' or press Ctrl+C to exit)")
    try:
        with sd.InputStream(samplerate=samplerate, channels=1, callback=audio_callback):
            while not stop_event.is_set():
                while not audio_queue.empty():
                    audio_chunk = audio_queue.get()
                    global audio_buffer
                    audio_buffer = np.concatenate((audio_buffer, audio_chunk.flatten()))

                if len(audio_buffer) >= samplerate * 4:
                    audio_data = np.copy(audio_buffer).astype(np.float32)
                    audio_buffer = np.zeros((0,))
                    print("⏳ Processing command...")
                    result = model.transcribe(audio_data)
                    command = result["text"].strip()
                    print(f"🗣️ Command recognized: {command}")
                    interpret_and_execute(command)

                    # ✅ Break immediately if stop command was spoken
                    if stop_event.is_set():
                        break

                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Ctrl+C detected. Stopping listener...")
        stop_event.set()
    finally:
        print("✅ Listener stopped cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
