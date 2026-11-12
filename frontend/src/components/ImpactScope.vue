<script setup lang="ts">
import {computed} from 'vue';
import type {StaleReport} from '../types/domain';
import {metrics,changeKind} from '../constants/enums';
import {num} from '../utils/format';
const props=defineProps<{report:StaleReport}>();
const metricName=(code:string)=>metrics[code as keyof typeof metrics]?.name||code;
const metricUnit=(code:string)=>metrics[code as keyof typeof metrics]?.unit||'';
const samples=computed(()=>props.report.sample_changes);
const criteria=computed(()=>props.report.criterion_changes);
const fmt=(v:unknown)=>typeof v==='number'?num(v,4):String(v??'—');
</script>
<template>
  <div class="impact-scope">
    <div v-if="samples.length" class="impact-block">
      <h4>受影响试样 · {{samples.length}}</h4>
      <div class="table-scroll">
        <table class="impact-table">
          <thead><tr><th>试样</th><th>变化类型</th><th>字段</th><th>冻结时 → 当前值</th></tr></thead>
          <tbody>
            <tr v-for="c in samples" :key="(c.sample_id??'')+c.kind">
              <td><b>{{c.code||('#'+c.sample_id)}}</b></td>
              <td>{{changeKind[c.kind]||c.kind}}</td>
              <td><span v-for="f in c.fields" :key="f" class="field-chip">{{metricName(f)}}</span><span v-if="!c.fields.length" class="muted">—</span></td>
              <td>
                <span v-for="f in c.fields" :key="f" class="value-pair">
                  <i class="old">{{fmt(c.before?.[f])}}</i> → <b>{{fmt(c.after?.[f])}}</b> <small>{{metricUnit(f)}}</small>；
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-if="criteria.length" class="impact-block">
      <h4>受影响指标口径 · {{criteria.length}}</h4>
      <div class="table-scroll">
        <table class="impact-table">
          <thead><tr><th>指标</th><th>变化类型</th><th>字段</th><th>冻结时 → 当前值</th></tr></thead>
          <tbody>
            <tr v-for="c in criteria" :key="c.code+c.kind">
              <td><b>{{c.name||c.code}}</b><small v-if="c.name"> / {{c.code}}</small></td>
              <td>{{changeKind[c.kind]||c.kind}}</td>
              <td><span v-for="f in c.fields" :key="f" class="field-chip">{{f==='direction'?'方向':f==='center_weight'?'中心权重':f}}</span><span v-if="!c.fields.length" class="muted">—</span></td>
              <td>
                <span v-for="f in c.fields" :key="f" class="value-pair">
                  <i class="old">{{fmt(c.before?.[f])}}</i> → <b>{{fmt(c.after?.[f])}}</b>；
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-if="!samples.length&&!criteria.length" class="muted">指纹不同但未定位到字段级差异，可能来自候选集合变化。</p>
  </div>
</template>
