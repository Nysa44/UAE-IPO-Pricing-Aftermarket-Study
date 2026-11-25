from __future__ import annotations
import numpy as np
import pandas as pd

REQUIRED_MASTER = {"ipo_id","company","exchange","listing_date","currency","offer_price"}
REQUIRED_PRICES = {"ipo_id","date","close","volume"}
REQUIRED_INDEX = {"date","index_close"}

def validate_inputs(master: pd.DataFrame, prices: pd.DataFrame, index: pd.DataFrame) -> None:
    missing = REQUIRED_MASTER - set(master.columns)
    if missing:
        raise ValueError(f"ipo_master missing columns: {sorted(missing)}")
    missing = REQUIRED_PRICES - set(prices.columns)
    if missing:
        raise ValueError(f"ipo_prices missing columns: {sorted(missing)}")
    missing = REQUIRED_INDEX - set(index.columns)
    if missing:
        raise ValueError(f"market_index missing columns: {sorted(missing)}")
    if master["ipo_id"].duplicated().any():
        raise ValueError("ipo_master contains duplicate ipo_id values")
    if (pd.to_numeric(master["offer_price"], errors="coerce").dropna() <= 0).any():
        raise ValueError("offer_price must be positive")
    if prices[["close","volume"]].isna().any().any():
        raise ValueError("price file contains missing close or volume values")
    if (pd.to_numeric(prices["close"], errors="coerce") <= 0).any():
        raise ValueError("daily close must be positive")
    if (pd.to_numeric(prices["volume"], errors="coerce") < 0).any():
        raise ValueError("volume cannot be negative")
    if prices.duplicated(["ipo_id","date"]).any():
        raise ValueError("duplicate IPO/date observations found")
    if index.duplicated(["date"]).any():
        raise ValueError("duplicate market index dates found")

def simple_return(start: float, end: float) -> float:
    if start is None or end is None or pd.isna(start) or pd.isna(end) or start <= 0:
        return np.nan
    return float(end / start - 1.0)

def _next_observation(frame: pd.DataFrame, target: pd.Timestamp, column: str):
    subset = frame.loc[frame["date"] >= target].sort_values("date")
    if subset.empty:
        return np.nan, pd.NaT
    row = subset.iloc[0]
    return float(row[column]), row["date"]

def calculate_ipo_metrics(master: pd.DataFrame, prices: pd.DataFrame,
                          index: pd.DataFrame, horizons=None,
                          annualisation_days: int = 252) -> pd.DataFrame:
    validate_inputs(master, prices, index)
    horizons = horizons or {"1_week":7,"1_month":30,"3_months":90}
    p = prices.copy()
    p["date"] = pd.to_datetime(p["date"], errors="raise")
    p["close"] = pd.to_numeric(p["close"], errors="raise")
    p["volume"] = pd.to_numeric(p["volume"], errors="raise")
    ix = index.copy()
    ix["date"] = pd.to_datetime(ix["date"], errors="raise")
    ix["index_close"] = pd.to_numeric(ix["index_close"], errors="raise")
    rows=[]
    for _, ipo in master.iterrows():
        listing = pd.Timestamp(ipo["listing_date"])
        deal = p[p["ipo_id"] == ipo["ipo_id"]].sort_values("date")
        if deal.empty:
            raise ValueError(f"No price observations for {ipo['ipo_id']}")
        first=deal.iloc[0]
        offer=float(ipo["offer_price"])
        result={
            "ipo_id":ipo["ipo_id"], "company":ipo["company"],
            "exchange":ipo["exchange"], "listing_date":listing.date().isoformat(),
            "offer_price":offer, "first_day_close":float(first["close"]),
            "first_day_return":simple_return(offer,float(first["close"])),
            "first_day_volume":int(first["volume"]),
            "subscription_multiple":pd.to_numeric(pd.Series([ipo.get("subscription_multiple",np.nan)]),errors="coerce").iloc[0],
            "offer_pe":pd.to_numeric(pd.Series([ipo.get("offer_pe",np.nan)]),errors="coerce").iloc[0]
        }
        result["first_day_traded_value"]=float(first["close"]*first["volume"])
        for label,days in horizons.items():
            target=listing+pd.Timedelta(days=int(days))
            close,obs_date=_next_observation(deal,target,"close")
            idx_start,idx_start_date=_next_observation(ix,first["date"],"index_close")
            idx_end,idx_end_date=_next_observation(ix,target,"index_close")
            ipo_ret=simple_return(offer,close)
            idx_ret=simple_return(idx_start,idx_end)
            result[f"{label}_close"]=close
            result[f"{label}_observation_date"]=obs_date.date().isoformat() if pd.notna(obs_date) else None
            result[f"{label}_return"]=ipo_ret
            result[f"{label}_index_return"]=idx_ret
            result[f"{label}_excess_return"]=ipo_ret-idx_ret if pd.notna(ipo_ret) and pd.notna(idx_ret) else np.nan
        daily_returns=deal["close"].pct_change().dropna()
        result["annualised_volatility"]=float(daily_returns.std(ddof=1)*np.sqrt(annualisation_days)) if len(daily_returns)>1 else np.nan
        result["average_daily_traded_value"]=float((deal["close"]*deal["volume"]).mean())
        result["trading_days_observed"]=int(len(deal))
        rows.append(result)
    out=pd.DataFrame(rows)
    return out

def peer_comparison(master: pd.DataFrame, peers: pd.DataFrame) -> pd.DataFrame:
    if peers.empty:
        return pd.DataFrame(columns=["ipo_id","company","offer_pe","peer_average_pe","offer_pe_discount_premium_pct","peer_count"])
    peer_copy=peers.copy()
    peer_copy["peer_pe"]=pd.to_numeric(peer_copy["peer_pe"],errors="coerce")
    peer_avg=peer_copy.groupby("ipo_id")["peer_pe"].agg(["mean","count"]).reset_index()
    merged=master[["ipo_id","company","offer_pe"]].merge(peer_avg,on="ipo_id",how="left")
    merged["offer_pe"]=pd.to_numeric(merged["offer_pe"],errors="coerce")
    merged["offer_pe_discount_premium_pct"]=merged["offer_pe"]/merged["mean"]-1
    return merged.rename(columns={"mean":"peer_average_pe","count":"peer_count"})
