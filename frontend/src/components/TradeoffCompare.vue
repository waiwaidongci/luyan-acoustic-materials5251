<script setup lang="ts">
import {computed,ref,onMounted} from 'vue';
import {useResearch} from '../stores/research';
import {useTask} from '../hooks/useTask';
import * as runsApi from '../api/runs';
import {num,rank,percent} from '../utils/format';
import type {Run,RankRow} from '../types/domain';

const props=defineProps<{run:Run}>();
const research=useResearch();const {perform}=useTask();
const otherId=ref(0);

const rootId=computed(()=>props.run.recalc_of_id||props.run.id);
const family=computed(()=>research.chainOf(rootId.value).filter(r=>r.status==='completed'));
const otherSummary=computed(()=>family.value.find(r=>r.id===otherId.value)||null);
const other=ref<Run|null>(null);

onMounted(()=>{
  // Default comparison partner: the other end of the chain (original for recalcs, newest for originals).
  const others=family.value.filter(r=>r.id!==props.run.id);
  if(others.length){
    const pick=props.run.recalc_of_id?others.find(r=>r.id===rootId.value)!:others[others.length-1];
    otherId.value=pick.id;
  }
});

async function choose(id:number){
  otherId.value=id;other.value=null;
  if(id)await perform(async()=>{other.value=await runsApi.detail(id);});
}
defineExpose({choose});

const currentRows=computed(()=>props.run.result?.samples||[]);
const otherRows=computed(()=>other.value?.result?.samples||[]);
const otherIndex=computed(()=>new Map(otherRows.value.map((s:RankRow)=>[s.code,s])));
const curIndex=computed(()=>new Map(currentRows.value.map((s:RankRow)=>[s.code,s])));
const rows=computed(()=>currentRows.value.slice().sort((a,b)=>a.rank-b.rank).map(s=>{
  const o=otherIndex.value.get(s.code);
  return {cur:s,old:o||null,rankDelta:o?o.rank-s.rank:null,scoreDelta:o?s.score-o.score:null};
}));
const curTop=computed(()=>currentRows.value.find(s=>s.rank===1));
const oldTop=computed(()=>otherRows.value.find((s:RankRow)=>s.rank===1));
const changedTop=computed(()=>curTop.value&&oldTop.value&&curTop.value.code!==oldTop.value.code);
</script>

<template>
  <section class="compare-panel">
    <div class="section-line">
      <h2 class="ruled-title">新旧权衡对照 <small>同偏好 · 同源研究 · 数据修订前后</small></h2>
      <label class="inline-select">对照版本
        <select :value="otherId" @change="choose(Number(($event.target as HTMLSelectElement).value))">
          <option :value="0">— 请选择 —</option>
          <option v-for="r in family.filter(x=>x.id!==run.id)" :key="r.id" :value="r.id">#{{r.id}} {{r.name}}（v{{r.recalc_seq||0}}）</option>
        </select>
      </label>
    </div>
    <p v-if="!family.filter(x=>x.id!==run.id).length" class="muted">该任务还没有同一链路上的其他版本；源数据修订并重算后可在此对照名次与贴近度变化。</p>
    <template v-else-if="other">
      <div class="compare-ledger">
        <div><small>当前版本 #{{run.id}}{{run.recalc_of_id?` · 重算 v${run.recalc_seq}`:' · 原始'}}</small><b>{{curTop?.code}} {{curTop?.name}}</b><span>贴近度 {{num(curTop?.score,4)}}</span></div>
        <div class="compare-arrow">⇄</div>
        <div><small>对照版本 #{{other.id}}{{other.recalc_of_id?` · 重算 v${other.recalc_seq}`:' · 原始'}}</small><b>{{oldTop?.code}} {{oldTop?.name}}</b><span>贴近度 {{num(oldTop?.score,4)}}</span></div>
      </div>
      <p v-if="changedTop" class="notice">榜首发生变化：{{oldTop?.code}} → {{curTop?.code}}；请结合右侧字段级影响范围阅读。</p>
      <p v-else class="muted">榜首未变，但各候选贴近度与情景名次仍可能移动。</p>
      <div class="table-scroll">
        <table class="compare-table">
          <thead><tr><th>试样</th><th>当前名次</th><th>对照名次</th><th>名次变化</th><th>当前贴近度</th><th>对照贴近度</th><th>贴近度变化</th><th>首位份额变化</th></tr></thead>
          <tbody>
            <tr v-for="r in rows" :key="r.cur.code" :class="{moved:!!r.rankDelta}">
              <td><b>{{r.cur.code}}</b> <small>{{r.cur.name}}</small></td>
              <td>{{rank(r.cur.rank)}}</td>
              <td>{{r.old?rank(r.old.rank):'—'}}</td>
              <td>
                <span v-if="r.rankDelta==null" class="muted">—</span>
                <b v-else-if="r.rankDelta>0" class="up">↑ {{r.rankDelta}}</b>
                <b v-else-if="r.rankDelta<0" class="down">↓ {{Math.abs(r.rankDelta)}}</b>
                <span v-else>持平</span>
              </td>
              <td>{{num(r.cur.score,4)}}</td>
              <td>{{r.old?num(r.old.score,4):'—'}}</td>
              <td><span :class="r.scoreDelta&&r.scoreDelta>0?'up':r.scoreDelta&&r.scoreDelta<0?'down':''">{{r.scoreDelta==null?'—':(r.scoreDelta>0?'+':'')+num(r.scoreDelta,4)}}</span></td>
              <td v-if="r.old">{{percent(r.cur.first_share-r.old.first_share)}}</td><td v-else class="muted">—</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="muted">名次变化以对照版本为基准：↑ 表示当前版本名次更靠前。两版结果均完整保留，已批准试样计划仍以批准时的快照指纹为依据。</p>
    </template>
  </section>
</template>
