from api.oanda_api import OandaApi
from infrastructure.instrument_collection import instrumentCollection
from stream_example.streamer import run_streamer
from db.db import DataDB

def db_tests():
    d = DataDB()

    # d.add_one(DataDB.SAMPLE_COLL, dict(age=12, name='paddy', street='elm'))
    # data = [
    #     dict(age=12, name='fred', eyes='blue'),
    #     dict(age=34, name='simon', eyes='green'),
    #     dict(age=32, name='tigger', eyes='red'),
    #     dict(age=89, name='frodo', eyes='white'),
    #     dict(age=34, name='sam', eyes='black')
    # ]
    # d.add_many(DataDB.SAMPLE_COLL, data)

    # print(d.query_single(DataDB.SAMPLE_COLL, age=34))
    print(d.query_distinct(DataDB.SAMPLE_COLL, 'age'))


if __name__ == '__main__':
    api = OandaApi()
    # instrumentCollection.LoadInstruments("./data")
    instrumentCollection.LoadInstrumentsDB()
    print(instrumentCollection.instruments_dict)
    # instrumentCollection.CreateDB(api.get_account_instruments())
    # run_streamer()
    # d = DataDB()
    # d.test_connection()
    # db_tests()