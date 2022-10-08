import time
from concurrent import futures

from ml_pb2 import *
from ml_pb2_grpc import *


class MlService(MlServiceServicer):

    def __init__(self):
        print("init")

    def Digest(self, request, context):
        role = request.role
        path = request.path

        news = ["test", "test", "test"]

        response = DigestResponse()
        response.news.extend(news)
        return response

    def Trend(self, request, context):

        response = DigestResponse()
        response.news.extend(["test_trend", "test_trend", "test_trend"])
        return response

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MlServiceServicer_to_server(
        MlService(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    print("Listening on port {}..".format(port))
    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        server.stop(0)


if __name__== "__main__":
    serve(6000)