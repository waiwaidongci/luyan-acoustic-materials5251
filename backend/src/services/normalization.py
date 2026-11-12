"""Scale before squaring: preserve representable small contrasts and tiny units."""
import numpy as np

def stable_norm(values,axis):
    a=np.asarray(values,dtype=float);scale=np.max(np.abs(a),axis=axis,keepdims=True)
    scaled=np.divide(a,scale,out=np.zeros_like(a),where=scale!=0)
    return np.squeeze(scale,axis=axis)*np.sqrt(np.sum(scaled*scaled,axis=axis))

def normalize_matrix(matrix):
    x=np.asarray(matrix,dtype=float)
    if x.ndim!=2 or not 2<=x.shape[0]<=120 or not 1<=x.shape[1]<=5:raise ValueError('矩阵须为2–120候选、1–5指标')
    if not np.isfinite(x).all() or (x<0).any():raise ValueError('物理指标须为有限非负数，不能含缺测')
    scale=np.max(np.abs(x),axis=0);scaled=np.divide(x,scale,out=np.zeros_like(x),where=scale!=0)
    lengths=np.sqrt(np.sum(scaled*scaled,axis=0));normalized=np.divide(scaled,lengths,out=np.zeros_like(scaled),where=lengths!=0)
    norms=scale*lengths
    if not np.isfinite(norms).all():raise ValueError('列范数超出双精度可表示范围，请先换单位')
    info=[{'index':j,'norm':float(norms[j]),'zero_norm':bool(scale[j]==0),'constant':bool(np.all(x[:,j]==x[0,j])),'policy':'zero column kept at zero, weight retained' if scale[j]==0 else 'constant column contributes no separation, weight retained' if np.all(x[:,j]==x[0,j]) else 'L2 normalized'} for j in range(x.shape[1])]
    return normalized,info

def normalize_weights(weights,size,strict_positive=False):
    w=np.asarray(weights,dtype=float)
    if w.ndim!=1 or len(w)!=size or not np.isfinite(w).all():raise ValueError('权重维数错误或非有限')
    if (w<=0).any() if strict_positive else (w<0).any():raise ValueError('中心权重必须全正' if strict_positive else '情景权重必须非负')
    peak=float(np.max(w))
    if peak==0:raise ValueError('权重和须为正')
    w=w/peak;return w/w.sum()
