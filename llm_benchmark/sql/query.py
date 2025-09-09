class SqlQuery:
    """Mock SQL query implementations"""
    
    @staticmethod
    def query_album(album_name):
        """Mock album query"""
        mock_data = {
            'Presence': 'Led Zeppelin - 1976',
            'Roundabout': 'Yes - Fragile (1971)'
        }
        return mock_data.get(album_name, 'Album not found')
    
    @staticmethod
    def join_albums():
        """Mock album join query"""
        return [('Led Zeppelin', 'Presence', 1976), ('Yes', 'Fragile', 1971)]
    
    @staticmethod
    def top_invoices():
        """Mock top invoices query"""
        return [('Invoice 1', 100.50), ('Invoice 2', 95.25), ('Invoice 3', 89.75)]
