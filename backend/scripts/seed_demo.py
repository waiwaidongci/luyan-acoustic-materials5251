"""Insert-only natural keys; global materials serve three candidate studies."""
import numpy as np
from sqlalchemy import select
from src.config.database import Base,engine,Session
from src.models import User,CandidateStudy,MaterialSample,Criterion
from src.utils.security import hash_password

def seed():
    Base.metadata.create_all(engine)
    with Session() as db:
        for role,name in [('admin','余芦 · 试样负责人'),('analyst','林砚 · 产品研究员'),('viewer','季乔 · 研发观察员')]:
            email=role+'@luyan.local'
            if not db.scalar(select(User).where(User.email==email)):db.add(User(email=email,name=name,role=role,password_hash=hash_password('Luyan2026!')))
        rng=np.random.default_rng(20261112);ids=[]
        for i in range(36):
            family=['芦芯纤维板','麻纤复合毡','矿纤混合板'][i//12];code=f'LY{i+1:02}';g=i//12
            a=float(rng.uniform([.62,.45,.70][g],[.93,.78,.98][g]));impact=float(rng.uniform([4,8,5][g],[9,17,12][g]));carbon=float(rng.uniform([.8,1.4,2.1][g],[1.9,3.4,4.8][g]));price=float(rng.uniform([65,75,90][g],[135,160,180][g]));thickness=float(rng.uniform([18,14,22][g],[36,30,42][g]))
            item=db.scalar(select(MaterialSample).where(MaterialSample.code==code))
            if not item:item=MaterialSample(code=code,name=family+' · '+str(i%12+1).zfill(2),family=family,absorption=a,impact=impact,carbon=carbon,price=price,thickness=thickness,batch='LYM-20261112');db.add(item);db.flush()
            ids.append(item.id)
        metrics=[('absorption','吸声系数','αw','benefit'),('impact','耐冲击','kJ/m²','benefit'),('carbon','碳强度','kgCO₂e/m²','cost'),('price','单位面积价格','元/m²','cost'),('thickness','厚度','mm','cost')]
        for code,name,weights in [('LY-BAL','芦芯展厅 · 均衡权衡',[.3,.2,.2,.2,.1]),('LY-CARBON','低碳会议室 · 碳优先',[.2,.15,.4,.15,.1]),('LY-THIN','薄型走廊 · 厚度约束',[.3,.15,.15,.15,.25])]:
            study=db.scalar(select(CandidateStudy).where(CandidateStudy.code==code))
            if not study:study=CandidateStudy(code=code,name=name,context='机构试样的偏好权重权衡；需要独立试样验证，不直接决定采购。',source_file='LYM_20261112_试样汇总.csv',material_ids=ids);db.add(study);db.flush()
            for (key,title,unit,direction),weight in zip(metrics,weights):
                if not db.scalar(select(Criterion).where(Criterion.study_id==study.id,Criterion.code==key)):db.add(Criterion(study_id=study.id,code=key,name=title,unit=unit,direction=direction,center_weight=weight))
        db.commit()
if __name__=='__main__':seed();print('seed insert-only complete')
