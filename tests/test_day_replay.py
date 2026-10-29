import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from day_radar import assess
from day_replay import replay_day,run

class DirectionalReplayTests(unittest.TestCase):
    def bars(self, down=False):
        a=[]
        for i in range(78):
            m=9*60+30+i*5;t=f'{m//60:02d}:{m%60:02d}'
            o=h=l=c=100.0
            if i==3:
                o=100;h=103;l=97;c=98 if down else 102
            if i==4:
                o=98 if down else 102
                h=104 if not down else 99
                l=96 if down else 101
                c=96 if down else 104
            a.append({'day':'2026-10-26','time':t,'open':o,'high':h,'low':l,'close':c,'volume':1000})
        return a
    def test_confirmation_is_bar_end(self):
        bars=self.bars()
        x=assess('AAA',[dict(b,day='2026-10-27') for b in bars],datetime(2026,10,27,14,tzinfo=ZoneInfo('America/New_York')))
        self.assertEqual(x['research_setups']['LONG']['first_confirmation_bar_ny'],'09:45')
        self.assertEqual(x['research_setups']['LONG']['confirmation_available_at_ny'],'09:50')
    def test_next_bar_entry_long(self):
        x=replay_day(self.bars(),'LONG')
        self.assertEqual(x['status'],'EVALUATED');self.assertEqual(x['entry'],102)
        self.assertEqual(x['first_actionable_bar_start'],'09:50')
    def test_short_next_bar(self):
        x=replay_day(self.bars(True),'SHORT')
        self.assertEqual(x['status'],'EVALUATED');self.assertEqual(x['entry'],98)
        self.assertEqual(x['confirmation_available_at'],'09:50')
    def test_missing_opening_rejected(self):
        self.assertEqual(replay_day(self.bars()[1:],'SHORT')['status'],'MISSING_OPENING')
    def test_no_orders_or_live(self):
        now=datetime(2026,10,27,18,tzinfo=timezone.utc)
        o=run(['AAA'],fetch=lambda sym,t:self.bars(),now_utc=now,sessions=1,output=None)
        self.assertEqual(o['orders_sent'],0)
        self.assertTrue(all(r['side'] in ('LONG','SHORT') for r in o['results']))

if __name__=='__main__':unittest.main()
