import time
from concurrent import futures
import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import hdbscan
from collections import Counter

from ml_pb2 import *
from ml_pb2_grpc import *


class MlService(MlServiceServicer):

    def __init__(self):

        self.tokenizer = AutoTokenizer.from_pretrained("cointegrated/LaBSE-en-ru")
        self.model = AutoModel.from_pretrained("cointegrated/LaBSE-en-ru")
        print("init model")

    # def vectorize(self, texts):
    #
    #     encoded_input = self.tokenizer(texts, padding=True, truncation=True, max_length=64, return_tensors='pt')
    #     with torch.no_grad():
    #         model_output = self.model(**encoded_input)
    #     embeddings = model_output.pooler_output
    #     embeddings = torch.nn.functional.normalize(embeddings)
    #     return embeddings
    #
    # def clusterize(self, embeddings):
    #
    #     cluster = hdbscan.HDBSCAN(min_cluster_size=3,
    #                       metric='euclidean',
    #                       cluster_selection_method='eom').fit(embeddings)
    #     return cluster
    #
    # def load_data_by_role(self, role, path):
    #     #return pandas DataFrame
    #     data = pd.read_csv(path)
    #     return data

    def Digest(self, request, context):
        role = request.role
        path = request.path

        # data = load_data_by_role(role, path)
        # на 6000 падает по памяти, а на 1000 работает. Нужно память оптимизировать или данные урезать
        data = pd.read_csv(path)#.iloc[:3000]


        #embedings = vectorize(list(data.main))
        encoded_input = self.tokenizer(list(data.main), padding=True, truncation=True, max_length=64, return_tensors='pt')
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        embeddings = model_output.pooler_output
        embeddings = torch.nn.functional.normalize(embeddings)

        #cluster = clusterize(embeddings)
        cluster = hdbscan.HDBSCAN(min_cluster_size=3,
                                  metric='euclidean',
                                  cluster_selection_method='eom').fit(embeddings)
        cluster_counts = list(sorted(Counter(cluster.labels_).items(), key=lambda item: item[1]))
        data['cluster'] = cluster.labels_

        news = list(data.loc[data['cluster']==cluster_counts[0][0]].main)
        #news = ["test", "test", "test"]

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
            time.sleep(1000000)
    except KeyboardInterrupt:
        server.stop(0)


if __name__== "__main__":
    serve(6000)