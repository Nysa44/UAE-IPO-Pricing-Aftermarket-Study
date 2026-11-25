from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def build_deck(path, metrics, peer_summary, chart_paths, data_mode="ILLUSTRATIVE"):
    prs=Presentation()
    prs.slide_width= Inches(13.333)
    prs.slide_height= Inches(7.5)
    navy=RGBColor(23,54,93); grey=RGBColor(90,100,110)
    def add_title(slide,title,subtitle):
        box=slide.shapes.add_textbox(Inches(.6), Inches(.35), Inches(12), Inches(.65))
        p=box.text_frame.paragraphs[0]; p.text=title; p.font.size=Pt(26); p.font.bold=True; p.font.color.rgb=navy
        sub=slide.shapes.add_textbox(Inches(.62), Inches(1.02), Inches(12), Inches(.35))
        q=sub.text_frame.paragraphs[0]; q.text=subtitle; q.font.size=Pt(10); q.font.color.rgb=grey
    def add_bullet(slide, text, y):
        box=slide.shapes.add_textbox(Inches(.8), Inches(y), Inches(11.8), Inches(.55))
        p=box.text_frame.paragraphs[0]; p.text="• "+text; p.font.size=Pt(17); p.font.color.rgb=grey
    # Slide 1
    s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,"UAE IPO Pricing & Aftermarket Study",f"{data_mode} DATA — replace with verified exchange and prospectus data")
    n=len(metrics)
    avg=metrics["first_day_return"].mean()*100 if n else float("nan")
    med=metrics["first_day_return"].median()*100 if n else float("nan")
    add_bullet(s,f"Sample: {n} IPOs across {metrics['exchange'].nunique() if n else 0} exchange(s)",1.65)
    add_bullet(s,f"Average first-day return: {avg:.1f}% | Median: {med:.1f}%",2.45)
    add_bullet(s,"Coverage: offer terms, demand, market-adjusted returns, volatility and traded value",3.25)
    add_bullet(s,"Selection rule and source traceability should be documented before drawing market conclusions",4.05)
    if chart_paths.get("first_day") and Path(chart_paths["first_day"]).exists():
        s.shapes.add_picture(str(chart_paths["first_day"]), Inches(7.1), Inches(1.55), width=Inches(5.5))
    # Slide 2
    s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,"Pricing versus peers & aftermarket performance","Descriptive comparison; peer set and valuation basis must be consistent")
    if chart_paths.get("returns") and Path(chart_paths["returns"]).exists():
        s.shapes.add_picture(str(chart_paths["returns"]), Inches(.7), Inches(1.5), width=Inches(6.0))
    if chart_paths.get("scatter") and Path(chart_paths["scatter"]).exists():
        s.shapes.add_picture(str(chart_paths["scatter"]), Inches(6.8), Inches(1.5), width=Inches(5.8))
    add_bullet(s,"Compare offer P/E with the average selected peer P/E; disclose peer count and observation date",6.35)
    # Slide 3
    s=prs.slides.add_slide(prs.slide_layouts[6]); add_title(s,"What this may mean for a future offering","Implications are hypotheses to test, not causal conclusions")
    add_bullet(s,"Pricing: assess the offer multiple against a transparent, relevant peer set and market conditions",1.7)
    add_bullet(s,"Demand: interpret oversubscription alongside tranche mix, investor type and allocation mechanics",2.6)
    add_bullet(s,"Aftermarket: monitor excess returns, volatility and traded value—not headline price performance alone",3.5)
    add_bullet(s,"Execution: use comparable IPO evidence to frame valuation range, deal size and investor messaging",4.4)
    add_bullet(s,"Caveat: small sample, changing market regimes and selection bias prevent strong statistical claims",5.3)
    prs.save(path)
