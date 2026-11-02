from sqlalchemy.orm import Session

from app.models import Comparison


def record_comparison(db: Session, steam_id_a: str, steam_id_b: str) -> Comparison:
    """Save a successful comparison with the database-generated timestamp."""
    comparison = Comparison(player_a_id=int(steam_id_a), player_b_id=int(steam_id_b))
    db.add(comparison)
    db.commit()
    db.refresh(comparison)
    return comparison
