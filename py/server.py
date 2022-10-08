import time
from concurrent import futures
import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import hdbscan
from collections import Counter
from datetime import datetime
from  sklearn.feature_extraction.text import TfidfVectorizer
from  sklearn.decomposition import LatentDirichletAllocation as LDA
import numpy as np
import re

from ml_pb2 import *
from ml_pb2_grpc import *


def get_datetime_format(date: str):
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except:
        return date
    
def get_main_sentence_from_cluster(news):
    #каждое предложение с каждым и находим среднее по кос дист
    #TODO 
    #пока что макс длину берем
    
    res = []
    for new in news:
        header = new['main'].values[0]+'.'
        sentences = text_clean_func(new['text'].values[0]).split('.')
        #embeddings_cluster = vectorize(sentences)
        
        #cos_sims = cosine_similarity(embeddings_cluster,embeddings_cluster)
        #metric_of_sim = [np.sum(i) for i in cos_sims]
        
        #res.append(sentences[max(enumerate(metric_of_sim),key=lambda x: x[1])[0]])
        res.append(header+'\n'+sorted(sentences, key=len)[-1])
    return res#,metric_of_sim,sentences

def analize_time_intervals(d, cluster_id, date_of_trend=datetime(2022, 10, 1)):
    #d - result фрейм после кластеризации
    # cluster id  номер кластера
    #date_of_trend в какой день ищем тренд - если была новость про  тренд в этот день или позднее, то ок
    
    #считаем среднее время между новостями, если есть периодичность(в среднем каждую неделю и меньше есть новость)
    # и кластер большой то считаем что есть тренд
    
    cl_dt = list(d.loc[d['cluster']==cluster_id].date)
    cl_dt = sorted([ i for i in cl_dt if type(i)!=float])

    mean_time_delta = np.mean(([(cl_dt[i]-cl_dt[i-1]).days if i>0 else 0 for i,j in enumerate(cl_dt)]))
    
    if mean_time_delta<7:## TODO здесб будет проверка по времени - за какой день тренд считать
        return True,mean_time_delta
    else:
        return False,mean_time_delta
    
def get_trend_words(d, cluster_id):
    #d - result фрейм после кластеризации
    # cluster id  номер кластера
    
    #vectorize texts  заголовки !?
    count_vect = TfidfVectorizer(ngram_range=(2,4))
    dataset = count_vect.fit_transform(d.loc[d['cluster']==cluster_id].text)
    lda = LDA(n_components =10,doc_topic_prior=3,
                 max_iter=20,
                 learning_method='batch',
                 verbose=1)
    #lda.fit(dataset)
    #res = lda.transform(dataset)

    # Fit and Transform SVD model on data
    lda_matrix = lda.fit_transform(dataset)

    # Get Components 
    lda_components=lda.components_
    
    terms = count_vect.get_feature_names()

    for index, component in enumerate(lda_components):
        zipped = zip(terms, component)
        top_terms_key=sorted(zipped, key = lambda t: t[1], reverse=True)[:7]
        top_terms_list=list(dict(top_terms_key).keys())
    return top_terms_list

def text_clean_func(text):
    """
    функция очистки текста
    
    """
    
    text = re.sub(r"\xa0", "", text)
    text = re.sub(r"\r", "", text)
    text = re.sub(r"\n", "", text)
    text = re.sub(r"\t", " ", text)

    return text

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
        data = pd.read_csv(path)#.iloc[:3000]
        data['date'] = data['date'].apply(get_datetime_format)

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
        data['cluster'] = cluster.labels_
        
        clusters = list(sorted(Counter(cluster.labels_).items(), key=lambda item: item[1],reverse=True))
        num_cl = 0
        news = []
        for i in clusters:
            if i[0]!=-1:
                num_cl+=1
                cl_dt = (data.loc[data['cluster']==i[0]].date)
                max_dt = sorted([ i for i in cl_dt if type(i)!=float])[-1]
                news.append((data.loc[(data['cluster']==i[0])&(data['date']==max_dt),['main','text']]))
            if num_cl == 2:
                break
        news = get_main_sentence_from_cluster(news)


        response = DigestResponse()
        response.news.extend(news)
        return response

    def Trend(self, request, context):
        
        data = pd.read_csv(request.path)#.iloc[:3000]
        data['date'] = data['date'].apply(get_datetime_format)

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
        data['cluster'] = cluster.labels_
        
        clusters = list(sorted(Counter(cluster.labels_).items(), key=lambda item: item[1],reverse=True))
        num_cl = 0
        trends = []
        for i in clusters:
            if i[0]!=-1:
                a,b = (analize_time_intervals(data, i[0]))
                if a:
                    num_cl+=1
                    lda = get_trend_words(data, i[0])
                    trend = 'Trend: '+sorted(lda, key=len)[-1]
                    trends.append(trend)
                if num_cl == 1:
                    break
        
        response = DigestResponse()
        response.news.extend(trends)
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