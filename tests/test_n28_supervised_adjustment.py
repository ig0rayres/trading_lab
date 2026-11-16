"""N28.2–4 — supervised parameter path; risk anchors immutable."""
import json
import tempfile
import unittest
from pathlib import Path
from supervised_adjustment import (
    RISK_ANCHOR_FIELDS,
    apply_proposal,
    get_current_value,
    is_risk_anchor,
    load_overrides,
    propose_adjustment,
    read_adjustments,
    undo_adjustment,
)
from v4_web_dashboard import TRIGGER_PATCH_FIELDS


class N28SupervisedAdjustmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'evolution'
        self.root.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_n28_2_in_range_proposal_can_apply(self):
        row = propose_adjustment(
            strategy_key='signal_copy',
            parameter='ttl_seconds',
            proposed_value=45,
            reason='homolog tighter ttl',
            root=self.root,
        )
        self.assertEqual(row['status'], 'proposed')
        self.assertTrue(row['can_apply'])
        self.assertFalse(row['execution_authorized'])
        unknown = propose_adjustment(
            strategy_key='momentum',
            parameter='rsi_period',
            proposed_value=14,
            reason='would invent threshold',
            root=self.root,
        )
        self.assertEqual(unknown['status'], 'suggestion_only')
        self.assertFalse(unknown.get('can_apply'))

    def test_n28_2_out_of_range_rejected(self):
        row = propose_adjustment(
            strategy_key='signal_copy',
            parameter='ttl_seconds',
            proposed_value=90,
            reason='above documented max',
            root=self.root,
        )
        self.assertEqual(row['status'], 'rejected')
        self.assertEqual(row['reject_code'], 'OUT_OF_ORIGINAL_RANGE')

    def test_n28_3_apply_undo_persist_before_after_reason(self):
        proposal = propose_adjustment(
            strategy_key='prodigy_15d',
            parameter='ttl_seconds',
            proposed_value=40,
            reason='daily review',
            root=self.root,
        )
        applied, err = apply_proposal(proposal['id'], root=self.root)
        self.assertIsNone(err)
        self.assertEqual(applied['status'], 'applied')
        self.assertEqual(applied['after_value'], 40)
        self.assertEqual(get_current_value('prodigy_15d', 'ttl_seconds', self.root), 40)
        ledger = read_adjustments(self.root)
        self.assertTrue(any(r.get('status') == 'applied' for r in ledger))
        undo, uerr = undo_adjustment(applied['id'], root=self.root)
        self.assertIsNone(uerr)
        self.assertEqual(undo['status'], 'undone')
        self.assertIsNone(get_current_value('prodigy_15d', 'ttl_seconds', self.root))
        self.assertTrue(any(r.get('status') == 'undone' for r in read_adjustments(self.root)))

    def test_n28_4_never_mutates_risk_anchors(self):
        self.assertEqual(RISK_ANCHOR_FIELDS, TRIGGER_PATCH_FIELDS)
        for field in RISK_ANCHOR_FIELDS:
            self.assertTrue(is_risk_anchor(field))
            row = propose_adjustment(
                strategy_key='signal_copy',
                parameter=field,
                proposed_value=1,
                reason='must not apply',
                root=self.root,
            )
            self.assertEqual(row['reject_code'], 'RISK_ANCHOR_FORBIDDEN')
        proposal = propose_adjustment(
            strategy_key='signal_copy',
            parameter='ttl_seconds',
            proposed_value=50,
            reason='anchor isolation check',
            root=self.root,
        )
        apply_proposal(proposal['id'], root=self.root)
        blob = json.dumps(load_overrides(self.root))
        for anchor in RISK_ANCHOR_FIELDS:
            self.assertNotIn(anchor, blob)


if __name__ == '__main__':
    unittest.main()