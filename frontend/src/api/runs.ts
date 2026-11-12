import {request,post} from './client';import type {Run,RunSummary} from '../types/domain';
export const list=()=>request<RunSummary[]>('/runs'+'');
export const create=(data:unknown)=>post<Run>('/runs',data);
export const detail=(id:number)=>request<Run>('/runs/'+id);
