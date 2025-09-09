class SqlQuery:
    # Mock data for demo purposes
    albums = [
        {"name": "Presence", "artist": "Led Zeppelin"},
        {"name": "Roundabout", "artist": "Yes"},
        {"name": "Abbey Road", "artist": "The Beatles"}
    ]
    
    invoices = [
        {"id": 1, "amount": 150.00},
        {"id": 2, "amount": 200.50},
        {"id": 3, "amount": 99.99}
    ]
    
    @staticmethod
    def query_album(album_name):
        """Simple album lookup"""
        for album in SqlQuery.albums:
            if album["name"] == album_name:
                return album
        return None
    
    @staticmethod
    def join_albums():
        """Mock join operation"""
        return [{"album": album["name"], "artist": album["artist"]} for album in SqlQuery.albums]
    
    @staticmethod
    def top_invoices():
        """Get top invoices"""
        return sorted(SqlQuery.invoices, key=lambda x: x["amount"], reverse=True)
