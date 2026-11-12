<script setup lang="ts">
import {computed,ref} from 'vue';
import {useRouter} from 'vue-router';
import {useResearch} from '../stores/research';
import {useAuth} from '../stores/auth';
import {useTask} from '../hooks/useTask';
import {recalcStatus} from '../constants/enums';
import {date} from '../utils/format';
import StatusBadge from './common/StatusBadge.vue';
import StaleBadge from './StaleBadge.vue';
import ImpactScope from './ImpactScope.vue';
import type {StaleReport} from '../types/domain';

const props=defineProps<{report:StaleReport}>();
const research=useResearch(),auth=useAuth(),router=useRouter(),{busy,perform}=useTask();
const expanded=ref(false);
const recalc=computed(()=>research.recalcByRoot.get(props.report.run_id)||null);

async function openRun(id:number){await research.select(id);router.push('/results');}
async function recalcOne(){await research.recalculate(props.report.run_id);}
async function retryOne(id:number){await research.retry(id);}
</script>

<template>
  <article class="stale-entry">
    <div class="entry-line">
      <StaleBadge :run-id="report.run_id"/>
      <small>原始任务 #{{report.run_id}} · {{date(report.created_at)}}</small>
    </div>
    <h3>{{report.name}}</h3>
    <p class="muted">试样变化 {{report.sample_changes.length}} 项 · 指标变化 {{report.criterion_changes.length}} 项 · 受影响试样 {{report.affected_sample_ids.length}} 份</p>
    <div class="button-row">
      <button class="small-button" @click="expanded=!expanded">{{expanded?'收起影响范围':'查看影响范围'}}</button>
      <button class="small-button" @click="perform(()=>openRun(report.run_id))">阅读旧权衡 ↗</button>
      <template v-if="recalc">
        <button class="small-button" @click="perform(()=>openRun(recalc!.id))">查看新权衡 #{{recalc!.id}} ↗</button>
        <StatusBadge :status="recalc!.status"/>
        <small v-if="recalc!.recalc_status" class="muted">{{recalcStatus[recalc!.recalc_status as keyof typeof recalcStatus]}}</small>
        <button v-if="recalc!.status==='failed'&&auth.canEdit" class="small-button" :disabled="busy" @click="perform(()=>retryOne(recalc!.id))">重试重算</button>
        <p v-if="recalc!.status==='failed'&&recalc!.error" class="error-text">失败原因：{{recalc!.error}}（旧计划仍可正常分发，可重试）</p>
      </template>
      <button v-else-if="auth.canEdit" class="primary" :disabled="busy" @click="perform(recalcOne)">按原偏好重算 →</button>
    </div>
    <ImpactScope v-if="expanded" :report="report"/>
  </article>
</template>
