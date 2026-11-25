import pandas as pd
import numpy as np
import pytest
from src.analysis import simple_return, validate_inputs, calculate_ipo_metrics

def small_inputs():
    master=pd.DataFrame([{"ipo_id":"X","company":"Demo","exchange":"ADX","listing_date":"2025-01-01","currency":"AED","offer_price":10.0,"subscription_multiple":5.0,"offer_pe":15.0}])
    prices=pd.DataFrame([
        ["X","2025-01-01",11.0,1000],["X","2025-01-08",12.0,1200],
        ["X","2025-01-31",12.5,1300],["X","2025-04-01",13.0,1400]
    ],columns=["ipo_id","date","close","volume"])
    index=pd.DataFrame([["2025-01-01",100.0],["2025-01-08",101.0],["2025-01-31",102.0],["2025-04-01",103.0]],columns=["date","index_close"])
    return master,prices,index

def test_simple_return_positive():
    assert simple_return(10,12)==pytest.approx(0.2)

def test_simple_return_negative():
    assert simple_return(10,9)==pytest.approx(-0.1)

def test_simple_return_invalid_base():
    assert np.isnan(simple_return(0,10))

def test_valid_inputs_pass():
    m,p,i=small_inputs()
    validate_inputs(m,p,i)

def test_duplicate_ipo_id_rejected():
    m,p,i=small_inputs()
    m=pd.concat([m,m],ignore_index=True)
    with pytest.raises(ValueError,match="duplicate"):
        validate_inputs(m,p,i)

def test_missing_price_rejected():
    m,p,i=small_inputs()
    p.loc[0,"close"]=np.nan
    with pytest.raises(ValueError,match="missing"):
        validate_inputs(m,p,i)

def test_negative_volume_rejected():
    m,p,i=small_inputs()
    p.loc[0,"volume"]=-1
    with pytest.raises(ValueError,match="volume"):
        validate_inputs(m,p,i)

def test_duplicate_date_rejected():
    m,p,i=small_inputs()
    p=pd.concat([p,p.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="duplicate"):
        validate_inputs(m,p,i)

def test_first_day_and_excess_return_math():
    m,p,i=small_inputs()
    result=calculate_ipo_metrics(m,p,i,{"1_week":7,"1_month":30,"3_months":90})
    row=result.iloc[0]
    assert row["first_day_return"]==pytest.approx(0.10)
    assert row["1_week_return"]==pytest.approx(0.20)
    assert row["1_week_index_return"]==pytest.approx(0.01)
    assert row["1_week_excess_return"]==pytest.approx(0.19)

def test_missing_ipo_price_series_rejected():
    m,p,i=small_inputs()
    p=p[p["ipo_id"]!="X"]
    with pytest.raises(ValueError,match="No price observations"):
        calculate_ipo_metrics(m,p,i)
