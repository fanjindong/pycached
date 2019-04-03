import tornado.web
import tornado.ioloop
from datetime import datetime
from pycached import cached
from pycached.serializers import JsonSerializer


class MainHandler(tornado.web.RequestHandler):

    # Due some incompatibilities between tornado and asyncio, caches can't use the "timeout" feature
    # in order to make it work, you will have to specify it always to 0
    @cached(key="my_custom_key", serializer=JsonSerializer(), timeout=0)
    def time(self):
        return {"time": datetime.now().isoformat()}

    def get(self):
        self.write(self.time())


if __name__ == "__main__":
    tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
    app = tornado.web.Application([(r"/", MainHandler)])
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
