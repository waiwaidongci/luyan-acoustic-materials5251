import {request,post} from './client';import type {Criterion} from '../types/domain';
export const list=(study_id:number)=>request<Criterion[]>('/criteria'+`?study_id=${study_id}`);
export const create=(data:unknown)=>post<Criterion>('/criteria',data);
export const update=(id:number,data:unknown)=>request<Criterion>('/criteria/'+id,{method:'PUT',body:JSON.stringify(data)});
