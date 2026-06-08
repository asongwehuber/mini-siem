from app.main import create_app
from app.extensions import db  

app = create_app()



print("\n===== ROUTES =====")
print(app.url_map)
print("==================\n")

#with app.app_context():
  #  db.create_all()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)