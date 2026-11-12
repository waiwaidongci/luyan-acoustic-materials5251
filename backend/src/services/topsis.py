"""Vector-normalized, weighted Euclidean TOPSIS. Ties are exact score ties."""
import numpy as np
from src.services.normalization import normalize_matrix,normalize_weights,stable_norm

def average_ranks(scores):
    order=np.argsort(-np.asarray(scores),kind='stable');r=np.zeros(len(order));s=np.zeros(len(order));start=0
    while start<len(order):
        end=start+1
        while end<len(order) and scores[order[end]]==scores[order[start]]:end+=1
        r[order[start:end]]=(start+1+end)/2
        if start==0:s[order[start:end]]=1/(end-start)
        start=end
    return r,s

def score_normalized(normalized,directions,weights):
    n,m=normalized.shape
    if len(directions)!=m or any(d not in ('benefit','cost') for d in directions):raise ValueError('指标方向只能为benefit/cost，且须逐列对应')
    w=normalize_weights(weights,m,False);v=normalized*w
    benefit=np.array([d=='benefit' for d in directions]);best=np.where(benefit,np.max(v,axis=0),np.min(v,axis=0));worst=np.where(benefit,np.min(v,axis=0),np.max(v,axis=0))
    dp=stable_norm(v-best,1);dm=stable_norm(v-worst,1)
    # No absolute epsilon: even tiny representable distances can separate.
    scale=np.maximum(dp,dm);a=np.divide(dm,scale,out=np.zeros_like(dm),where=scale!=0);b=np.divide(dp,scale,out=np.zeros_like(dp),where=scale!=0)
    score=np.divide(a,a+b,out=np.full(n,.5),where=scale!=0);ranks,first=average_ranks(score)
    return {'scores':score,'ranks':ranks,'first_share':first,'weighted':v,'ideal_best':best,'ideal_worst':worst,'distance_best':dp,'distance_worst':dm,'all_indistinguishable':bool(np.all(scale==0))}

def calculate_topsis(matrix,directions,weights):
    normalized,columns=normalize_matrix(matrix);result=score_normalized(normalized,directions,weights)
    return {**result,'normalized':normalized,'columns':columns}
