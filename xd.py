import event_emitter as events


class Ok:
    def __init__(self, a):
        self.a = a
        self.event_emitter = events.EventEmitter()

    def on(self, event: str):
        def decorator(function):
            res = self.event_emitter.on(event, function)
            return res
        return decorator


e = Ok("a")


@e.on("ready")
def ez(x: int):
    print(x)


e.event_emitter.emit("ready", 3)
