from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import yaml
from src.generator.core import generate_all
from src.rules.payouts import calculate_payouts
from src.validation.validate import validate

def test_small_generation():
    cfg=yaml.safe_load(Path("configs/starter.yaml").read_text())
    d=generate_all(cfg)
    assert len(d["seller"])==20
    assert len(d["product_listing"])==100
    assert len(d["orders"])==500
    assert d["seller"].seller_id.is_unique
    assert d["product_listing"].listing_id.is_unique

def test_foreign_keys():
    cfg=yaml.safe_load(Path("configs/starter.yaml").read_text())
    d=generate_all(cfg)
    assert set(d["order_line"].order_id)<=set(d["orders"].order_id)
    assert set(d["order_line"].listing_id)<=set(d["product_listing"].listing_id)
    assert set(d["fulfillment"].order_line_id)<=set(d["order_line"].order_line_id)

def test_payout_lines():
    cfg=yaml.safe_load(Path("configs/starter.yaml").read_text())
    d=generate_all(cfg)
    p,pl=calculate_payouts(d,cfg)
    assert set(pl.payout_id)<=set(p.payout_id) if len(pl) else True
