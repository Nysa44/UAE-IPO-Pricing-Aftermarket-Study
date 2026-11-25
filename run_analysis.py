import argparse, json
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.analysis import calculate_ipo_metrics, peer_comparison
from src.workbook import build_workbook
from src.presentation import build_deck

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description="Run UAE IPO pricing and aftermarket analysis")
    parser.add_argument("--demo",action="store_true",help="Run the included synthetic illustrative dataset")
    args=parser.parse_args()
    config=json.loads((ROOT/"config.json").read_text())
    mode=config.get("data_mode","RESEARCH")
    if args.demo: mode="ILLUSTRATIVE"
    raw=ROOT/"data"/"raw"
    master=pd.read_csv(raw/"ipo_master.csv")
    prices=pd.read_csv(raw/"ipo_prices.csv")
    index=pd.read_csv(raw/"market_index.csv")
    peers=pd.read_csv(raw/"peer_valuations.csv")
    if mode=="RESEARCH" and any(master.get("data_status",pd.Series(dtype=str)).eq("ILLUSTRATIVE")):
        raise SystemExit("Illustrative rows detected. Replace them with verified research data or run explicitly with --demo.")
    metrics=calculate_ipo_metrics(master,prices,index,config["return_horizons_calendar_days"],config["annualisation_days"])
    peer_summary=peer_comparison(master,peers)
    out=ROOT/"outputs"; charts=out/"charts"; charts.mkdir(parents=True,exist_ok=True)
    metrics.to_csv(out/"ipo_summary.csv",index=False)
    peer_summary.to_csv(out/"peer_valuation_comparison.csv",index=False)
    # Chart 1: first-day returns
    fig,ax=plt.subplots(figsize=(8,4.5))
    ax.bar(metrics["company"],metrics["first_day_return"]*100)
    ax.set_ylabel("First-day return (%)"); ax.set_title("IPO first-day performance")
    ax.tick_params(axis="x",rotation=20); fig.tight_layout()
    first=charts/"first_day_returns.png"; fig.savefig(first,dpi=160); plt.close(fig)
    # Chart 2: horizon returns
    cols=["first_day_return","1_week_return","1_month_return","3_months_return"]
    labels=["First day","1 week","1 month","3 months"]
    means=[metrics[c].mean()*100 for c in cols]
    fig,ax=plt.subplots(figsize=(8,4.5)); ax.bar(labels,means)
    ax.set_ylabel("Mean return (%)"); ax.set_title("Average IPO return by horizon")
    fig.tight_layout(); returns=charts/"returns_by_horizon.png"; fig.savefig(returns,dpi=160); plt.close(fig)
    # Chart 3: demand versus first day
    scatter=charts/"oversubscription_vs_first_day.png"
    valid=metrics.dropna(subset=["subscription_multiple","first_day_return"])
    fig,ax=plt.subplots(figsize=(7,4.5))
    if len(valid):
        ax.scatter(valid["subscription_multiple"],valid["first_day_return"]*100)
        for _,r in valid.iterrows():
            ax.annotate(r["company"],(r["subscription_multiple"],r["first_day_return"]*100),fontsize=8)
    ax.set_xlabel("Subscription multiple (x)"); ax.set_ylabel("First-day return (%)")
    ax.set_title("Oversubscription vs first-day return (small sample)")
    fig.tight_layout(); fig.savefig(scatter,dpi=160); plt.close(fig)
    build_workbook(out/"UAE_IPO_Analysis.xlsx",master,prices,index,peers,metrics,peer_summary)
    build_deck(out/"UAE_ECM_Market_Review.pptx",metrics,peer_summary,
               {"first_day":first,"returns":returns,"scatter":scatter},mode)
    print(f"Analysis complete ({mode}). Outputs saved to {out}")

if __name__=="__main__": main()
