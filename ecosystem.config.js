module.exports = {
    "apps": [
        {
        "name": "nova-camera",
        "script": "python3 scripts/camera.py",
        "instances": "1",
        "output": "./logs/nova-camera-out.log",
        "error": "./logs/nova-camera-error.log"
        },
        {
            "name": "nova-stream",
            "script": "python3 scripts/stream.py",
            "instances": "1",
            "output": "./logs/nova-stream-out.log",
            "error": "./logs/nova-stream-error.log"
        },
        {
            "name": "nova-track",
            "script": "python3 scripts/track.py",
            "instances": "1",
            "output": "./logs/nova-track-out.log",
            "error": "./logs/nova-track-error.log"
        }
    ]
}
