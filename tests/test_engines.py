import os
from unittest.mock import patch

import betamax
import pytest
import requests
from flask import Flask

from rasp.base import DefaultEngine, Webpage
from rasp.tor_engine import TorEngine

with betamax.Betamax.configure() as config:
    current_dir = os.path.abspath(os.path.dirname(__file__))
    config.cassette_library_dir = os.path.join(current_dir, 'cassettes')

class TestDefaultEngine:
    @patch('rasp.base.DefaultEngine._session')
    def setUp(self, req_mock):
        session = requests.session()
        req_mock.return_value = session
        self.session = session
        self.engine = DefaultEngine()

    def test_default_pull_source_empty_url(self):
        with pytest.raises(ValueError):
            self.engine.get_page_source('')

    def test_default_pull_source_valid_url(self):
        with betamax.Betamax(self.session) as vcr:
            vcr.use_cassette('test_default_pull_source_valid_url')
            url = 'http://www.google.com'
            response = self.engine.get_page_source(url)
            assert isinstance(response, Webpage)
            assert isinstance(response.source, str)

    def test_curried_function(self):
        """
        Changes to the state of the Engine instance after currying shouldn't
        affect the parameters of the curried method
        """
        self.engine.headers.update({'Content-Type': 'text/json'})
        get_source = self.engine.curry()
        self.engine.headers.update({'Content-Type': 'text/xml'})
        page1 = get_source('http://127.0.0.1:5000/echo-headers/')
        content_type = [x for x in page1 if x[0] == 'Content-Type'][0]
        assert content_type == 'text/json'

    def test_default_pull_source_not_found(self):
        with betamax.Betamax(self.session) as vcr:
            vcr.use_cassette('test_default_pull_source_not_found')
            url = 'http://www.google.com'
            response = self.engine.get_page_source(url)
            assert response is None


class TestTorEngine:
    @patch('rasp.base.DefaultEngine._session')
    def setUp(self, req_mock):
        session = requests.session()
        req_mock.return_value = session
        self.session = session
        self.engine = TorEngine(control_password='raspdefaulttorpass')

    def test_tor_pull_source_valid_url(self):
        with betamax.Betamax(self.session) as vcr:
            vcr.use_cassette('test_tor_pull_source_valid_url')
            url = 'http://www.google.com'
            response = self.engine.get_page_source(url)
            assert isinstance(response, Webpage)
            assert isinstance(response.source, str)
