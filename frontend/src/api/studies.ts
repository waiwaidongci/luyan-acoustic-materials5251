import {request,post} from './client';import type {Study} from '../types/domain';
export const list=()=>request<Study[]>('/studies'+'');
export const create=(data:unknown)=>post<Study>('/studies',data);
export const update=(id:number,data:unknown)=>request<Study>('/studies/'+id,{method:'PUT',body:JSON.stringify(data)});
