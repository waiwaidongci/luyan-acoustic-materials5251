import {request,post} from './client';import type {Run,RunSummary,StaleReport,BatchRecalcResult} from '../types/domain';
export const list=()=>request<RunSummary[]>('/runs'+'');
export const create=(data:unknown)=>post<Run>('/runs',data);
export const detail=(id:number)=>request<Run>('/runs/'+id);
export const stale=(studyId?:number)=>request<StaleReport[]>('/runs/stale'+(studyId?`?study_id=${studyId}`:''));
export const recalculate=(id:number)=>post<Run>(`/runs/${id}/recalculate`,{});
export const retry=(id:number)=>post<Run>(`/runs/${id}/retry`,{});
export const recalculateStale=(studyId?:number)=>post<BatchRecalcResult>('/runs/recalculate',{study_id:studyId??null});
