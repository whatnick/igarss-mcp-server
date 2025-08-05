from src.server import scrape_sessions

def test_scrape_sessions():
    keyword = "SAR"
    sessions = scrape_sessions(keyword)
    
    assert isinstance(sessions, list)
    assert len(sessions) > 0
    for session in sessions:
        assert 'title' in session
        assert 'time' in session