import os
import json
from training import metadata_utils


def test_update_metadata_creates_and_updates(tmp_path):
    agent = tmp_path / 'agent'
    os.makedirs(agent, exist_ok=True)
    path = str(agent)
    metadata_utils.update_metadata(path, foo='bar')
    jsn = os.path.join(path, 'metadata.json')
    assert os.path.exists(jsn)
    data = json.loads(open(jsn).read())
    assert data['foo'] == 'bar'
    assert 'last_updated' in data


def test_log_promotion_adds_fields(tmp_path):
    agent = tmp_path / 'agent'
    os.makedirs(agent, exist_ok=True)
    metadata_utils.log_promotion(str(agent), 3, {'A':1})
    data = json.loads(open(os.path.join(str(agent), 'metadata.json')).read())
    assert data['iteration'] == 3
    assert 'promotion_time' in data
