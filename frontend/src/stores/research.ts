import {defineStore} from 'pinia';
import {ref,computed} from 'vue';
import * as runsApi from '../api/runs';
import * as notesApi from '../api/notes';
import type {RunSummary,Run,Note,StaleReport,BatchRecalcResult} from '../types/domain';

export const useResearch=defineStore('research',()=>{
  const runs=ref<RunSummary[]>([]);
  const notes=ref<Note[]>([]);
  const staleReports=ref<StaleReport[]>([]);
  const selected=ref(Number(localStorage.getItem('material-run')||0));
  const current=ref<Run|null>(null);

  const staleById=computed(()=>new Map(staleReports.value.map(r=>[r.run_id,r])));
  const staleRuns=computed(()=>staleReports.value.filter(r=>r.stale));
  // Map an original run id to its newest recalculation summary (any status), if one exists.
  const recalcByRoot=computed(()=>{
    const m=new Map<number,RunSummary>();
    runs.value.filter(r=>r.recalc_of_id).forEach(r=>{
      const prev=r.recalc_of_id?m.get(r.recalc_of_id):undefined;
      if(!prev||(r.recalc_seq||0)>=(prev.recalc_seq||0))m.set(r.recalc_of_id as number,r);
    });
    return m;
  });
  const activeRecalcCount=computed(()=>runs.value.filter(r=>r.recalc_of_id&&['queued','running'].includes(r.status)).length);

  async function loadRuns(){
    runs.value=await runsApi.list();
    if(!runs.value.some(r=>r.id===selected.value))selected.value=runs.value.find(r=>r.status==='completed')?.id||runs.value[0]?.id||0;
  }
  async function loadStale(studyId?:number){staleReports.value=await runsApi.stale(studyId);}
  async function select(id:number){
    selected.value=id;localStorage.setItem('material-run',String(id));current.value=null;
    if(id)current.value=await runsApi.detail(id);
  }
  async function queue(data:unknown){
    const run=await runsApi.create(data);await loadRuns();
    selected.value=run.id;localStorage.setItem('material-run',String(run.id));
    return run;
  }
  async function recalculate(id:number){const run=await runsApi.recalculate(id);await loadRuns();await loadStale();return run;}
  async function retry(id:number){const run=await runsApi.retry(id);await loadRuns();await loadStale();return run;}
  async function recalculateStale(studyId?:number):Promise<BatchRecalcResult>{
    const result=await runsApi.recalculateStale(studyId);await loadRuns();await loadStale(studyId);return result;
  }
  function chainOf(runId:number){
    const root=runs.value.find(r=>r.id===runId);
    const rootId=root?.recalc_of_id||runId;
    const family=runs.value.filter(r=>r.id===rootId||r.recalc_of_id===rootId).sort((a,b)=>a.id-b.id);
    return family;
  }
  async function loadNotes(){notes.value=await notesApi.list();}
  async function addNote(data:unknown){const n=await notesApi.create(data);await loadNotes();return n;}
  async function review(id:number,status:string,note:string){await notesApi.review(id,status,note);await loadNotes();}
  return {runs,notes,staleReports,selected,current,staleById,staleRuns,recalcByRoot,activeRecalcCount,
    loadRuns,loadStale,select,queue,recalculate,retry,recalculateStale,chainOf,loadNotes,addNote,review};
});
