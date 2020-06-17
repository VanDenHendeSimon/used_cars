from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form.to_dict()

        return data

    @staticmethod
    def get_listings():
        sql = "SELECT * FROM listing;"
        return Database.get_rows(sql)

    @staticmethod
    def get_listing(_id):
        sql = "SELECT * FROM listing WHERE Id = %s;"
        return Database.get_rows(sql, [_id])

    @staticmethod
    def create_listing(
            _id, titel, beschrijving, stad, prijs, km_stand, bouwjaar, carpass_url, details_url, image_url, transmissie,
            adverteerder, brandstof, merk, model, euronorm, motor_inhoud, carrosserie
    ):

        sql = "INSERT INTO listing VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        params = [
            _id, titel, beschrijving, stad, prijs, km_stand, bouwjaar, carpass_url, details_url, image_url, transmissie,
            adverteerder, brandstof, merk, model, euronorm, motor_inhoud, carrosserie
        ]

        return Database.execute_sql(sql, params)
