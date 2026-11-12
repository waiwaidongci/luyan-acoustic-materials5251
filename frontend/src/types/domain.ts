export interface User{id:number;name:string;email:string;role:'admin'|'analyst'|'viewer'}
export type MetricCode='absorption'|'impact'|'carbon'|'price'|'thickness';export type Direction='benefit'|'cost';
export interface Study{id:number;code:string;name:string;context:string;source_file:string;material_ids:number[]}
export interface Sample{id:number;code:string;name:string;family:string;absorption:number;impact:number;carbon:number;price:number;thickness:number;batch:string}
export interface Criterion{id:number;study_id:number;code:MetricCode;name:string;unit:string;direction:Direction;center_weight:number}
export interface RankRow extends Sample{score:number;rank:number;distance_best:number;distance_worst:number;rank_min:number;rank_max:number;rank_low:number;rank_median:number;rank_high:number;first_share:number;rank_frequency:Record<string,number>;normalized:number[];weighted:number[]}
export interface Draw{repeat:number;weights:number[];scores:number[];ranks:number[];first_share:number[];all_indistinguishable:boolean}
export interface Result{samples:RankRow[];criteria:Criterion[];columns:{index:number;norm:number;constant:boolean;zero_norm:boolean;policy:string}[];center_weights:number[];alpha:number[];concentration:number;repeats:number;seed:number;ideal_best:number[];ideal_worst:number[];all_indistinguishable:boolean;draws:Draw[];zero_weight_scenarios:number;fingerprint:string;scope:string;snapshot:Snapshot}
export interface Snapshot{study:Study;samples:Sample[];criteria:Criterion[]}
export interface RunSummary{id:number;name:string;study_id:number;center_weights:Record<string,number>;concentration:number;repeats:number;seed:number;status:'queued'|'running'|'completed'|'failed';summary:{samples:number;criteria:number;fingerprint?:string;all_indistinguishable?:boolean;recalc_of?:number;recalc_seq?:number};error:string;source_fingerprint?:string;recalc_of_id?:number|null;recalc_seq?:number;recalc_status?:string;created_at:string}
export interface Run extends RunSummary{snapshot:Snapshot;result:Result}
export interface SourceChange{sample_id?:number;code?:string;name?:string;kind:'changed'|'added'|'removed';fields:string[];before?:Record<string,number>;after?:Record<string,number>}
export interface StaleReport{run_id:number;name:string;study_id:number;status:string;stale:boolean;source_fingerprint:string;current_fingerprint:string;sample_changes:SourceChange[];criterion_changes:SourceChange[];affected_sample_ids:number[];recalc_of_id?:number|null;recalc_seq:number;recalc_status:string;created_at:string}
export interface BatchRecalcResult{queued:{run_id:number;recalc_id:number;recalc_seq:number}[];skipped:{run_id:number;reason:string;recalc_id?:number}[];up_to_date:{run_id:number;recalc_id:number}[]}
export interface Note{id:number;name:string;run_id:number;sample_id:number;protocol:string;status:'draft'|'approved'|'rejected';reviewer_note:string;reviewed_by:string;created_at:string}
