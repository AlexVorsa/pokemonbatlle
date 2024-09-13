# pokemonbatlle
To do homework at the QA Studio school

``` bash
python -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

Add _--alluredir_ parameter to pytest settings.
For example:
```
{
    "python.testing.pytestArgs": [
        "tests",
        "--alluredir=my_allure_results"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}
```


<b>Attention!</b>
Edit _common/conf.py_ before running your tests.
