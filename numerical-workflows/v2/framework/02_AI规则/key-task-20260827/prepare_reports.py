import hashlib,json,shutil
from pathlib import Path
from datetime import datetime
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]; RUN=ROOT/'05_验算核算'/'映射之匙任务_20260827'
report=json.loads((RUN/'staged-validation.json').read_text(encoding='utf-8'))
assert report['status']=='PASS_STATIC_WITH_RUNTIME_GATES'
files=[]
for f in ['任务/任务配置校验.json','无限之旅/无限之旅配置校验.json','主线高难/主线高难奖励配置校验.json']:
    dest=ROOT/'06_最终配置'/f;stage=RUN/'stage'/f;stage.parent.mkdir(parents=True,exist_ok=True)
    old=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else None
    backup=RUN/'backup'/f
    if dest.exists():
        backup.parent.mkdir(parents=True,exist_ok=True)
        if not backup.exists():shutil.copy2(dest,backup)
    content={'batch':'KEY-TASK-20260827','generated_at':datetime.now().isoformat(),'status':report['status'],'scope':'06候选局部落表；SVN未改；历史整包结果不作为本轮全量验收证明','current_validation':'../../05_验算核算/映射之匙任务_20260827/published-validation.json','weekly_keys':41,'monthly_keys':8,'runtime_gates':report['runtime_gates'],'previous_validation':old}
    if f.startswith('任务'):content.update(daily_count=10,weekly_count=33,task_keys_per_week=31,seven_day_keys=8,task_unlocks={'arena':123,'mapping':140})
    elif f.startswith('无限'):content.update(reward_packages=40,drop_rows=120,keys_per_difficulty=10,exclusive_difficulties=True,nr_totals=report['nr_totals'])
    else:content.update(drop_rows=999,chapter_id=10002,stars=36,drop_id=11000012,key_increment=5,other_rewards_preserved=True)
    stage.write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
    files.append({'file':f,'source':str(dest),'backup':str(backup),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None,'stage_sha256':hashlib.sha256(stage.read_bytes()).hexdigest()})
plan=json.loads((RUN/'plan.json').read_text(encoding='utf-8'))
for f in plan['files']:f['stage_sha256']=hashlib.sha256((RUN/'stage'/f['file']).read_bytes()).hexdigest()
plan['reports']=files
(RUN/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('Staged report files:',len(files))
