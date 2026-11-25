from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def build_workbook(path, master, prices, index, peers, metrics, peer_summary):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with pd.ExcelWriter(path,engine="openpyxl") as writer:
        master.to_excel(writer,sheet_name="IPO Inputs & Sources",index=False)
        prices.to_excel(writer,sheet_name="Daily IPO Prices",index=False)
        index.to_excel(writer,sheet_name="Market Index",index=False)
        peers.to_excel(writer,sheet_name="Peer Inputs",index=False)
        metrics.to_excel(writer,sheet_name="IPO Calculations",index=False)
        peer_summary.to_excel(writer,sheet_name="Peer Comparison",index=False)
        pd.DataFrame({
            "Metric":["First-day return","1-week / 1-month / 3-month return","Excess return","Annualised volatility","Average daily traded value"],
            "Definition":["First-day close / offer price - 1","First available close on or after 7 / 30 / 90 calendar days after listing, divided by offer price - 1","IPO holding-period return less matched index return","Standard deviation of daily simple returns multiplied by sqrt(252)","Mean of daily close multiplied by daily share volume"],
            "Caveat":["Offer price is the base, not previous close","Next available trading date is used when target falls on a non-trading day","Simple benchmark excess return; not a factor model","Requires at least two daily return observations","Not free-float turnover"]
        }).to_excel(writer,sheet_name="Methodology",index=False)
    wb=load_workbook(path)
    for ws in wb.worksheets:
        ws.freeze_panes="A2"
        ws.auto_filter.ref=ws.dimensions
        for cell in ws[1]:
            cell.font=Font(bold=True,color="FFFFFF")
            cell.fill=PatternFill("solid",fgColor="17365D")
            cell.alignment=Alignment(wrap_text=True,vertical="center")
        ws.row_dimensions[1].height=32
        for col in ws.columns:
            letter=get_column_letter(col[0].column)
            maxlen=max((len(str(c.value)) if c.value is not None else 0) for c in col[:100])
            ws.column_dimensions[letter].width=min(max(maxlen+2,12),42)
    wb.save(path)
