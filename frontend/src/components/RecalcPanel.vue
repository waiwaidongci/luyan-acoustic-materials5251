<script setup lang="ts">
import {computed,ref} from 'vue';
import {useResearch} from '../stores/research';
import {useAuth} from '../stores/auth';
import {useTask} from '../hooks/useTask';
import {date} from '../utils/format';
import StatusBadge from './common/StatusBadge.vue';
import RecalcEntry from './RecalcEntry.vue';

const props=defineProps<{studyId?:number}>();
const research=useResearch(),auth=useAuth(),{busy,perform}=useTask();
const batchMessage=ref('');

const staleRoots=computed(()=>research.staleRuns
  .filter(r=>!props.studyId||r.study_id===props.studyId)
  .filter(r=>!r.recalc_of_id));
const activeRecalcs=computed(()=>research.runs
  .filter(r=>r.recalc_of_id&&['queued','running'].includes(r.status))
  .filter(r=>!props.studyId||r.study_id===props.studyId));
const failedRecalcs=computed(()=>research.runs
  .filter(r=>r.recalc_of_id&&r.status==='failed')
  .filter(r=>!props.studyId||r.study_id===props.studyId));
const affectedSamples=computed(()=>new Set(staleRoots.value.flatMap(r=>r.affected_sample_ids)).size);

async function batch(){
  batchMessage.value='';
  const result=await research.recalculateStale(props.studyId);
  const parts=[`新排队 ${result.queued.length} 项`];
  if(result.up_to_date.length)parts.push(`已是最新 ${result.up_to_date.length} 项（未重复建任务）`);
  if(result.skipped.length)parts.push(`跳过 ${result.skipped.length} 项（${result.skipped.map(s=>s.reason).join('；')}）`);
  batchMessage.value=parts.join('，');
}
async function retryOne(id:number){batchMessage.value='';await research.retry(id);}
</script>

<template>
  <section class="recalc-panel">
    <div class="section-line">
      <h2 class="ruled-title">源数据修订与过期权衡
        <small>{{staleRoots.length}} 项过期 / 影响 {{affectedSamples}} 份试样 / 重算进行 {{activeRecalcs.length}} 项</small>
      </h2>
      <button v-if="auth.canEdit" class="primary" :disabled="busy||!staleRoots.length" @click="perform(batch)">
        {{busy?'提交中…':'按原偏好批量重算 →'}}
      </button>
    </div>
    <p class="muted">检测组修订共享资料库后，系统按冻结指纹自动标记过期权衡；重算沿用原中心权重、κ、seed 与情景数，旧结果和已批准试样计划保留原依据，可与新版本对照。重复执行同一修订不会新增任务。</p>
    <p v-if="batchMessage" class="success" role="status">{{batchMessage}}</p>

    <div v-if="activeRecalcs.length" class="recalc-progress">
      <h3>重算进度</h3>
      <article v-for="r in activeRecalcs" :key="r.id" class="progress-row">
        <StatusBadge :status="r.status"/>
        <div><b>#{{r.id}} {{r.name}}</b><small>依据原始任务 #{{r.recalc_of_id}} · 第 {{r.recalc_seq}} 版 · {{date(r.created_at)}}</small></div>
        <span class="working">队列每2.5秒刷新</span>
      </article>
    </div>

    <div v-if="!staleRoots.length&&!failedRecalcs.length" class="empty">
      <h3>没有过期权衡</h3>
      <p>已完成任务的冻结快照与当前资料库一致；修订测量值或指标口径后，这里会列出影响范围。</p>
    </div>

    <RecalcEntry v-for="rep in staleRoots" :key="rep.run_id" :report="rep"/>

    <div v-if="failedRecalcs.length" class="failed-strip">
      <h3>失败待重试 · {{failedRecalcs.length}}</h3>
      <article v-for="r in failedRecalcs" :key="r.id" class="progress-row">
        <StatusBadge :status="r.status"/>
        <div><b>#{{r.id}} {{r.name}}</b><small>{{r.error}}</small></div>
        <button v-if="auth.canEdit" class="small-button" :disabled="busy" @click="perform(()=>retryOne(r.id))">在原任务上重试</button>
      </article>
    </div>
  </section>
</template>
