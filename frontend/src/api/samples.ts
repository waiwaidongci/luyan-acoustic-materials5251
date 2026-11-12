import {request,post} from './client';import type {Sample} from '../types/domain';
export const list=()=>request<Sample[]>('/samples'+'');
export const create=(data:unknown)=>post<Sample>('/samples',data);
export const update=(id:number,data:unknown)=>request<Sample>('/samples/'+id,{method:'PUT',body:JSON.stringify(data)});
