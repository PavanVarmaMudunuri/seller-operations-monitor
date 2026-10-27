import argparse, json, hashlib, shutil
from pathlib import Path
import pandas as pd
import yaml
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.generator.core import generate_all
from src.rules.payouts import calculate_payouts
from src.anomalies.injector import inject_anomalies
from src.validation.validate import validate
from src.analytics.metrics import calculate_metrics

def write_csv(df,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(path,index=False)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",required=True)
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    cfg=yaml.safe_load((root/args.config).read_text())
    out=root/"data"/"exports"
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    data=generate_all(cfg)
    payouts,payout_lines=calculate_payouts(data,cfg)
    data,payouts,payout_lines,ground=inject_anomalies(data,payouts,payout_lines,cfg)

    for name,df in {**data,"payout":payouts,"payout_line":payout_lines}.items():
        write_csv(df,out/f"{name}.csv")
    write_csv(ground,root/"ground_truth"/"ground_truth.csv")

    validation,recon=validate(data,payouts,payout_lines)
    write_csv(validation,root/"reports"/"validation_summary.csv")
    write_csv(recon,root/"reports"/"payout_reconciliation.csv")

    seller_metrics,payout_metrics,exception_metrics=calculate_metrics(
        data,payouts,payout_lines,ground)
    write_csv(seller_metrics,root/"reports"/"seller_metrics.csv")
    write_csv(payout_metrics,root/"reports"/"payout_metrics.csv")
    write_csv(exception_metrics,root/"reports"/"exception_metrics.csv")

    manifest={}
    for p in sorted(out.glob("*.csv")):
        manifest[p.name]={
            "rows":sum(1 for _ in open(p,encoding="utf-8"))-1,
            "sha256":hashlib.sha256(p.read_bytes()).hexdigest()
        }
    repro={"seed":cfg["seed"],"config":args.config,"files":manifest}
    (root/"reports"/"reproducibility.json").write_text(json.dumps(repro,indent=2),encoding="utf-8")

    summary={
        "seed":cfg["seed"],
        "tables":{k:len(v) for k,v in {**data,"payout":payouts,"payout_line":payout_lines}.items()},
        "ground_truth_cases":len(ground),
        "validation_passed":int(validation.passed.sum()),
        "validation_total":len(validation)
    }
    (root/"reports"/"run_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
