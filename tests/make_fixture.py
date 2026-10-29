import csv,datetime as dt,random
from pathlib import Path
rng=random.Random(42)
p=Path(__file__).resolve().parents[1]/'data'/'SYNTHETIC_SMOKE_ONLY.csv'
with p.open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['timestamp','open','high','low','close','volume','session'])
 day=dt.date(2026,1,5)
 for k in range(90):
  d=day+dt.timedelta(days=k)
  if d.weekday()>=5:continue
  price=100+rng.uniform(-4,4)
  for i in range(78):
   ts=dt.datetime.combine(d,dt.time(9,30),dt.timezone(dt.timedelta(hours=-5)))+dt.timedelta(minutes=5*i)
   op=price;price=op*(1+rng.gauss(0,.002));lo=min(op,price)*(1-rng.uniform(0,.001));hi=max(op,price)*(1+rng.uniform(0,.001))
   w.writerow([ts.isoformat(),f'{op:.5f}',f'{hi:.5f}',f'{lo:.5f}',f'{price:.5f}',rng.randint(1000,12000),d.isoformat()])
print(p)
