from .. import load_tabby


def test_load_tabby(tabby_record_w_overrides):
    trwo = tabby_record_w_overrides
    loaded = load_tabby(
        trwo['input']['root'],
        single=True,
        jsonld=False,
    )
    assert loaded['single'] == trwo['target']['single']
    assert loaded['many'] == trwo['target']['many']
