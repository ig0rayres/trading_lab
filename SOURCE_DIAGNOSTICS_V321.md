# Source Diagnostics v3.2.1

Execute `/app/scripts/run.sh continuous-review` after deployment. Then inspect:

```sh
python3 - <<'PY'
import json
p='/app/reports/intelligence/provider-180d-latest.json'
for r in json.load(open(p))['providers']:
    print(r['name'],r['status'],r['reasons'],r.get('source_error_type'),r.get('source_error_detail'))
    print('equity keys:',r.get('equity_field_names'))
PY
```

Data fields and date formats remain fail-closed if not recognized. This build is read-only; it does not authorize Paper orders.
