<script setup lang="ts">
import {computed} from 'vue';
import {useResearch} from '../stores/research';
const props=defineProps<{runId:number;small?:boolean}>();
const research=useResearch();
const report=computed(()=>research.staleById.get(props.runId));
const count=computed(()=>{
  if(!report.value?.stale)return 0;
  return report.value.sample_changes.length+report.value.criterion_changes.length;
});
</script>
<template>
  <span v-if="report?.stale" :class="['stale-badge',{small}].filter(Boolean).join(' ')"
    :title="`源数据已更新：${count} 项变化，旧结果保留为对照依据`">源数据已过期 · {{count}} 项变化</span>
  <span v-else-if="report && !report.stale" class="fresh-badge" :class="{small}">源数据一致</span>
</template>
