from diablorun_igt.gui import GUI

gui = GUI()
gui.run()

"""
while True:
    if gui.closed.is_set():
        queue.put_nowait({"event": "stop"})
        break

    try:
        rgb = window_capture.get_rgb()
        print(rgb.shape)
        #changes = reader.get_changes()

        # for change in changes:
        #    print(change)
        #    queue.put_nowait(change)

        time.sleep(0.01)
    except Exception:
        print("Unable to capture window")
        time.sleep(1)
"""
