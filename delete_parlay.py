from app import app, db, Parlay
with app.app_context():
    id = int(input("Enter the ID of the parlay to delete: "))
    parlay = db.session.query(Parlay).get(id)
    if parlay is None:
        print("Parlay not found.")
    else:
        db.session.delete(parlay)
        db.session.commit()
        print(f"Parlay {id} deleted.")