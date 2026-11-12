"""Dirichlet weights are hypothetical preference scenarios, never inference."""
from collections import Counter
import hashlib,json
import numpy as np
from src.services.normalization import normalize_matrix,normalize_weights
from src.services.topsis import score_normalized

def analyze_decision(snapshot,center_weights,concentration,repeats,seed,heartbeat=None):
    samples=sorted(snapshot['samples'],key=lambda x:x['code']);criteria=sorted(snapshot['criteria'],key=lambda x:x['code'])
    if len({x['id'] for x in samples})!=len(samples) or len({x['code'] for x in samples})!=len(samples):raise ValueError('候选标识重复')
    codes=[c['code'] for c in criteria]
    if len(set(codes))!=len(codes) or not codes:raise ValueError('指标为空或重复')
    if set(center_weights)!=set(codes):raise ValueError('中心权重必须逐一覆盖本研究指标，不可缺失或多余')
    if not np.isfinite(concentration) or concentration<=0:raise ValueError('集中度必须有限且为正')
    if isinstance(repeats,bool) or not isinstance(repeats,int) or not 1000<=repeats<=2000:raise ValueError('权重情景须为1000–2000次')
    try:matrix=np.array([[s[c] for c in codes] for s in samples],dtype=float)
    except (KeyError,TypeError,ValueError):raise ValueError('候选缺少有效指标值')
    normalized,columns=normalize_matrix(matrix);center=normalize_weights([center_weights[c] for c in codes],len(codes),True)
    alpha=center*concentration
    if (alpha<=0).any():raise ValueError('权重与集中度乘积小到无法用双精度表示')
    directions=[c['direction'] for c in criteria];baseline=score_normalized(normalized,directions,center)
    rng=np.random.default_rng(seed);scenarios=rng.dirichlet(alpha,size=repeats);draws=[];rank_rows=[];share_rows=[]
    if not np.isfinite(scenarios).all():raise ValueError('Dirichlet抽样非有限，请使用可表示的中心权重')
    for i,w in enumerate(scenarios):
        # Finite-precision Dirichlet can yield zero components: legal nonnegative weights.
        result=score_normalized(normalized,directions,w);rank_rows.append(result['ranks']);share_rows.append(result['first_share'])
        draws.append({'repeat':i+1,'weights':w.tolist(),'scores':result['scores'].tolist(),'ranks':result['ranks'].tolist(),'first_share':result['first_share'].tolist(),'all_indistinguishable':result['all_indistinguishable']})
        if heartbeat and i%50==0:heartbeat()
    ranks=np.asarray(rank_rows);shares=np.asarray(share_rows);rows=[]
    for i,s in enumerate(samples):
        q=np.quantile(ranks[:,i],[.025,.5,.975]);freq=Counter(str(float(v)) for v in ranks[:,i])
        rows.append({**s,'score':float(baseline['scores'][i]),'rank':float(baseline['ranks'][i]),'distance_best':float(baseline['distance_best'][i]),'distance_worst':float(baseline['distance_worst'][i]),'rank_min':float(ranks[:,i].min()),'rank_max':float(ranks[:,i].max()),'rank_low':float(q[0]),'rank_median':float(q[1]),'rank_high':float(q[2]),'first_share':float(shares[:,i].mean()),'rank_frequency':dict(sorted(freq.items(),key=lambda x:float(x[0]))),'normalized':normalized[i].tolist(),'weighted':baseline['weighted'][i].tolist()})
    canonical={'version':'vector-topsis-dirichlet-v1','snapshot':snapshot,'center_weights':center_weights,'concentration':concentration,'repeats':repeats,'seed':seed}
    fingerprint=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    return {'samples':rows,'criteria':criteria,'columns':columns,'center_weights':center.tolist(),'alpha':alpha.tolist(),'concentration':concentration,'repeats':repeats,'seed':seed,'ideal_best':baseline['ideal_best'].tolist(),'ideal_worst':baseline['ideal_worst'].tolist(),'all_indistinguishable':baseline['all_indistinguishable'],'draws':draws,'zero_weight_scenarios':int(np.any(scenarios==0,axis=1).sum()),'fingerprint':fingerprint,'snapshot':snapshot,'rank_rule':'exact equal computed closeness scores receive average ranks; tied first split one share','scope':'hypothetical preference-weight sensitivity, not statistical confidence, posterior, or procurement recommendation'}
